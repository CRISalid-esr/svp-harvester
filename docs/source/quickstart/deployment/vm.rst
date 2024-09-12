VM Deployment
===========================================================

This guide will walk you through setting up the SVP Harvester project on a fresh Ubuntu 22.04 installation.

1. Install RabbitMQ
----------------------

To install RabbitMQ on your system, please follow the steps outlined in the `official RabbitMQ documentation <https://www.rabbitmq.com/docs/install-debian>`_.

Once RabbitMQ is installed, enable the management interface by executing the following commands:

.. code-block:: bash

    # Enable the management interface
    sudo rabbitmq-plugins enable rabbitmq_management

    # Restart RabbitMQ
    sudo systemctl restart rabbitmq-server

After completing these steps, access the management interface through your web browser by navigating to `localhost:15672`. You can log in using the default credentials: ``guest:guest``.


2. Install PostgreSQL
----------------------

Follow the steps outlined on `PostgreSQL's official documentation <https://www.postgresql.org/download/linux/ubuntu/>`_:

.. code-block:: bash

   # Add PostgreSQL repository
   sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
   wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
   sudo apt-get update

   # Install PostgreSQL
   sudo apt-get -y install postgresql-16

   # Create PostgreSQL database and user
   sudo -u postgres psql

In the PostgreSQL shell:

.. code-block:: sql

   CREATE DATABASE svph;
   CREATE USER svph_user WITH PASSWORD 'svph_word';
   GRANT ALL PRIVILEGES ON DATABASE svph TO svph_user;
   ALTER DATABASE svph OWNER TO svph_user;

Create a ``.env`` file from ``.env.example``:

.. code-block:: bash

   cp .env.example .env

Edit ``.env`` to add database credentials:

.. code-block:: bash

   gedit .env

Replace ``DB_NAME``, ``DB_USER``, ``DB_PASSWORD`` values with the ones you set previously.

3. Install Redis
-----------------

Refer to the `Redis documentation <https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/>`_ for installation instructions:

.. code-block:: bash

   curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

   echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

   sudo apt-get update
   sudo apt-get install redis

4. Install SVP Harvester
--------------------------

.. note::
   Before proceeding with the installation, please ensure that Git and Python are installed on your system. If not, you will need to install them before following the installation instructions provided below.

   To check if Git is installed, run the following command in your terminal:

   .. code-block:: bash

      git --version

   If Git is not installed, you can install it by running:

   .. code-block:: bash

      sudo apt update
      sudo apt install git-all

   To check if Python is installed, run the following command in your terminal:

   .. code-block:: bash

      python3 --version

   If Python is not installed, you can install it by running:

   .. code-block:: bash

      sudo apt update
      sudo apt install software-properties-common -y
      sudo add-apt-repository ppa:deadsnakes/ppa
      sudo apt update
      sudo apt install python3.10 python3.10-venv python3.10-dev
      sudo rm /usr/bin/python3
      sudo ln -s python3.10 /usr/bin/python3
      python3 --version

Clone the repository and set up the project:



.. code-block:: bash

   # Clone the repository
   git clone https://github.com/CRISalid-esr/svp-harvester.git

   # Install nvm and npm
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
   nvm install v18.12.1
   nvm use 18.12.1

   # Install JavaScript dependencies
   cd svp-harvester/app/templates/src/js/
   npm install
   npm run build

   # Return to the project root
   cd ../../../../

   # Set up Python virtual environment
   python3 -m venv svp_venv
   source svp_venv/bin/activate

   # Install Python requirements
   pip install -r requirements.txt

   # Set up database tables
   APP_ENV=DEV alembic upgrade head

   # Run the project
   APP_ENV=DEV uvicorn app.main:app

To deactivate the virtual environment, use:

.. code-block:: bash

   deactivate
