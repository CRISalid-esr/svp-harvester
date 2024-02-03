Harvesters : ScanR
=====================================

Data source
-----------

SoVisu+ ScanR Harvester fetches data from the latest ScanR API.

.. note:: The ScanR Harvester requires identifiers and credentials from the ScanR API, currently under development and not yet released to the public.
    Obtain these by contacting the ScanR team.
    They should be integrated into the harvester's environment variables.
    The harvester will be updated once the new API is released to the public.

Supported identifiers
---------------------

The following identifiers are handled by the harvester:

- idref
- orcid
- idHal_s

.. note:: When `idref` is unavailable, the harvester uses `orcid` or `idHal_s` to gather the entity's data.
    It then derives the `scanr_id` from the `idref`, enabling the retrieval of the entity's publications from the ScanR API.


Data conversion
---------------

ScanR document types and authors qualities are mapped to RDF classes following the table provided in `CRISalid data model documentation <https://www.esup-portail.org/wiki/pages/viewpage.action?pageId=1352335371#GECMod%C3%A9lisation-MappingScanr-SoVisu+>`_.