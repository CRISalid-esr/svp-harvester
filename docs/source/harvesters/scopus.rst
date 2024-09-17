Harvesters : Scopus
=====================================

.. note:: The Scopus Harvester requires the following:

    - A valid Scopus API key
    - A valid Scopus institution token

    Add these to the environment variables SCOPUS_API_KEY and SCOPUS_INST_TOKEN

Data source
-----------

SoVisu+ Scopus Harvester fetches data from the `Scopus API <"https://api.elsevier.com/content/search/scopus">`_.

Supported identifiers
---------------------

The following identifiers are handled by the harvester:

- scopus_eid

Data conversion
---------------

Scopus document types are mapped to RDF classes following the table provided in `CRISalid data model documentation <https://www.esup-portail.org/wiki/pages/viewpage.action?pageId=1378320388>`_.
