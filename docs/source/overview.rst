Overview
========

SoVisu+ Harvester is a generic tool design to harvest bibliographic references from various sources
and to convert them into a common standardized format. The tool is designed to allow easy
extension in order to accommodate new data sources.

Key Features:
-------------

- **Flexible Configuration:** SoVisu+ Harvester serves as a runner for a group of harvesters, each of which is defined with
specific parameters in a configuration file.
These harvesters are responsible for retrieving data from distinct sources and converting it into a uniform format.

- **Parallel Processing:** To optimize performance, the harvesters are run concurrently. The results can be delivered
in real-time or as a single batch upon completion of the process, with options for both synchronous and asynchronous modes.

- **Standardized Data Format:** The harvested data is converted into a common format, aligning with the `SciencePlus data model <https://documentation.abes.fr/aidescienceplusabes/index.html#ModeleGeneral>`_.
This model is based on widely accepted ontologies in the field, such as Dublin Core, Bibo, Vivo, and more.
