Harvesters : Hal
----------------

Data source
-----------

SoVisu+ Hal Harvester fetches data from the `Hal API <https://api.archives-ouvertes.fr/docs/search>`_.

Supported identifiers
---------------------

The following identifiers are handled by the harvester:

- idHal_i
- idHal_s
- ORCID

.. note:: For SoVisu+ Hal Harvester, Hal identifiers have priority over ORCID. In case where both idHal_i and idHal_s are provided, idHal_i is used. SoVisu+ Hal Harvester will not check the alignment between idHal_i and idHal_s, as the client is supposed to provide consistent data.

Data conversion
---------------

Hal document types are mapped to RDF classes following the table provided in `CRISalid data model documentation <https://www.esup-portail.org/wiki/pages/viewpage.action?pageId=1352335371#GECMod%C3%A9lisation-MappingHAL-SoVisu+>`_.

Hal authors qualities are mapped to LoC roles following the table provided in `CRISalid data model documentation <https://www.esup-portail.org/wiki/pages/viewpage.action?pageId=1352335371#GECMod%C3%A9lisation-Typologiedesr%C3%B4les>`_.

