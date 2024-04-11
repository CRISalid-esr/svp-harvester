##########
Kubernetes
##########

Kubernetes deployment files are located in the :code:`deploy/k8s` directory.

Example of Minikube deployment:

1. Copy all *.yaml.dist files in the :code:`deploy/k8s` directory to *.yaml files and replace all environment variables by their base64 encoded values.

.. code-block:: bash

    echo -n "my-password" | base64

2. Copy postgresql sql.dist initialization script to SQL file and replace all credentials by their values.
Push the sql file to the Minikube VM.

.. code-block:: bash

    minikube cp svph-user-db.sql /home/docker/svph-user-db.sql

3. Start the deployment

.. code-block:: bash

    kubectl apply -f deploy/k8s