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

|signup details|

.. code-block:: bash

    gigalixir signup


Log In
------

Next, log in. This will grant you an api key which expires in 365 days. It will also optionally modify your ~/.netrc file so that all future commands are authenticated.

.. code-block:: bash

    gigalixir login 

Prepare Your App
----------------

There are a few steps involved to `make your existing app work on GIGALIXIR`_, but if you are starting a project from scratch, we recommend you clone the :bash:`gigalixir-getting-started` repo.

.. code-block:: bash

    git clone https://github.com/gigalixir/gigalixir-getting-started.git

Set Up App for Deploys
----------------------

|set up app for deploys|

.. code-block:: bash

    cd gigalixir-getting-started
    gigalixir create 

Deploy!
-------

Finally, build and deploy.

.. code-block:: bash

    git push gigalixir
    curl https://$YOUR_APP_NAME.gigalixirapp.com/

.. _`make your existing app work on GIGALIXIR`:

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

.. _`life of a deploy`:

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

At this point, your app is running. The Kubernetes ingress controller is routing traffic from your host to the appropriate pods and terminating SSL/TLS for you automatically. For more information about how SSL/TLS works, see :ref:`how-tls-works`.

If at any point, the deploy fails, we rollback to the last know good release.

.. _how-tls-works:

How SSL/TLS Works
-----------------

TODO

Cleaning Your Cache
-------------------

There is an extra flags you can pass to clean your cache before building in case you need it, but you need git 2.9.0 or higher for it to work. 

.. code-block:: bash

    git -c http.extraheader="GIGALIXIR-CLEAN: true" push gigalixir


.. _life-of-a-hot-upgrade:

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
 
.. _`replica sizing`:

Replica Sizing
==============

TODO
 
Monitoring
==========

TODO
 
How to Set Up Distributed Phoenix Channels
==========================================

If you have successfully clustered your nodes, then distributed Phoenix channels *just work* out of 
the box. No need to follow any of the steps described in `Running Elixir and Phoenix projects on a 
cluster of nodes`_. See more information on how to `cluster your nodes`_.
 
How to Sign Up for an Account
=============================

|signup details|

.. code-block:: bash

    gigalixir signup


How to Create an App
====================

|set up app for deploys|

.. code-block:: bash

    gigalixir create 

How to Deploy an App
====================

Deploying an app is done using a git push, the same way you would push code to github. For more information
about how this works, see `life of a deploy`_.

.. code-block:: bash

    git push gigalixir
 
How to Scale an App
===================

You can scale your app by adding more memory and cpu to each container, also called a replica. You can also
scale by adding more replicas. Both are handled by the following command. For more information about, see
`replica sizing`_.

.. code-block:: bash

    gigalixir scale $APP_NAME --replicas=2 --size=0.6

How to Configure an App
=======================

All app configuration is done through envirnoment variables. You can get, set, and delete configs using the following commands. Note that setting configs does not automatically restart your app so you may need to do that yourself. We do this to give you more control at the cost of simplicity. It also potentially enables hot config updates or updating your environment variables without restarting. For more information on hot configuration, see :ref:`hot-configure`. For more information about using environment variables for app configuration, see `The Twelve-Factor App's Config Factor`_. For more information about using environment variables in your Elixir app, see :ref:`distillery-replace-os-vars`.
 
.. code-block:: bash

    $ gigalixir configs $APP_NAME
    {}
    $ gigalixir set_config $APP_NAME FOO bar
    $ gigalixir configs $APP_NAME                                                                                 
    {
      "FOO": "bar"
    }
    $ gigalixir delete_config $APP_NAME FOO                                                                           
    $ gigalixir configs $APP_NAME
    {}

.. _`hot-configure`:

How to Hot Configure an App
===========================

This feature is still a work in progress.

How to Hot Upgrade an App
=========================

To do a hot upgrade, deploy your app with the extra header shown below. You'll need git v2.9.0 for this 
to work. For information on how to install the latest version of git on Ubuntu, see `this stackoverflow question <http://stackoverflow.com/questions/19109542/installing-latest-version-of-git-in-ubuntu>`_. For more information about how hot upgrades work, see :ref:`life-of-a-hot-upgrade`.

.. code-block:: bash

    git -c http.extraheader="GIGALIXIR-HOT: true" push gigalixir
 
How to Rollback an App
======================

To rollback one release, run the following command. 
 
.. code-block:: bash

    gigalixir rollback $APP_NAME

To rollback to a specific release, find the :bash:`rollback_id` by listing all releases. You can see
which SHA the release was built on and when it was built. This will also automatically restart your app
with the new release.

.. code-block:: bash

    $ gigalixir releases foo
    [
      {
        "created_at": "2017-04-12T17:43:28.000+00:00", 
        "customer_app_name": "gigalixir_getting_started", 
        "rollback_id": "2fbf5dd5-b920-4f2c-aeea-ebde333ee1e6", 
        "sha": "77f6c2952129ffecccc4e56ae6b27bba1e65a1e3", 
        "slug_url": "<REDACTED>"
      }, 
      ...
    ]

Then specify the rollback_id when rolling back.

.. code-block:: bash

    gigalixir rollback $APP_NAME --rollback_id=2fbf5dd5-b920-4f2c-aeea-ebde333ee1e6

The release list is immutable so when you rollback, we create a new release on top of the old releases,
but the new release refers to the old slug. 

How to Set Up a Custom Domain
=============================

After your first deploy, you can see your app by visiting https://$APP_NAME.gigalixirapp.com/, but if 
you want, you can point your own domain such as www.example.com to your app. To do this, first modify
your DNS records and point your domain to $APP_NAME.gigalixirapp.com using a CNAME record. Then, run 
the following command to add a custom domain.

.. code-block:: bash

    gigalixir add_domain $APP_NAME www.example.com

This will do a few things. It registers your fully qualified domain name in the load balancer so that
it knows to direct traffic to your containers. It also sets up SSL/TLS encryption for you. For more
information on how SSL/TLS works, see :ref:`how-tls-works`.

The GIGALIXIR Command-Line Interface
====================================

  - installation
  - encryption
  - no news is good news
  - exit codes
  - stderr vs stdout
  - options vs arguments
  - naming
  - authentication
  - error reporting
  - open source
 
How to Set Up SSL/TLS
=====================

SSL/TLS certificates are set up for you automatically assuming your custom domain is set up properly. You
shouldn't have to lift a finger. For more information on how this works, see :ref:`how-tls-works`.
 
How to Tail Logs
================

You can tail logs in real-time aggregated across all containers using the following command. Note that it
takes up to a minute or so to start streaming logs because it sets up a Stackdriver sink and PubSub topic
on-demand. We're working on improving this, but if you need more logging features, we suggest `PaperTrail`_.
We have tested and verified that it works.

.. code-block:: bash

    gigalixir logs $APP_NAME
 

.. _managing-ssh-keys:

Managing SSH Keys
=================

TODO

How to SSH into a Production Container
======================================

To SSH into a running production container, first, add your public SSH keys to your account. For more information on managing SSH keys, see :ref:`managing-ssh-keys`.

.. code-block:: bash

    gigalixir add_ssh_key "ssh-rsa <REDACTED> foo@gigalixir.com"

Then use the following command to SSH into a live production container. If you are running multiple 
containers, this will put you in a random container. We do not yet support specifying which container you want to SSH to. In order for this work, you must add your public SSH keys to your account.

.. code-block:: bash

    gigalixir ssh $APP_NAME

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

    gigalixir releases $APP_NAME
 
How to Change or Reset Your Password
====================================

To change your password, run


.. code-block:: bash

    gigalixir change_password

If you forgot your password, send a reset token to your email address by running the following command and following the instructions in the email.

.. code-block:: bash

    gigalixir send_reset_password_token

How to Change Your Credit Card
==============================

To change your credit card, run

.. code-block:: bash

    gigalixir set_payment_method

How to Delete an App
====================

There is currently no way to completely delete an app, but if you scale the replicas down to 0, you will not incur any charges. We are working on implementing this feature.

How to Delete your Account
==========================

There is currently no way to completely delete an account. We are working on implementing this feature.

How to View Billing and Usage
=============================

TODO

How to Restart an App
=====================

TODO

How to Run Jobs
========================

TODO

How to Reset your API Key
=========================

TODO

How to Log Out
==============

TODO

How to Log In
=============

TODO

How to Connect a Database
=========================

TODO

How to Run Migrations
=====================

TODO

.. _`Launching a remote console`: 

How to Drop into a Remote Console
=================================

.. code-block:: bash

    gigalixir ssh $APP_NAME -c remote_console

How to Run Distillery Commands
==============================

Since we use Distillery to build releases, we also get all the commands Distillery provides such as ping, rpc, command, and eval. `Launching a remote console`_ is just a special case of this. To run a Distillery command, run the command below. For a complete list of commands, see `Distillery's boot.eex`_.

.. code-block:: bash

    gigalixir ssh $APP_NAME -c $COMMAND

.. _`Distillery's boot.eex`: https://github.com/bitwalker/distillery/blob/master/priv/templates/boot.eex#L417

.. _app-status:

How to Check App Status
=======================

TODO

How to Launch a Remote Observer
===============================

To launch observer and connect it to a production node

.. code-block:: bash

    gigalixir observer $APP_NAME

and follow the instructions. This connects to a random container. We don't currently allow you to specify which container you want to connect to.

.. _distillery-replace-os-vars:

Using Environment Variables in your App
=======================================

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
.. _`container that runs your app`: https://github.com/gigalixir/gigalixir-run
.. _`herokuish`: https://github.com/gliderlabs/herokuish
.. _`elixir homepage`: http://elixir-lang.org/
.. _`phoenix homepage`: http://www.phoenixframework.org/
.. _`twelve-factor methodology`: https://12factor.net/
.. _`PaperTrail`: https://papertrailapp.com/
.. _`Running Elixir and Phoenix projects on a cluster of nodes`: https://dockyard.com/blog/2016/01/28/running-elixir-and-phoenix-projects-on-a-cluster-of-nodes
.. |signup details| replace:: Create an account using the following command. It will prompt you for your email address and password. You will have to confirm your email before continuing. It will also prompt you for credit card information. GIGALIXIR currently does not offer a free trial, but we do offer a `money back guarantee`_. Please don't hesitate to use it.
.. |set up app for deploys| replace:: To create your app, run the following command. It will also set up a git remote so you can later run :bash:`git push gigalixir`. This must be run from within a git repository folder. An app name will be generated for you, but you can also optionally supply an app name if you wish. There is currently no way to change your app name.
.. _`The Twelve-Factor App's Config Factor`: https://12factor.net/config
