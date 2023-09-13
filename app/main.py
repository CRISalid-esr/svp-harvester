""" Main application and routing logic for API """

import uvicorn

from app.svp_harvester import SvpHarvester

app = SvpHarvester()

if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="0.0.0.0", port=8000)
