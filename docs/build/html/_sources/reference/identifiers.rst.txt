Reference : identifiers
-----------------------
.. warning::
    In this application, an entity (person or structure) is considered as a **list of identifiers**.
    This list of identifiers is provided by the user, and it is important to note,
    that the application is not able to align the identifiers of the entity with the ones provided by the user.
    The application is also unable to complete the missing identifiers.



People identifiers
==================
.. note::
    list of supported identifiers
    an entity is considered as a list of identifiers
    The user is responsible for providing the list of identifiers
    The application support those identifiers:


The following identifiers are currently supported for people entities:

- **idHal_s**: Works with the **Hal** and **ScanR** harvesters. This identifier is a string composed of the first and last name.
- **idHal_i**: Works only with the **Hal** harvester. This identifier is an integer, and each one is unique.
- **ORCID**: Works with the **Hal**, **IdRef**, **ScanR**, and **OpenAlex** harvesters. The ORCID is a 16-digit identifier formatted as `0000-0000-0000-000X`, where the last digit is a checksum (which can be a number or the letter 'X').
- **IdRef**: Works with the **IdRef** and **ScanR** harvesters. This identifier is a unique, 9-digit number.
- **Scopus EID**: Works only with the **Scopus** harvester. This identifier is unique to Scopus, and each researcher has their own Scopus ID.


Structures identifiers
=======================


.. note::

   At present, the application does not support handling **Structure entities**. However, this feature will be added in a future update. This section will be updated as soon as the feature is added.
