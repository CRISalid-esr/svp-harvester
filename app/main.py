""" Main application and routing logic for API """

import uvicorn

from app.logging.logging_middleware import log_middleware
from app.svp_harvester import SvpHarvester

app = SvpHarvester()

app.middleware("http")(log_middleware)

if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="0.0.0.0", port=8000)
