# svp-harvester

Sovisu+ publications harvester as microservice

:warning: This project is still in development and is not yet ready for production.

## Overview

### Goals

The SoVisu+ Harvester project is intended to provide a unified interface to the various scholarly publication databases
and repositories
that are used by an institutional research information system in general and the SoVisu+ project in particular.

SoVisu+ Harvester is implemented as a microservice that can be deployed in a containerized environment.

It is intended to institutions that have already created and actively maintain a repository of matched identifiers for
actors, structures and research projects.

### Overall use

The SoVisu+ Harvester is designed to receive requests containing a list of identifiers for a so-called "research
entity" (actor, structure or research project) and to return a list of references to publications
that are associated with the research entity.

The list of accepted identifiers is not exhaustive as the service is extensible by design.

- Idref
- Idhal
- ORCID
- ResearcherID
- ...

The references are obtained through a set of modular harvesters that are designed to query various scholarly publication
databases and repositories :

- Data.idref.fr
- Hal
- Scanr
- Web of Science
- OpenAlex
- ...
  The harvesters are launched in parallel and their results are returned on the fly to the client, allowing for a fast
  response
  time and an asynchronous display of the results.

![svp-harvester overall behavior](img/svp-harvester-overall-behavior.png?raw=true "Overall behavior")

Requests and results are registered in the database for monitoring purposes. The harvesting history may be consulted
through the web interface.

### Input

The research entities may be submitted to the harvester in 4 ways :

- Manually, through the web interface
- By querying the REST API asynchronoulsy
- By querying the REST API synchronoulsy
- Through AMQP messages delivered through a message broker (such as RabbitMQ)

### Output

The structure of the JSON output complies with
the [SciencePlus publications model](https://documentation.abes.fr/aidescienceplusabes/index.html#ModeleDonnees).

Please note that references deduplication is out of scope of SoVisu+ Harvester and should be handled by another SoVisu+
component.

## Technical overview

### Used technologies

Server side :

- Python 3.10 with asyncio
- FastAPI with Pydantic
- PostgreSQL with asyncpg and alembic
- RabbitMQ (through aio-pika)
- Poetry
- Pytest
- Black

Client side (admin interface) :

- Npm
- Webpack
- Bootstrap
- Jest

## Development ressources (installation outside of a containerized environment)

### Database configuration

#### Database creation

As postgres user :

```sql
CREATE
DATABASE your_db_name;
CREATE
USER your_user_name WITH PASSWORD 'your_secret';
GRANT ALL PRIVILEGES ON DATABASE
your_db_name to your_user_name;
```

Repeat for test database.

Update .env and .test.env with credentials

```bash
DB_USER="your_user_name"
DB_NAME="your_db_name"
DB_PASSWORD="your_secret"
```

#### Database migration

The project uses [alembic](https://alembic.sqlalchemy.org/en/latest/) for schema versioning and migration.

```bash
APP_ENV=DEV alembic revision --autogenerate -m "Explain what you did to the model"
APP_ENV=DEV alembic upgrade head
``` 

### Dependencies installation

The project uses [poetry](https://python-poetry.org/) for dependency management.

```bash
poetry install
```

### Tests

The project uses [pytest](https://docs.pytest.org/en/stable/) for testing.

From project root :

```bash
APP_ENV=TEST pytest
```

or with coverage

```bash
APP_ENV=TEST coverage run --source=app -m pytest
coverage report --show-missing
```

### Assets compilation

The project uses [webpack](https://webpack.js.org/) for assets compilation.

From app/templates :

- Dependencies installation

```bash
npm install
```

- Assets compilation

```bash

npm run build

```

or

```bash
npm run build
```

### Launch

From project root :

```bash
APP_ENV=DEV uvicorn app.main:app --reload
```

or

```bash
APP_ENV=DEV python3 app/main.py 
```