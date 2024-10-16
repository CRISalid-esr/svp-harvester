Docker image Deployment
===========================================================

At the time of writing, svp-harvester docker image should only be rebuilt if you want to
modify the translation files, adapt some hard-coded parameters in javascript environment variables
or in order to customize the look and feel.
If you just want to deploy the application, you can use the pre-build docker image from docker hub and skip the following 2-4 steps.

1. Clone the repository

..  code-block:: bash

    git clone https://github.com/CRISalid-esr/svp-harvester.git


2. Customize js environment variables

Javascript environment variables are located in the following file: :code:`app/templates/src/js/env.js`.

The API path parameters are commented out by default. If you leave them as is, the GUI will receive this information
from the back end environment variables (API_HOST, API_PATH and API_VERSION). If for any reason you want to hard-code
these parameters client side, you can uncomment them and set them to the desired values.

.. code-block:: javascript

    // apiHost: "http://localhost",
    // apiPath: "/api/v1",

The remaining parameters are related to the list of identifiers types that are available from the collection test form.

3. Build the static files

Install the required build environment if needed

.. code-block:: bash

    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
    source ~/.bashrc
    nvm install v18.12.1
    nvm use 18.12.1

Move to the js directory and build the static files

.. code-block:: bash

    cd app/templates/src/js/
    npm install
    npm run build

4. Build the docker image

If you don't want to use docker compose, you can build the docker image manually
e.g. to push it to a private registry. Else, you can skip this step as the image
will be built automatically by docker compose.

From repository root directory:

.. code-block:: bash

    docker build -t svp-harvester .
