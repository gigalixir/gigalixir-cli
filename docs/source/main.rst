Quick Start
===========

Prequisites
-----------

.. role:: bash(code)
    :language: bash

You should make sure you have :bash:`pip` installed. For help, take a look at the `pip documentation`_.

Install the Command-Line Interface
----------------------------------

Next install, the command-line interface. GIGALIXIR currently does not have a web interface. We want the command-line to be a first-class citizen so that you can build scripts and tools easily.

.. code-block:: bash

    pip install gigalixir

Create an Account
-----------------

Create an account using the following command. It will prompt you for your email address and password. You will have to confirm your email before continuing. It will also prompt you for credit card information. GIGALIXIR currently does not offer a free trial, but we do offer a `money back guarantee`_. Please don't hesitate to use it.

.. code-block:: bash

    gigalixir signup

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
    gigalixir create_app $YOUR_APP_NAME

Deploy!
-------

Finally, build and deploy.

.. code-block:: bash

    git push gigalixir
    curl https://$YOUR_APP_NAME.gigalixirapp.com/

.. _`make your app work on GIGALIXIR`:

Modifying an Existing App to Run on GIGALIXIR
=============================================

Required

  - Distillery
  - Buildpacks

Optional 

  - Libcluster
  - Secrets
  - Migrations
  - Git

.. _`money back guarantee`:

Money-back Guarantee
====================

If you are unhappy for any reason within the first 31 days, contact us to get a refund up to $75. Enough to run a 3 node cluster for 31 days.

How Does GIGALIXIR Work?
========================

We use Kubernetes and Docker to run your apps. We use a git server with pre-receive hooks to build your apps. We use Google Cloud Storage to store your release tarball, also called a slug. We built an API server which orchestrates everything together. 

TODO: insert diagram, component list with descriptions

Components
----------

  - Slug Builder

    - Herokuish
    - Buildpacks

  - API Server / Controller
  - Database
  - Logger

    - PubSub
    - Stackdriver

  - Router

    - Nginx Ingress Controller

  - TLS Manager

    - kube-lego

  - Kubernetes
  - Slug Storage
  - Secret/Config Storage
  - Observer
  - Run Container
  - Command-Line Interface

Concepts
--------

  - User
  - API Key
  - SSH Key
  - App
  - Releases
  - Replicas
  - Custom Domain
  - Payment Method
  - Permission

Life of a Deploy
----------------

When you run :bash:`git push gigalixir`, our git server receives your source code and kicks off a build using a pre-receive hook. We build your app in a docker container using `herokuish`_ which produces a slug which we store for later. The buildpacks used are defined in your :bash:`.buildpack` file.

By default, the buildpacks we use include

  - https://github.com/gigalixir/gigalixir-buildpack-clean-cache.git

    - To clean the cache if enabled.

  - https://github.com/HashNuke/heroku-buildpack-elixir.git

    - To run mix compile
    - If you want, you can `configure this buildpack <https://github.com/HashNuke/heroku-buildpack-elixir#configuration>`_.

  - https://github.com/gjaldon/heroku-buildpack-phoenix-static.git

    - To run mix phoenix.digest

  - https://github.com/gigalixir/gigalixir-buildpack-distillery.git

    - To run mix release

We only build the master branch and ignore other branches. When building, we cache compiled files and dependencies so you do not have to repeat the work on every deploy. We support git submodules. 

Once your slug is built, we upload it to cloud storage and we create a new release record for your app which points at the location of the new slug. The release record also includes a :bash:`rollback_id` which you can use later on if you need to rollback to this release. 

Then we create or update your Kubernetes configuration to deploy the app. We create a separate Kubernetes namespace for every app, a service account, an ingress for HTTP traffic, an ingress for SSH traffic, a TLS certificate, a service, and finally a deployment which creates pods and containers. 

The `container that runs your app`_ is a derivative of `heroku/cedar:14`_. The entrypoint is a script that sets up necessary environment variables including those from your `app configuration`_. It also starts an SSH server, installs your SSH keys, downloads the current slug, and executes it. We automatically generate and set up your erlang cookie, distributed node name, and phoenix secret key base for you. We also set up the Kubernetes permissions and libcluster selector you need to `cluster your nodes`_. We poll for your SSH keys every minute in case they have changed.

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

Frequently Asked Questions
==========================

  - *What is Elixir? What is Phoenix?*

    This is probably best answered by someone else. Take a look at the `elixir homepage`_ and 
    the `phoenix homepage`_.

  - *How is GIGALIXIR different from Heroku, Deis, Dokku, Elastic Beanstalk, and App Engine?*

    Heroku is a really great platform to run you Elixir apps and much of GIGALIXIR was designed
    based on their excellent `twelve-factor methodology`_. But Heroku made design decisions that
    prioritize simplicity and it is difficult to run Elixir and Phoenix on Heroku unless you are
    willing to sacrifice many of the greatest advantages Elixir and Phoenix provide like node
    clustering, hot upgrades, and remote observer.

    Deis is also really great platform if you want to run on your own infrastructure. You can 
    install Deis and run apps almost as easily as Heroku, but they do not support Elixir's
    distributed features out of the box. While it can be done, there's a lot of extra work 
    you'll have to do to support clustering, hot upgrades, and remote observer. GIGALIXIR has
    already figured these out so you can focus on building your app. 

    Dokku is also a great solution, but only runs on a single node so it inherently does not support
    clustering.

    Elastic Beanstalk and App Engine similarly does not support distributed Elixir features 
    without a lot of extra effort.

  - *I thought you weren't supposed to SSH into docker containers!?*

    There are a lot of reasons not to SSH into your docker containers, but it is a tradeoff that
    doesn't fit that well with Elixir apps. We need to allow SSH in order to connect a remote observer
    to a production node, drop into a remote console, and do hot upgrades. If you don't need any
    of these features, then you probably don't need and probably shouldn't SSH into your containers,
    but it is available should you want to. Just keep in mind that full SSH access to your containers
    means you have almost complete freedom to do whatever you want including shoot yourself in the foot.
    Any manual changes you make during an SSH session will also be wiped out if the container restarts 
    itself so use SSH with care.

  - *Why do you download the slug on startup instead of including the slug in the Docker image?*

    Great question! The short answer is that after a hot-upgrade, if the container restarts, you end 
    up reverting back to the slug included in the container. By downloading the slug on startup, 
    we can always be sure to pull the most current slug even after a hot upgrade.

    This sort of flies in the face of a lot of advice about how to use Docker, but it is a tradeoff
    we felt was necessary in order to support hot upgrades in a containerized environment. The 
    non-immutability of the containers can cause problems, but over time we've ironed them out and
    feel that there is no longer much downside to this approach. All the headaches that came as a
    result of this decision are our responsibility to address and shouldn't affect you as a customer. 
    In other words, you reap the benefits while we pay the cost, which is one of the ways we provide value.

Pricing Details
===============

TODO
 
Replica Sizing
===============

TODO
 
Logging
===============

TODO
 
Monitoring
===============

TODO
 
How to Set Up Distributed Phoenix Channels
===============

TODO
 
How to Create an Account
===============

TODO
 
How to Create an App
===============

TODO
 
How to Deploy an App
===============

TODO
 
How to Scale an App
===============

TODO
 
How to Configure an App
===============

TODO
 
How to Hot Upgrade an App
===============

TODO
 
How to Rollback an App
===============

TODO
 
How to Set Up a Custom Domain
===============

TODO
 
How to Set Up SSL/TLS
===============

TODO
 
How to Tail Logs
===============

TODO
 
How to SSH into a Production Container
===============

TODO
 
How to List Apps
===============

TODO
 
How to List Releases
===============

TODO
 
How to Change or Reset Your Password
==============

TODO

How to Change Your Credit Card
==============

TODO

How to Delete an App
==============

TODO

How to Delete your Account
==============

TODO

How to View Billing and Usage
==============

TODO

How to Connect a Database
==============

TODO

How to Run Migrations
==============

TODO

How to Drop into a Remote Console
==============

TODO

How to Launch a Remote Observer
===============================

To launch observer and connect it to a production node

.. code-block:: bash

    gigalixir observer $APP_NAME

and follow the instructions. This connects to a random container. We don't currently allow you to specify which container you want to connect to.

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _`pip documentation`: https://packaging.python.org/installing/
.. _`Distillery appup documentation`: https://hexdocs.pm/distillery/upgrades-and-downgrades.html#appups
.. _`Distillery's upgrade command`: https://hexdocs.pm/distillery/walkthrough.html#deploying-an-upgrade
.. _`heroku/cedar:14`: https://hub.docker.com/r/heroku/cedar/
.. _`container that runs your app`: https://github.com/gigalixir/gigalixir-run
.. _`herokuish`: https://github.com/gliderlabs/herokuish
.. _`elixir homepage`: http://elixir-lang.org/
.. _`phoenix homepage`: http://www.phoenixframework.org/
.. _`twelve-factor methodology`: https://12factor.net/
