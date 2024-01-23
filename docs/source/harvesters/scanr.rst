Harvesters : ScanR
=====================================

Data source
-----------

SoVisu+ ScanR Harvester fetches data from the latest ScanR API.

.. note:: To operate the ScanR Harvester, identifiers and credentials from the non-public ScanR API are needed. These can be procured by reaching out to the ScanR team and should be integrated into the harvester's environment variables. The harvester will be updated to use the public ScanR API as soon as it is available.

Supported identifiers
---------------------

The following identifiers are handled by the harvester:

- idref

.. note:: Due to the current data model, the harvester only accepts idref identifiers.
    However, it is planned to support ORCID and idHal_s in the future.


Data conversion
---------------

ScanR document types and authors qualities are mapped to RDF classes following the table provided in `CRISalid data model documentation <https://www.esup-portail.org/wiki/pages/viewpage.action?pageId=1352335371#GECMod%C3%A9lisation-MappingScanr-SoVisu+>`_.