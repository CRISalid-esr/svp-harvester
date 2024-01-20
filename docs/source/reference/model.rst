=================
Reference : model
=================

One of SoVisu+ Harvester's main tasks is to convert the various formats originating from the source platforms into a common data model compatible with the Semantic Web standards.

Reference model
----------------

The target model used to represent scientific output in SoVisu+ is inspired
by the `ABES Science Plus model <https://documentation.abes.fr/aidescienceplusabes/index.html#ModeleGeneral>`_.

For more information about modeling choices and mapping with source formats,
please refer to the `Modeling working group reports <https://www.esup-portail.org/wiki/pages/viewpage.action?pageId=1352335371>`_.
Database Model
--------------

Here is an UML-like schema generated from the SQLAlchemy models.

.. image:: https://raw.githubusercontent.com/CRISalid-esr/svp-harvester/dev-main/img/sql_alchemy_entities.png
  :width: 1000
  :alt: **SoVisu+ Harvester** UML model


