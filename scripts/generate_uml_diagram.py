# may require `apt install graphviz` on linux terminals
from app.db.session import Base
from app.db.models import (
    abstract,
    affiliations,
    concept,
    contribution,
    contributor,
    document_type,
    entity,
    harvesting,
    identifier,
    label,
    reference_literal_field,
    organization,
    person,
    reference,
    reference_event,
    references_document_type,
    references_subject,
    retrieval,
    subtitle,
    title,
    versioned_record,
)
from sqlalchemy_schemadisplay import create_uml_graph

graph = create_uml_graph(
    Base.registry.mappers,
    show_operations=False,
    show_multiplicity_one=True,
)
graph.write_png("../img/sql_alchemy_entities.png")
