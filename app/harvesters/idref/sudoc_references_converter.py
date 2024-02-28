import rdflib
from rdflib import DC, Literal

from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.idref.abes_rdf_references_converter import (
    AbesRDFReferencesConverter,
)
from app.harvesters.idref.sudoc_document_type_converter import (
    SudocDocumentTypeConverter,
)
from app.harvesters.idref.sudoc_qualities_converter import SudocQualitiesConverter
from app.utilities.string_utilities import remove_after_separator


class SudocReferencesConverter(AbesRDFReferencesConverter):
    """
    Converts raw data from Sudoc to a normalised Reference object
    """

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DC.title):
            yield Title(
                value=remove_after_separator(title.value, "/"), language=title.language
            )

    async def _document_type(self, pub_graph, uri):
        for document_type in pub_graph.objects(rdflib.term.URIRef(uri), DC.type):
            uri, label = SudocDocumentTypeConverter().convert(str(document_type))
            yield await self._get_or_create_document_type_by_uri(uri, label)

    async def _add_contributions(self, pub_graph, uri):
        contribution_informations = []
        query = """
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX marcrel: <http://id.loc.gov/vocabulary/relators/>

                    SELECT DISTINCT ?role ?person ?name
                    WHERE {
                        ?work ?role ?person .
                        ?person a foaf:Person .
                        ?person foaf:name ?name .
                        FILTER(STRSTARTS(STR(?role), STR(marcrel:)))
                    }
                """

        results = pub_graph.query(query)
        for role, identifier, name in results:
            role = role.split("/")[-1]
            contribution_informations.append(
                AbstractReferencesConverter.ContributionInformations(
                    role=SudocQualitiesConverter.convert(role),
                    identifier=str(identifier),
                    name=str(name),
                    rank=None,
                )
            )

        async for contribution in self._contributions(
            contribution_informations=contribution_informations, source="sudoc"
        ):
            yield contribution
