Harvesters: Overview
=====================================

Harvesters constitute a modular system of components, each designed to retrieve data from diverse sources and convert it into a standardized format based on the `SciencePlus data model <https://documentation.abes.fr/aidescienceplusabes/index.html#ModeleGeneral>`_.
The system is designed to be extensible, allowing for the addition of new harvesters as needed.

Each harvester comprises two key components:

1. **Data Fetcher or Client:** This component is responsible for retrieving data from a specified source, such as a JSON API, SRU endpoint, SPARQL endpoint, etc.

2. **Converter:** This component is tasked with converting the data into the target format.

The list of active harvesters is defined in a configuration file (`harvesters.yml`), which is loaded during the system startup. Each harvester is associated with a factory class that inherits from `AbstractHarvesterFactory`, which is responsible for creating the harvester's data fetcher and converter components.

All harvesters are built on the asyncio framework to enable the parallel execution of multiple harvesters, which is essential for the system's performance.

Triggering of harvesters
------------------------

When an entity's identifiers are received, each harvester self-decides whether it is relevant for the provided identifiers. If so, it is triggered to retrieve the entity's data.

But an harvester may be disabled :

- globally, through the `harvesters.yml` configuration file
- on a per-request basis, through the `harvesters` parameter of the `references` endpoint




