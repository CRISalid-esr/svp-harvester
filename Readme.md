# SoVisu+ Harvester

Microservice intended to be used as a part of the SoVisu+ project. It is responsible for harvesting publications and
other scholarly works from various sources (Hal, data.idref.fr, Scanr, Wos, ...).

## Deployment

### Outside docker

Install dependencies:

```bash
pip install -r requirements.txt
```

Customize environment variables :
- either by renaming .env.example to .env and filling it
- either by providing the same variables through environment variables

Run the tests:

```bash
pytest
```

Run the service:

```bash
uvicorn app.main:app --reload --env-file .env
```



