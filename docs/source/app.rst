App Management
~~~~~~~~~~~~~~

How to Create an App
====================

To create your app, run the following command. It will also set up a git remote. This must be run from within a git repository folder. An app name will be generated for you, but you can also optionally supply an app name if you wish using :bash:`gigalixir create -n $APP_NAME`. There is currently no way to change your app name once it is created. If you like, you can also choose which cloud provider and region using the :bash:`--cloud` and :bash:`--region` options. We currently support :bash:`gcp` in :bash:`v2018-us-central1` or :bash:`europe-west1` and :bash:`aws` in :bash:`us-east-1` or :bash:`us-west-2`. The default is v2018-us-central1 on gcp.

.. code-block:: bash

    gigalixir create

.. _`choose an app name`:

How to choose a name for your app
=================================

Normally, gigalixir generates a unique name for you automatically, but if you want, you can specify your app name. You'll need to :ref:`install the CLI` and run something like this

.. code-block:: bash

    gigalixir create -n $APP_NAME

That should do it. Once you deploy, you'll be able to access your app from :bash:`https://$APP_NAME.gigalixirapp.com`.

.. _`delete-app`:

How to Delete an App
====================

To delete an app, run

.. code-block:: bash

    gigalixir apps:destroy

How to Rename an App
====================

There is no way to rename an app, but you can delete it and then create a new one. Remember to migrate over your configs.

.. _`scale`:
.. _`scaling`:

How to Scale an App
===================

You can scale your app by adding more memory and cpu to each container, also called a replica. You can also scale by adding more replicas. Both are handled by the following command. For more information, see :ref:`replica sizing`.

.. code-block:: bash

    gigalixir ps:scale --replicas=2 --size=0.6

.. _app-status:

How to Check App Status
=======================

To see how many replicas are actually running in production compared to how many are desired, run

.. code-block:: bash

    gigalixir ps

How do I manage multiple apps?
==============================

All relevant CLI commands can take an optional :bash:`--app_name` flag to specify which app you want to run the command on. Or, if you prefer, you can use the :bash:`GIGALIXIR_APP` environment variable instead. Without the app name, Gigalixir tries to auto-detect the app name based on your git remotes which works fine when you only have one app.

How to List Apps
================

To see what apps you own and information about them, run the following command. This will only show you
your desired app configuration. To see the actual status of your app, see :ref:`app-status`.

.. code-block:: bash

    gigalixir apps

How to List Releases
====================

Each time you deploy or rollback a new release is generated. To see all your previous releases, run

.. code-block:: bash

    gigalixir releases

How to View App Activity
========================

We keep a record of each time you deploy, change configs, scale, etc. To view the activity history, run

.. code-block:: bash

    gigalixir apps:activity


.. _`restart`:

How to Restart an App
=====================

.. code-block:: bash

    gigalixir ps:restart

For hot upgrades, See :ref:`hot-upgrade`. We are working on adding custom health checks.

Restarts should be zero-downtime. See :ref:`zero-downtime`.
