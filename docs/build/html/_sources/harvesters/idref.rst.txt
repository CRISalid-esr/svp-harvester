Harvesters : Idref
=====================================

Data source
-----------

SoVisu+ idref Harvester fetches data from the `Idref SPARQL Endpoint <https://data.idref.fr/sparql>`_.

Supported identifiers
---------------------

The following identifiers are handled by the harvester:

- idref
- ORCID

Data conversion
---------------
Idref document types are mapped to RDF classes, and authors qualities are mapped to LoC roles following the tables provided in `CRISalid data model documentation <https://www.esup-portail.org/wiki/pages/viewpage.action?pageId=1452441617>`_.

Sub-Harvesters
---------------

Idref Harvester provides multiple sub-harvesters to gather additional data in case where the data provided by the main harvester is not enough.

The currently available sub-harvesters are:

* OpenEdition Harvester, who gather data from the `OpenEdition API <http://oai.openedition.org/?verb=ListRecords&metadataPrefix=oai_dc>`_
* Persee Harvester, who fetches data from the Persee RDF endpoint
* SciencePlus Harvester who fetches data from the SciencePlus RDF endpoint
* SUDOC Harvester who fetches data from the SUDOC RDF endpoint
