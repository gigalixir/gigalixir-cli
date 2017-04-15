.. GIGALIXIR documentation master file, created by
   sphinx-quickstart on Fri Apr 14 16:43:23 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=====================================
GIGALIXIR Documentation
=====================================

GIGALIXIR is a platform-as-a-service designed just for Elixir and Phoenix.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

Quick Start
===========

Prequisites
-----------

.. role:: bash(code)
    :language: bash

You should make sure you have :bash:`pip` installed. For help, take a look at the `pip documentation`_.

Install the Command-Line Interface
---------------------

Next install, the command-line interface. GIGALIXIR currently does not have a web interface. We want the command-line to be a first-class citizen so that you can build scripts and tools easily.

.. code-block:: bash

    pip install gigalixir

Create an Account
-----------------

Create an account using the following command. It will prompt you for your email address and password. You will have to confirm your email before continuing. It will also prompt you for credit card information. GIGALIXIR currently does not offer a free trial, but we do offer a `money back guarantee`_. Please don't hesitate to use it.

.. code-block:: bash

    gigalixir create user

Log In
------

Next, log in. This will grant you an api key which expires in 365 days. It will also optionally modify your ~/.netrc file so that all future commands are authenticated.

.. code-block:: bash

    gigalixir login 

Prepare Your App
----------------

There are a few steps involved to `make your app work on GIGALIXIR`_, but if you are starting a project from scratch, we recommend you clone the :bash:`gigalixir-getting-started` repo.

.. code-block:: bash

    git clone https://github.com/gigalixir/gigalixir-getting-started.git

You also need to create a GIGALIXIR app receord and set up your git remote.

.. code-block:: bash

    cd gigalixir-getting-started
    gigalixir create app $YOUR_APP_NAME

Deploy!
-------

Finally, build and deploy.

.. code-block:: bash

    git push gigalixir
    curl https://$YOUR_APP_NAME.gigalixirapp.com/

.. _`make your app work on GIGALIXIR`:

Modifying an Existing App to Run on GIGALIXIR
=============================================

TODO

.. _`money back guarantee`:

Money-back Guarantee
====================

If you are unhappy for any reason within the first 31 days, contact us to get a refund up to $75. Enough to run a 3 node cluster for 31 days.

How Does GIGALIXIR Work?
========================

We use Kubernetes and Docker to run your apps. We use a git server with pre-receive hooks to build your apps. We use Google Cloud Storage to store your release tarball, also called a slug. We built an API server which orchestrates everything together. 

TODO: insert diagram, component list with descriptions

Life of a Deploy
----------------

When you run :bash:`git push gigalixir`, our git server receives your source code and kicks off a build using a pre-receive hook. We build your app in a docker container which produces a slug which we store for later.

We only build the master branch and ignore other branches. When building, we cache compiled files and dependencies so you do not have to repeat the work on every deploy. We support git submodules. 

Once your slug is built, we upload it to cloud storage and we create a new release record for your app which points at the location of the new slug. The release record also includes a :bash:`rollback_id` which you can use later on if you need to rollback to this release. 

Then we create or update your Kubernetes configuration to deploy the app. We create a separate Kubernetes namespace for every app, a service account, an ingress for HTTP traffic, an ingress for SSH traffic, a TLS certificate, a service, and finally a deployment which creates pods and containers. 

The container that runs your app is a derivative of `heroku/cedar:14`_. The entrypoint is a script that sets up necessary environment variables including those from your `app configuration`_. It also starts an SSH server, installs your SSH keys, downloads the current slug, and executes it. We automatically generate and set up your erlang cookie, distributed node name, and phoenix secret key base for you. We also set up the Kubernetes permissions and libcluster selector you need to `cluster your nodes`_. We poll for your SSH keys every minute in case they have changed.

At this point, your app is running. The Kubernetes ingress controller is routing traffic from your host to the appropriate pods and terminating SSL/TLS for you automatically.


If at any point, the deploy fails, we rollback to the last know good release.

Cleaning Your Cache
-------------------

There is an extra flags you can pass to clean your cache before building in case you need it, but you need git 2.9.0 or higher for it to work. 

.. code-block:: bash

    git -c http.extraheader="GIGALIXIR-CLEAN: true" push gigalixir


Life of a Hot Upgrade
---------------------

There is an extra flag you can pass to deploy by hot upgrade instead of a restart. You have to make sure you bump your app version in your :bash:`mix.exs`. Distillery autogenerates your appup file, but you can supply a custom appup file if you need it. For more information, look at the `Distillery appup documentation`_.

.. code-block:: bash

    git -c http.extraheader="GIGALIXIR-HOT: true" push gigalixir

A hot upgrade follows the same steps as a regular deploy, except for a few differences. In order for distillery to build an upgrade, it needs access to your old app so we download it and make it available in the docker build container. 

Once the slug is generated and uploaded, we execute an upgrade script on each run container instead of restarting. The upgrade script downloads the new slug, and calls `Distillery's upgrade command`_. Your app should now be upgraded in place without any downtime, dropped connections, or loss of in-memory state.

.. _`cluster your nodes`:

Clustering Nodes
================

TODO

.. _`app configuration`:

App Configuration/Enviroment Variables
======================================

TODO

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _`pip documentation`: https://packaging.python.org/installing/
.. _`Distillery appup documentation`: https://hexdocs.pm/distillery/upgrades-and-downgrades.html#appups
.. _`Distillery's upgrade command`: https://hexdocs.pm/distillery/walkthrough.html#deploying-an-upgrade
.. _`heroku/cedar:14`: https://hub.docker.com/r/heroku/cedar/
