################
Docker compose
################

If you want to deploy the application using docker compose, you can use the provided docker-compose.yml file.
This file will deploy the following containers:
- postgresql database
- rabbitmq message broker
- svp-harvester application (API + interactive documentation + GUI)

Rename :code:`docker-compose.yml.dist` to :code:`docker-compose.yml` and adapt all environment variables to your needs.

If you need to build the docker image manually (see above steps 2-4), you will need to modify the docker-compose.yml file :

- replace the image name by the one you built
- or uncomment the build section and comment out the image section
  svphweb:
    #image: crisalidesr/svp-harvester:latest
    build:
      context: .
      dockerfile: Dockerfile

5. Start the containers

Run the following command from the directory containing the docker-compose.yml file:

.. code-block:: bash

    docker-compose up -d
