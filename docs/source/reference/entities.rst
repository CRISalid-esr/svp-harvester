Reference : entity resolution
=============================

Entities and alignement in SoVisu+ Harvester
-------------------------------------------

In SoVisu+ Harvester, harvesting activities are always conducted on behalf of an **entity** equipped with unique **identifiers**.
An **entity** can be an individual, a project, a research structure, or an institution—essentially, any unit to which publications can be attributed.
Currently, the system primarily supports entities of the "person" type, focusing on researchers.
The concept of **identifier alignment** refers to the process whereby an entity is associated with multiple identifiers.
These identifiers are presumed to represent the same entity, ensuring that the harvesting activities are conducted consistently across the various sources.

.. note::

   SoVisu+ Harvester does not perform any kind of entity alignment by itself. It is up to the client system to provide correct identifiers for each submitted entity. Nevertheless, SoVisu+ Harvester memorizes the submitted entities and their identifiers (unless instructed otherwise) and will use the same alignment for subsequent harvestings of the same entity.

In the case where the client system submits an entity with changed identifiers, SoVisu+ Harvester will do its best to update the entity alignment in respect to the new provided identifiers.

.. warning::

   However, sending entities with shifting and contradictory alignments to SoVisu+ Harvester can put the system into an inconsistent state and make the harvesting history illegible, as past harvesting are not retroactively corrected when the alignments are updated.


Identifiers safe mode
---------------------

This whole behavior can be canceled by setting the `identifiers_safe_mode` parameter to `true` in the request body. In this case, the SoVisu+ Harvester will not register submitted identifiers nor update existing entities.
This mode is activated by default in the graphical user interface to prevent accidental perturbation of the entity alignments by manually submitted entities.

Recommendations
---------------

It is recommended to always submit the same entity with the same identifiers. This will ensure the legibility of the harvesting history and the coherency of the results.
Adding new identifiers to existing entities is the expected behavior of the client system. SoVisu+ harvester will handle this seamlessly and will update its alignment accordingly.
Correcting alignment errors is also a common operation. SoVisu+ Harvester expects it to occur occasionally and will do its best to   its inner entity registry.
This includes merging entities that were previously considered as distinct or removing an identifier from an entity to attach it to another one.

Identifier conflicts
--------------------

An identifier conflict occurs when the alignement of a newly submitted entity is logically incompatible with the previously submitted ones.

For example, Researcher 1 is submitted with ORCID identifier A and IdRef identifier B :

.. code-block:: text

    Researcher 1
    |
    +-- ORCID Identifier: A
    |
    +-- IdRef Identifier: B
    |
    v

    Researcher 2
    |
    +-- ORCID Identifier: A  <- Shared ORCID Identifier with Researcher 1
    |
    +-- IdRef Identifier: C

ORCID A cannot belong to both entities identified respectively by IdRef B and IdRef C. This is an identifier conflict.
SoVisu+ Harvester will use the `identifiers.yml` configuration file to resolve this conflict (see :doc:`Identifiers section<identifiers>` ).

Examples
--------

Example 1: submitting a new entity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


..  code-block:: bash

    curl -X 'POST' \
      'http://my-service-url/api/v1/references/retrieval' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "person": {
        "identifiers": [
          {
            "type": "idref",
            "value": "111111111"
          },
          {
            "type": "orcid",
            "value": "0000-0001-1111-1112"
          }
        ],
        "name": "Smith, P"
      },
      "identifiers_safe_mode": false,
      "harvesters": [
        "hal",
        "idref",
        "scanr",
        "openalex"
      ],
      "events": [
        "created", "updated", "deleted", "unchanged"
      ]
    }'

During the execution of this request, the SoVisu+ Harvester will:

- register a new entity with the name "Smith, P" and the identifiers ``111111111`` and ``0000-0001-1111-1112``


**Smith, P**

.. list-table::
   :stub-columns: 1

   * - **IdRef**
     - 111111111
   * - **ORCID**
     - 0000-0001-1111-1112


- submit the entity to the harvesters "hal", "idref", "scanr" and "openalex"

- return an URL where status and results of the harvesting can be fetched asynchronously

When a request is submitted to the **SoVisu+ Harvester** using either the *IdRef identifier* “``111111111``” or the *ORCID identifier* ``0000-0001-1111-1112``, the system recognizes and aligns with the previously established entity without creating a new one.
After an entity has been initially aligned with specific identifiers, subsequent retrievals require **only one of the identifiers**, not all, to trigger the retrieval process with all the associated identifiers.


Example 2: change in identifiers alignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following the previous example, let's say that the client system wants to update the ORCID identifier of the entity identified by ``111111111``.

..  code-block:: bash

    curl -X 'POST' \
      'http://my-service-url/api/v1/references/retrieval' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "person": {
        "identifiers": [
          {
            "type": "idref",
            "value": "111111111"
          },
          {
            "type": "orcid",
            "value": "0000-0001-1111-1113"
          }
        ],
        "name": "Smith, P"
      },
      "identifiers_safe_mode": false,
      "harvesters": [
        "hal",
        "idref",
        "scanr",
        "openalex"
      ],
      "events": [
        "created", "updated", "deleted", "unchanged"
      ]
    }'

During the execution of this request, the SoVisu+ Harvester will:

- update the entity identified by ``111111111`` with the new ORCID identifier ``0000-0001-1111-1113``

**Smith, P**

.. list-table::
   :stub-columns: 1

   * - **IdRef**
     - 111111111
   * - **ORCID**
     - 0000-0001-1111-1113


- submit the entity to the harvesters "hal", "idref", "scanr" and "openalex"

- return an URL where status and results of the harvesting can be fetched asynchronously

If a subsequent request is made with idref identifier ``111111111`` **and** another orcid identifier, the SoVisu+ Harvester will update the entity identified by ``111111111``
with the new ORCID identifier and will submit the entity to the harvesters.

Example 3 : identifiers safe mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following the example 1, imagine that the client system wants to submit an entity with the same IdRef identifier but a different ORCID identifier.
But this time, the parameter `identifiers_safe_mode` is set to `true`.

..  code-block:: bash

    curl -X 'POST' \
      'http://my-service-url/api/v1/references/retrieval' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "person": {
        "identifiers": [
          {
            "type": "idref",
            "value": "111111111"
          },
          {
            "type": "orcid",
            "value": "0000-0001-1111-1114"
          }
        ],
        "name": "Smith, P"
      },
      "identifiers_safe_mode": true,
      "harvesters": [
        "hal",
        "idref",
        "scanr",
        "openalex"
      ],
      "events": [
        "created", "updated", "deleted", "unchanged"
      ]
    }'

During the execution of this request, the SoVisu+ Harvester will:
- retrieve the previously submitted entity identified by ``111111111`` (as a superior priority is given to the IdRef identifier, see :doc:`Identifiers section<identifiers>`.)

**Smith, P**

.. list-table::
   :stub-columns: 1

   * - **IdRef**
     - 111111111
   * - **ORCID**
     - 0000-0001-1111-1112

As the `identifiers_safe_mode` parameter is set to `true`, the entity will not be updated and the newly submitted ORCID will be ignored.

- submit the entity with the same identifiers as in Example 1 to the harvesters "hal", "idref", "scanr" and "openalex"

Example 4 : identifier conflict
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This time, the new requests contains an identifier conflict. A new entity is submitted with the same ORCID identifier as an existing entity but a different IdRef identifier.

..  code-block:: bash

    curl -X 'POST' \
      'http://my-service-url/api/v1/references/retrieval' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "person": {
        "identifiers": [
          {
            "type": "idref",
            "value": "222222222"
          },
          {
            "type": "orcid",
            "value": "0000-0001-1111-1112"
          }
        ],
        "name": "Dupont, G"
      },
      "identifiers_safe_mode": false,
      "harvesters": [
        "hal",
        "idref",
        "scanr",
        "openalex"
      ],
      "events": [
        "created", "updated", "deleted", "unchanged"
      ]
    }'

As the parameter `identifiers_safe_mode` is set to `false`, the SoVisu+ Harvester will:

- register a new entity with the name "Dupont, G" and the identifiers ``222222222`` and ``0000-0001-1111-1112``

**Dupont, G**

.. list-table::
   :stub-columns: 1

   * - **IdRef**
     - 222222222
   * - **ORCID**
     - 0000-0001-1111-1112

- remove the ORCID identifier ``0000-0001-1111-1112`` from the entity identified by ``111111111``

**Smith, P**

.. list-table::
   :stub-columns: 1

   * - **IdRef**
     - 111111111

- submit the entity to the harvesters "hal", "idref", "scanr" and "openalex"



