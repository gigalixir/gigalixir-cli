What is GIGALIXIR?
==================

GIGALIXIR is a Platform-as-a-Service designed for Elixir and Phoenix apps. PaaSes are designed to make it simple to deploy, run, and manage an app in production, but GIGALIXIR is unique because it is designed to support all of features that probably drew you to Elixir in the first place, like node clustering, hot upgrades, and remote observer. Moreover, some platforms restart your processes every 24 hours, restrict you to 50 simultaneous connections per instance, and limit each connection to 30 seconds. GIGALIXIR made opinionated design decisions from the ground up to support all the fetaures of Elixir because we know that most Elixir apps are built to be distributed, highly available, and handle large numbers of concurrent long-lived connections. 

.. _`quick start`:

Quick Start
===========

Prequisites
-----------

.. role:: elixir(code)
    :language: elixir

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

There are a few steps involved to `make your existing app work on GIGALIXIR`_, but if you are starting a project from scratch, we recommend you clone the `gigalixir-getting-started`_ repo.

.. code-block:: bash

    git clone https://github.com/gigalixir/gigalixir-getting-started.git

Set Up App for Deploys
----------------------

|set up app for deploys|

.. code-block:: bash

    cd gigalixir-getting-started
    APP_NAME=$(gigalixir create)

Deploy!
-------

Finally, build and deploy.

.. code-block:: bash

    git push gigalixir
    curl https://$APP_NAME.gigalixirapp.com/

Note!
-----

The `gigalixir-getting-started`_ app does not have a database connected yet. In fact, we removed the Ecto Repo from the supervisor tree to prevent database connection attempts. To connect a database, see :ref:`connect-database`.

What's Next?
------------

- :ref:`connect-database`
- :ref:`configs`
- :ref:`scale`

.. _`make your existing app work on GIGALIXIR`:

Modifying an Existing App to Run on GIGALIXIR
=============================================

Required Modifications
----------------------

These modifications are required to run on GIGALIXIR, but features such as node clustering probably won't work unless you make some optional modifications described in the next section.

Install Distillery to Build Releases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Distillery is currently the only supported release tool. We assume you have followed the `Distillery installation instructions`_. We use Distillery instead of bundling up your source code is to support hot upgrades. 

.. _`Distillery installation instructions`: https://hexdocs.pm/distillery/getting-started.html#installation-setup

.. _`buildpacks`:

Specify Buildpacks to Compile and Build Releases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We rely on buildpacks to compile and build your release. Create a :bash:`.buildpacks` file with the following contents.

.. code-block:: bash

    https://github.com/gigalixir/gigalixir-buildpack-clean-cache.git
    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-distillery.git

If you *really* want, the :bash:`gigalixir-buildpack-clean-cache` is optional if you know you will never want to clean your GIGALIXIR build cache. Also, :bash:`heroku-buildpack-phoenix-static` is optional if you do not have phoenix static assets. For more information about buildpacks, see :ref:`life of a deploy`.


Optional Modifications
----------------------

These modifications are not required, but are recommended if you want to use all of features GIGALIXIR offers.

Set up Node Clustering with Libcluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to cluster nodes, you should install libcluster. For more information about installing libcluster, see :ref:`cluster your nodes`.

Secrets using Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, Phoenix creates a :bash:`prod.secret.exs` file to store secrets. If you want to continue using :bash:`prod.secret.exs` you'll have to commit it to version control so we can bundle it into your release. This is usually not a good idea, though. 

GIGALIXIR prefers that you use environment variables for secrets and configuration. To do this, you'll want to delete your :bash:`prod.secret.exs` file, move the contents to your :bash:`prod.exs` file, and modify the values to pull from environment variables. 

Open your :bash:`prod.exs` file and delete the following line if it is there

.. code-block:: elixir

    import_config "prod.secret.exs"

Then add the following in :bash:`prod.exs`

.. code-block:: elixir

     config :gigalixir_getting_started, GigalixirGettingStarted.Endpoint,
       server: true,
       secret_key_base: "${SECRET_KEY_BASE}"
     
     config :gigalixir_getting_started, GigalixirGettingStarted.Repo,
       adapter: Ecto.Adapters.Postgres,
       url: {:system, "DATABASE_URL"},
       pool_size: 20

Replace :elixir:`:gigalixir_getting_started` and :elixir:`GigalixirGettingStarted` with your app name. You don't have to worry about setting your SECRET_KEY_BASE config because we generate one and set it for you. If you use a database, you'll have to set the DATABASE_URL yourself. You can do this by running the following. For more information on setting configs, see :ref:`configs`.

.. code-block:: bash

    gigalixir set_config $APP_NAME DATABASE_URL "ecto://user:pass@host:port/db"

Set Up Migrations
^^^^^^^^^^^^^^^^^

In development, you use `Mix`_ to run database migrations. In production, `Mix`_ is not available so you need a different approach. Instructions on how to set up and run migrations are described in more detail in :ref:`migrations`.

.. _`Mix`: https://hexdocs.pm/mix/Mix.html

Set Up Hot Upgrades with Git v2.9.0
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run hot upgrades, you send an extra http header when running :bash:`git push gigalixir`. Extra HTTP headers are only supported in git 2.9.0 and above so make sure you upgrade if needed. For information on running hot upgrades, see :ref:`hot-upgrade` and :ref:`life-of-a-hot-upgrade`.

Known Issues
============

  - Logging is still currently in the alpha testing stage. It's known to have slow startup, high latency, and will periodically fail entirely if another app is producing too many logs. We are currently rebuilding the logging system to address these issues. In most cases, however, logging should still be useful. If it doesn't fit your needs, we recommend `PaperTrail`_.

How Does GIGALIXIR Work?
========================

When you deploy an app on GIGALIXIR, you :bash:`git push` the source code to a build server. The build server compiles the code and assets and generates a standalone tarball we call a slug. The controller then combines the slug and your app configuration into a release. The release is deployed to run containers which actually run your app.

.. image:: deploy.png

When you update a config, we encrypt it, store it, and combine it with the existing slug into a new release. The release is deployed to run containers.

.. image:: config.png

Components
----------

  - *Build Server*: This is responsible for building your code into a release or slug.
  - *API Server / Controller*: This is responsible for handling all user requests such as scaling apps, setting configs, etc. It is also responsible for deploying the release into a run container.
  - *Database*: The database is where all of your app configuration is stored. Configs are encrypted due to their sensitive nature.
  - *Logger*: This is responsible for collecting logs from all your containers, aggregating them, and streaming them to you.
  - *Router*: This is responsible for receiving web traffic for your app, terminating TLS, and routing the traffic to your run containers.
  - *TLS Manager*: This is responsible for automatically obtaining TLS certificates and storing them.
  - *Kubernetes*: This is responsible for managing your run containers.
  - *Slug Storage*: This is where your slugs are stored.
  - *Observer*: This is an application that runs on your local machine that connects to your production node to show you everything you could ever want to know about your live production app.
  - *Run Container*: This is the container that your app runs in.
  - *Command-Line Interface*: This is the command-line tool that runs on your local machine that you use to control GIGALIXIR.

Concepts
--------

  - *User*: The user is you. When you sign up, we create a user.
  - *API Key*: Every user has an API Key which is used to authenticate most API requests. You get one when you login and you can regenerate it at any time. It expires every 365 days.
  - *SSH Key*: SSH keys are what we use to authenticate you when SSHing to your containers. We usethem for remote observer, remote console, etc.
  - *App*: An app is your Elixir application.
  - *Release*: A release is a combination of a slug and a config which is deployed to a run container.
  - *Slug*: Each app is compiled and built into a slug. The slug is the actual code that is run in your containers. Each app will have many slugs, one for every deploy.
  - *Config*: A config is a set of key-value pairs that you use to configure your app. They are injected into your run container as environment variables.
  - *Replicas*: An app can have many replicas. A replica is a single instance of your app.
  - *Custom Domain*: A custom domain is a fully qualified domain that you control which you can set up to point to your app.
  - *Payment Method*: Your payment method is the credit card on file you use to pay your bill each month.
  - *Permission*: A permission grants another user the ability to deploy. Even though they can deploy, you remain the owner and are responsible for paying the bill.

.. _`life of a deploy`:

Life of a Deploy
----------------

When you run :bash:`git push gigalixir`, our git server receives your source code and kicks off a build using a pre-receive hook. We build your app in an isolated docker container which ultimately produces a slug which we store for later. The buildpacks used are defined in your :bash:`.buildpack` file.

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

Once your slug is built, we upload it to slug storage and we combine it with a config to create a new release for your app. The release is tagged with a :bash:`version` number which you can use later on if you need to rollback to this release. 

Then we create or update your Kubernetes configuration to deploy the app. We create a separate Kubernetes namespace for every app, a service account, an ingress for HTTP traffic, an ingress for SSH traffic, a TLS certificate, a service, and finally a deployment which creates pods and containers. 

The `container that runs your app`_ is a derivative of `heroku/cedar:14`_. The entrypoint is a script that sets up necessary environment variables including those from your `app configuration`_. It also starts an SSH server, installs your SSH keys, downloads the current slug, and executes it. We automatically generate and set up your erlang cookie, distributed node name, and phoenix secret key base for you. We also set up the Kubernetes permissions and libcluster selector you need to `cluster your nodes`_. We poll for your SSH keys every minute in case they have changed.

At this point, your app is running. The Kubernetes ingress controller is routing traffic from your host to the appropriate pods and terminating SSL/TLS for you automatically. For more information about how SSL/TLS works, see :ref:`how-tls-works`.

If at any point, the deploy fails, we rollback to the last known good release.

.. _how-tls-works:

How SSL/TLS Works
-----------------

We use kube-lego for automatic TLS certificate generation with Let's Encrypt. For more information, see `kube-lego's documentation`_. When you add a custom domain, we create a Kubernetes ingress for you to route traffic to your app. kube-lego picks this up, obtains certificates for you and installs them. Our ingress controller then handles terminating SSL traffic before sending it to your app.

.. _`kube-lego's documentation`: https://github.com/jetstack/kube-lego

Cleaning Your Cache
-------------------

There is an extra flag you can pass to clean your cache before building in case you need it, but you need git 2.9.0 or higher for it to work. 

.. code-block:: bash

    git -c http.extraheader="GIGALIXIR-CLEAN: true" push gigalixir


.. _life-of-a-hot-upgrade:

Life of a Hot Upgrade
---------------------

There is an extra flag you can pass to deploy by hot upgrade instead of a restart. You have to make sure you bump your app version in your :bash:`mix.exs`. Distillery autogenerates your appup file, but you can supply a custom appup file if you need it. For more information, look at the `Distillery appup documentation`_.

.. code-block:: bash

    git -c http.extraheader="GIGALIXIR-HOT: true" push gigalixir

A hot upgrade follows the same steps as a regular deploy, except for a few differences. In order for distillery to build an upgrade, it needs access to your old app so we download it and make it available in the build container. 

Once the slug is generated and uploaded, we execute an upgrade script on each run container instead of restarting. The upgrade script downloads the new slug, and calls `Distillery's upgrade command`_. Your app should now be upgraded in place without any downtime, dropped connections, or loss of in-memory state.

Frequently Asked Questions
==========================

*What is Elixir? What is Phoenix?*
----------------------------------

This is probably best answered by taking a look at the `elixir homepage`_ and the `phoenix homepage`_.

*How is GIGALIXIR different from Heroku and Deis Workflow?*
-----------------------------------------------------------

.. image:: venn.png

Heroku is a really great platform and much of GIGALIXIR was designed based on their excellent `twelve-factor methodology`_. Heroku and GIGALIXIR are similar in that they both try to make deployment and operations as simple as possible. Elixir applications, however, aren't very much like most other apps today written in Ruby, Python, Java, etc. Elixir apps are distributed, highly-available, hot-upgradeable, and often use lots of concurrent long-lived connections. GIGALIXIR made many fundamental design choices that ensure all these things are possible.

For example, Heroku restarts your app every 24 hours regardless of if it is healthy or not. Elixir apps are designed to be long-lived and many use in-memory state so restarting every 24 hours sort of kills that. Heroku also limits the number of concurrent connections you can have to 50 per instance. It also has limits to how long these connections can live. Heroku isolates each instance of your app so they cannot communicate with each other, which prevents node clustering. Heroku also restricts SSH access to your containers which makes it impossible to do hot upgrades, remote consoles, remote observers, production tracing, and a bunch of other things. The list goes on, but suffice it to say, running an Elixir app on Heroku forces you to give up a lot of the features that drew you to Elixir in the first place.

Deis Workflow is also really great platform and is very similar to Heroku, except you run it your own infrastructure. Because Deis is open source and runs on Kubernetes, you *could* make modifications to support node clustering and remote observer, but they won't work out of the box and hot upgrades would require some fundamental changes to the way Deis was designed to work. Even so, you'd still have to spend a lot of time solving problems that GIGALIXIR has already figured out for you.

On the other hand, Heroku and Deis are more mature products that have been around much longer. They have more features, but we are working hard to fill in the holes. Heroku and Deis also support languages other than Elixir. Heroku has a web interface, databases as a service, and tons of add-ons.

*I thought you weren't supposed to SSH into docker containers!?*
----------------------------------------------------------------

There are a lot of reasons not to SSH into your docker containers, but it is a tradeoff that doesn't fit that well with Elixir apps. We need to allow SSH in order to connect a remote observer to a production node, drop into a remote console, and do hot upgrades. If you don't need any of these features, then you probably don't need and probably shouldn't SSH into your containers, but it is available should you want to. Just keep in mind that full SSH access to your containers means you have almost complete freedom to do whatever you want including shoot yourself in the foot.  Any manual changes you make during an SSH session will also be wiped out if the container restarts itself so use SSH with care.

*Why do you download the slug on startup instead of including the slug in the Docker image?*
--------------------------------------------------------------------------------------------

Great question! The short answer is that after a hot-upgrade, if the container restarts, you end 
up reverting back to the slug included in the container. By downloading the slug on startup, 
we can always be sure to pull the most current slug even after a hot upgrade.

This sort of flies in the face of a lot of advice about how to use Docker, but it is a tradeoff
we felt was necessary in order to support hot upgrades in a containerized environment. The 
non-immutability of the containers can cause problems, but over time we've ironed them out and
feel that there is no longer much downside to this approach. All the headaches that came as a
result of this decision are our responsibility to address and shouldn't affect you as a customer. 
In other words, you reap the benefits while we pay the cost, which is one of the ways we provide value.

*How do I add worker processes?*
--------------------------------

Heroku and others allow you to specify different types of processes under a single app such as workers that pull work from a queue. With Elixir, that is rarely needed since you can spawn asynchronous tasks within your application itself. Elixir and OTP provide all the tools you need to do this type of stuff among others. For more information, see `Background Jobs in Phoenix`_ which is an excellent blog post. If you really need to run an Redis-backed queue to process jobs, take a look at Exq, but consider `whether you really need Exq`_.

.. _`Background Jobs in Phoenix`: http://blog.danielberkompas.com/2016/04/05/background-jobs-in-phoenix.html
.. _`whether you really need Exq`: https://github.com/akira/exq#do-you-need-exq


.. _`cluster your nodes`:

Clustering Nodes
================

We use libcluster to manage node clustering. For more information, see `libcluster's documentation`_. GIGALIXIR handles permissions so that you have access to Kubernetes endpoints and we automatically set your node name and erlang cookie so that your nodes can reach each other. We don't firewall each container from each other like Heroku does. We also automatically set the environment variables :bash:`LIBCLUSTER_KUBERNETES_SELECTOR`, :bash:`LIBCLUSTER_KUBERNETES_NODE_BASENAME`, :bash:`APP_NAME`, and :bash:`MY_POD_IP` for you. See `gigalixir-run's run-cmd script`_ for more details. 

.. _`libcluster's documentation`: https://github.com/bitwalker/libcluster

Your app configuration needs to have something like this in it. For a full example, see `gigalixir-getting-started's prod.exs file`_.


.. code-block:: elixir

    ...
    config :libcluster,
      topologies: [
        k8s_example: [
          strategy: Cluster.Strategy.Kubernetes,
          config: [
            kubernetes_selector: "${LIBCLUSTER_KUBERNETES_SELECTOR}",
            kubernetes_node_basename: "${LIBCLUSTER_KUBERNETES_NODE_BASENAME}"]]]
    ...

You also need to create a :bash:`rel/vm.args` file with something like this in it. For a full example, see `gigalixir-getting-started's vm.args file`_.

.. code-block:: elixir

    ## Name of the node
    -name ${MY_NODE_NAME}

    ## Cookie for distributed erlang
    -setcookie ${MY_COOKIE}
    ...

Lastly, you need to modify your distillery config so it knows where to find your :bash:`vm.args` file. Something like this. For a full example, see `gigalixir-getting-started's rel/config.exs file`_.

.. code-block:: elixir

    ...
    environment :prod do
      ...
      # this is just to get rid of the warning. see https://github.com/bitwalker/distillery/issues/140
      set cookie: :"${MY_COOKIE}"
      set vm_args: "rel/vm.args"
    end
    ...

.. _`gigalixir-getting-started's vm.args file`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/rel/vm.args
.. _`gigalixir-getting-started's prod.exs file`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/config/prod.exs#L68
.. _`gigalixir-getting-started's rel/config.exs file`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/rel/config.exs#L27
.. _`gigalixir-run's run-cmd script`: https://github.com/gigalixir/gigalixir-run/blob/master/run-cmd

.. _`pricing`:

Pricing Details
===============

Every month after you sign up on the same day of the month, we calculate the number of replica-size-seconds used, multiply that by $0.00001866786, and charge your credit card.

replica-size-seconds is how many replicas you ran multiplied by the size of each replica multiplied by how many seconds they were run. This is aggregated across all your apps and is prorated to the second.

For example, if you ran a single 0.5 size replica for 31 days, you will have used 

.. code-block:: bash

  (1 replica) * (0.5 size) * (31 days) = 1339200 replica-size-seconds. 
  
Your monthly bill will be 

.. code-block:: bash

  1339200 * $0.00001866786 = $25.00.

If you ran a 1.0 size replica for 10 days, then scaled it up to 3 replicas, then 10 days later scaled the size up to 2.0 and it was a 30-day month, then your usage would be 

.. code-block:: bash

  (1 replica) * (1.0 size) * (10 days) + (3 replicas) * (1.0 size) * (10 days) + (3 replicas) * (2.0 size) * (10 days) = 8640000 replica-size-seconds 
  
Your monthly bill will be

.. code-block:: bash

  8640000 * $0.00001866786 = $161.29.
 
.. _`replica sizing`:

Replica Sizing
==============

  - A replica is a docker container that your app runs in.
  - Replica sizes are available in increments of 0.1 between 0.5 and 16. Contact us if you need a bigger size.
  - 1 size unit is 1GB memory and 1 CPU share.
  - 1 CPU share is 200m as defined using `Kubernetes CPU requests`_ or roughly 20% of a core guaranteed.

    - If you are on a machine with other containers that don't use much CPU, you can use as much CPU as you like.

  - Memory is defined using `Kuberenetes memory requests`_.

    - If you are on a machine with other machines that don't use much memory, you can use as much memory as you like.

  - Memory and CPU sizes can not be adjusted separately.

.. _`Kubernetes CPU requests`: https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#meaning-of-cpu
.. _`Kuberenetes memory requests`: https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#meaning-of-memory
 
Releases
========

One common pitfall for beginners is how releases differ from running apps with `Mix`_. In development, you typically have access to `Mix`_ tasks to run your app, migrate your database, etc. In production, we use releases. With releases, your code is distributed in it's compiled form and is almost no different from an Erlang release. You no longer have access to `Mix`_ commands. However, in return, you also have access to hot upgrades and smaller slug sizes, and a "single package which can be deployed anywhere, independently of an Erlang/Elixir installation. No dependencies, no hassle" [1].

[1]: https://github.com/bitwalker/distillery

Limits
======

GIGALIXIR is designed for Elixir/Phoenix apps and it is common for Elixir/Phoenix apps to have many connections open at a time and to have connections open for long periods of time. Because of this, we do not limit the number of concurrent connections or the duration of each connection. 

We also know that Elixir/Phoenix apps are designed to be long-lived and potentially store state in-memory so we do not restart replicas arbitrarily. In fact, replicas should not restart at all, unless there is an extenuating circumstance that requires it.  For apps that require extreme high availability, we suggest that your app be able to handle node restarts just as you would for any app not running on GIGALIXIR.

Monitoring
==========

GIGALIXIR doesn't provide any monitoring out of the box, but we are working on it.
 
.. _distillery-replace-os-vars:
.. _`app configuration`:

Using Environment Variables in your App
=======================================

Environment variables with Elixir, Distillery, and releases in general are one of those things that always trip up beginners. I think `Distillery's Runtime Configuration`_ explains it better than I can. GIGALIXIR automatically sets :bash:`REPLACE_OS_VARS=true` for you so all you have to do is add something like this to your config.exs file, set your app config, and you should be good to go. For information about how to set app configs, see :ref:`configs`.

.. code-block:: elixir

    ...
    config :myapp,
        my_config: "$MY_CONFIG"
    ...

Then set MY_CONFIG, by running

.. code-block:: bash

    gigalixir set_config MY_CONFIG foo

In your app code, 

.. code-block:: elixir

    Application.get_env(:myapp, :my_config) == "foo"
    System.get_env("MY_CONFIG") == "foo"

.. _`Distillery's Runtime Configuration`: https://hexdocs.pm/distillery/runtime-configuration.html#content

Troubleshooting
===============

TODO: Common issues go here.

Support/Help
============

If you run into issues, `Stack Overflow`_ is the best place to search. If you can't find an answer, the developers at GIGALIXIR monitor `the gigalixir tag`_ and will answer questions there. We prefer Stack Overflow over a knowledge base because it is public and collaborative. If you have a private question, email help@gigalixir.com or call us at `(415) 326-8880`_.

.. _`Stack Overflow`: http://stackoverflow.com/
.. _`the gigalixir tag`: http://stackoverflow.com/questions/tagged/gigalixir
.. _`(415) 326-8880`: tel:4153268880

The GIGALIXIR Command-Line Interface
====================================

The GIGALIXIR Command-Line Interface or CLI is a tool you install on your local machine to control GIGALIXIR.

Installation
------------

Install :bash:`gigalixir` using :bash:`pip install gigalixir`. If you don't have pip installed, take a look at the `pip documentation`_.

Encryption
----------

All HTTP requests made between your machine and GIGALIXIR's servers are encrypted.

Conventions
-----------

  - No news is good news: If you run a command that produces no output, then the command probably succeeded.
  - Exit codes: Commands that succeed will return a 0 exit code, and non-zero otherwise.
  - stderr vs stdout: Stderr is used for errors and for log output. Stdout is for the data output of your command.

Authentication
--------------

When you login with your email and password, you receive an API key. This API key is stored in your :bash:`~/.netrc` file. Commands generally use your :bash:`~/.netrc` file to authenticate with few exceptions.

Error Reporting
---------------

Bugs in the CLI are reported to GIGALIXIR's error tracking service. Currently, the only way to disable this is by modifying the source code. `Pull requests`_ are also accepted!

.. _`Pull requests`: https://github.com/gigalixir/gigalixir-cli/pulls

Open Source
-----------

The GIGALIXIR CLI is open source and we welcome pull requests. See `the gigalixir-cli repository`_.

.. _`the gigalixir-cli repository`: https://github.com/gigalixir/gigalixir-cli
 
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
 
.. _`scale`:

How to Scale an App
===================

You can scale your app by adding more memory and cpu to each container, also called a replica. You can also
scale by adding more replicas. Both are handled by the following command. For more information about, see
`replica sizing`_.

.. code-block:: bash

    gigalixir scale $APP_NAME --replicas=2 --size=0.6

.. _`configs`:

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
.. _`hot configuration updates`: 

How to Hot Configure an App
===========================

This feature is still a work in progress.

.. _`hot-upgrade`:

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

To rollback to a specific release, find the :bash:`version` by listing all releases. You can see which SHA the release was built on and when it was built. This will also automatically restart your app
with the new release.

.. code-block:: bash

    $ gigalixir releases foo
    [
      {
        "created_at": "2017-04-12T17:43:28.000+00:00", 
        "version": "5", 
        "sha": "77f6c2952129ffecccc4e56ae6b27bba1e65a1e3", 
        "summary": "Set `DATABASE_URL` config var."
      }, 
      ...
    ]

Then specify the version when rolling back.

.. code-block:: bash

    gigalixir rollback $APP_NAME --version=5

The release list is immutable so when you rollback, we create a new release on top of the old releases, but the new release refers to the old slug. 

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

In order to SSH, run remote observer, remote console, etc, you need to set up your SSH keys. It could take up to a minute for the SSH keys to update in your containers.

.. code-block:: bash

    gigalixir add_ssh_key "ssh-rsa <REDACTED> foo@gigalixir.com"

To view your SSH keys

.. code-block:: bash

    gigalixir ssh_keys

To delete an SSH key, find the key's id and then run delete the key by id.

.. code-block:: bash

    gigalixir delete_ssh_key 1

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

We currently do not have a way to view usage or your bill so far in the middle of the month, but we are working on it. For more information about how your bill is calculated, see :ref:`pricing`.


How to Restart an App
=====================

Currently, restarts will cause brief downtime as we restart all containers at once. To avoid downtime, consider doing a hot upgrade instead. See, :ref:`hot-upgrade`. We are working on adding health checks so we can do rolling restarts with no downtime.

.. code-block:: bash

    gigalixir restart $APP_NAME

.. _`jobs`:

How to Run Jobs
===============

There are many ways to run one-off jobs and tasks with Distillery. The approach described here uses Distillery's :bash:`command` command. As an alternative, you can also `drop into a remote console`_ and run code manually or use Distillery's custom commands, eval command, rpc command, pre-start hooks, and probably others.

To run one-off jobs like migrations and scripts, you'll need to write an Elixir function within your app somewhere, for example, :bash:`lib/tasks.ex` maybe. GIGALIXIR uses Distillery's :bash:`command` command to run your task.

.. code-block:: bash

    gigalixir run $APP_NAME $MODULE $FUNCTION


For example, the following command will run the :elixir:`Tasks.migrate/0` function.

.. code-block:: bash

    gigalixir run myapp Elixir.Tasks migrate

For an example task, see `gigalixir-getting-started's migrate task`_. The task is not run on the same node that your app is running in. We start a separate container to run the job so if you need any applications started such as your :elixir:`Repo`, use :elixir:`Application.ensure_all_started/2`. Also, be sure to stop all applications when done, otherwise your job will never complete and just hang until it times out. Jobs are currently killed after 5 minutes. For more information about running migrations with Distillery, see `Distillery's Running Migrations`_. Distillery commands currently do not support passing arguments into the job. 

We prepend :elixir:`Elixir.` to your module name to let the BEAM virtual machine know that you want to run an Elixir module rather than an Erlang module. The BEAM doesn't know the difference between Elixir code and Erlang code once it is compiled down, but compiled Elixir code is namespaced under the Elixir module.

The size of the container that runs your job will be the same size as the app containers and billed the same way, based on replica-size-seconds. See, :ref:`pricing`.

.. _`gigalixir-getting-started's migrate task`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/lib/tasks.ex
.. _`Distillery's Running Migrations`: https://hexdocs.pm/distillery/running-migrations.html

How to Reset your API Key
=========================

If you lost your API key or it has been stolen, you can reset it by running

.. code-block:: bash

    gigalixir reset_api_key

Your old API key will no longer work and you may have to login again.

How to Log Out
==============

.. code-block:: bash

    gigalixir logout

How to Log In
=============

.. code-block:: bash

    gigalixir login

This modifies your ~/.netrc file so that future API requests will be authenticated. API keys expire after 365 days, but if you login again, you will automatically receive an we API key.

.. _`connect-database`:

How to Connect a Database
=========================

Connecting to a database is done no differently from apps running outside GIGALIXIR. We recommend you set a DATABASE_URL config and configure your database adapter accordingly to read from that variable. In short, you'll want to add something like this to your :bash:`prod.exs` file.

.. code-block:: elixir

     config :gigalixir_getting_started, GigalixirGettingStarted.Repo,
       adapter: Ecto.Adapters.Postgres,
       url: {:system, "DATABASE_URL"},
       pool_size: 20

Replace :elixir:`:gigalixir_getting_started` and :elixir:`GigalixirGettingStarted` with your app name. Then, be sure to set your :bash:`DATABASE_URL` config with something like this.  For more information on setting configs, see :ref:`configs`.

.. code-block:: bash

    gigalixir set_config $APP_NAME DATABASE_URL "ecto://user:pass@host:port/db"

Note that if you started by cloning the `gigialixir-getting-started`_ repo, you'll have to uncomment a line in your :ref:`lib/gigalixir-getting-started.ex` file that looks like this.

.. code-block:: elixir

    # supervisor(GigalixirGettingStarted.Repo, []),

We commented this line out by default in order to disable database connection attempts before the database is configured. If you had followed the `quick start`_ without setting a :bash:`DATABASE_URL`, then the app won't start up properly. 

GIGALIXIR does not currently provide Databases-as-a-Service, but we are working on it. In the meantime, we recommend `Amazon Relational Database Service`_ or `Google Cloud SQL`_. We currently host your apps in Google Cloud Platform's us-central1 region so you'll likely get the best latency using Google Cloud SQL in the us-central1 region. Google Cloud SQL `supports PostgreSQL`_, but it is still in beta. To use MySQL, follow the `Phoenix Using MySQL Guide`_.

.. _`supports PostgreSQL`: https://cloud.google.com/sql/docs/postgres/
.. _`Phoenix Using MySQL Guide`: http://www.phoenixframework.org/docs/using-mysql
.. _`Amazon Relational Database Service`: https://aws.amazon.com/rds/
.. _`Google Cloud SQL`: https://cloud.google.com/sql/docs/
.. _`gigalixir-getting-started`: https://github.com/gigalixir/gigalixir-getting-started
.. _`lib/gigalixir-getting-started.ex`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/lib/gigalixir_getting_started.ex#L14

.. _`migrations`:

How to Run Migrations
=====================

Migrations are the same as any other job you might run. For information on running jobs, see :ref:`jobs`. In short, prepare a function to run the migration and execute the function by running

.. code-block:: bash

    gigalixir run $APP_NAME $MODULE $FUNCTION

.. _`Launching a remote console`: 
.. _`drop into a remote console`: 

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

To see how many replicas are actually running in production compared to how many are desired, run

.. code-block:: bash

    gigalixir status $APP_NAME

How to Launch a Remote Observer
===============================

To launch observer and connect it to a production node

.. code-block:: bash

    gigalixir observer $APP_NAME

and follow the instructions. This connects to a random container. We don't currently allow you to specify which container you want to connect to.

.. _`money back guarantee`:

Money-back Guarantee
====================

If you are unhappy for any reason within the first 31 days, contact us to get a refund up to $75. Enough to run a 3 node cluster for 31 days.

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
.. _`Herokuish`: https://github.com/gliderlabs/herokuish
.. _`gigalixir-getting-started`: https://github.com/gigalixir/gigalixir-getting-started
