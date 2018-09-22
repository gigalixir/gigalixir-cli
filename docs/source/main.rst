What is Gigalixir?
==================

`Gigalixir`_ is a fully-featured, production-stable platform-as-a-service built just for Elixir that saves you money and unlocks the full power of Elixir and Phoenix without forcing you to build production infrastructure or deal with maintenance and operations. For more information, see https://gigalixir.com.

Try Gigalixir for free without a credit card by following the :ref:`quick start`.

Screencast
==========

For those of you who prefer a screencast introduction. `Elixircasts.io <https://elixircasts.io>`_ has a great video that they've generously allowed us to embed here.

.. raw:: html

    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; height: auto; margin-bottom: 20px;">
        <iframe src="https://player.vimeo.com/video/288082873" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
    </div>



.. _`quick start`:

Getting Started Guide
=====================

The goal of this guide is to get your app up and running on Gigalixir. You will sign up for an account, prepare your app, deploy, and provision a database. 

If you're deploying an open source project, we provide consulting services free of charge. `Contact us`_ and we'll send you a pull request with everything you need to get started. 

Prequisites
-----------

.. role:: elixir(code)
    :language: elixir

.. role:: bash(code)
    :language: bash

#. :bash:`python2.7`, not :bash:`python3`. Most OSes already have this installed.
#. :bash:`pip`. For help, take a look at the `pip documentation`_. 
#. :bash:`git`. For help, take a look at the `git documentation`_.
#. Linux or OS X. 

For example, on Ubuntu, run

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install -y python python-pip git-core curl

.. _`buildpack configuration file`: https://github.com/HashNuke/heroku-buildpack-elixir#configuration
.. _`beta sign up form`: https://docs.google.com/forms/d/e/1FAIpQLSdB1Uh1mGQHqIIX7puoZvwm9L93bR88cM1uGeSOCXh06_smVg/viewform
.. _`gigalixir-getting-started-phx-1-3-rc-2`: https://github.com/gigalixir/gigalixir-getting-started-phx-1-3-rc-2

.. _`install the CLI`:

Install the Command-Line Interface
----------------------------------

Next install, the command-line interface. Gigalixir has a web interface at https://gigalixir.com/#/dashboard, but you will still need the CLI to do anything other than signup, deploy, and scale. 

.. code-block:: bash

    sudo pip install gigalixir --ignore-installed six

Verify by running

.. code-block:: bash

    gigalixir --help

The reason we ignore six is because OS X has a pre-installed version of six that is incompatible. When pip tries to upgrade it, OS X won't let us. For more, see https://github.com/pypa/pip/issues/3165

Create an Account
-----------------

If you already have an account, skip this step.

|signup details|

.. code-block:: bash

    gigalixir signup


Log In
------

Next, log in. This will grant you an api key which expires in 365 days. It will also optionally modify your ~/.netrc file so that all future commands are authenticated.

.. code-block:: bash

    gigalixir login 

Verify by running

.. code-block:: bash

    gigalixir account

Prepare Your App
----------------

If you have an existing app or want to use :bash:`mix phx.new`, follow the steps in :ref:`modifying existing app`. If you are starting a project from scratch, the easiest way to get started is to clone the `gigalixir-getting-started`_ repo.

.. code-block:: bash

    git clone https://github.com/gigalixir/gigalixir-getting-started.git


.. _`set up deploys`:

Set Up App for Deploys
----------------------

|set up app for deploys|

.. code-block:: bash

    cd gigalixir-getting-started
    APP_NAME=$(gigalixir create)

Verify that the app was created, by running

.. code-block:: bash

    gigalixir apps

Verify that a git remote was created by running

.. code-block:: bash

    git remote -v

Deploy!
-------

Finally, build and deploy.

.. code-block:: bash

    git push gigalixir master

Wait a minute or two since this is the first deploy, then verify by running

.. code-block:: bash

    curl https://$APP_NAME.gigalixirapp.com/

Provision a Database
--------------------

Your app does not have a database yet, let's create one.

.. code-block:: bash

    gigalixir pg:create --free 

Verify by running

.. code-block:: bash

    gigalixir pg 

Once the database is created, verify your configuration includes a :bash:`DATABASE_URL` by running

.. code-block:: bash

    gigalixir config
    

What's Next?
------------

- :ref:`logging`
- :ref:`configs`
- :ref:`scale`
- :ref:`restart`
- :ref:`rollback`
- :ref:`migrations`
- :ref:`remote console`
- :ref:`remote observer`
- :ref:`hot-upgrade`

.. _`make your existing app work on Gigalixir`:
.. _`modifying existing app`:

Modifying an Existing App to Run on Gigalixir
=============================================

Whether you have an existing app or you just ran :bash:`mix phx.new`, the goal of this guide is to get your app ready for deployment on Gigalixir. We assume that you are using Phoenix here. If you aren't feel free to `contact us`_ for help. As long as your app is serving HTTP traffic on :bash:`$PORT`, you should be fine.

Important: Although Gigalixir works with all versions of Phoenix, these guides assume you are running Phoenix 1.3. If you need help with Phoenix 1.2, please `contact us`_. The :bash:`prod.exs` can be tricky.

Important: If you have an umbrella app, be sure to *also* see :ref:`umbrella`.

Mix vs Distillery
-----------------

It's typically recommended to use distillery when you're ready to deploy, but if you prefer, you can also just use mix which you're probably already used to from development. Deploying with mix is simpler and easier, but you can't do hot upgrades, clustering, remote observer, and maybe a few other things. 

On the other hand, if you deploy with distillery, you no longer get mix tasks like :bash:`mix ecto.migrate` and configuring your :bash:`prod.exs` can be more confusing in some cases. 

If you don't know which to choose, we generally recommend going with distillery because.. why use elixir if you can't use all its amazing features? Also, Gigalixir works hard to make things easy with distillery. For example, we have a special command, :bash:`gigalixir ps:migrate`, that makes it easy to run migrations without mix. 

If you choose mix, see :ref:`modifying existing app with mix`.

If you choose distillery, see :ref:`modifying existing app with distillery`.

.. _`modifying existing app with mix`:

Using Mix
---------

For an example app that uses mix and works on gigalixir, see https://github.com/gigalixir/gigalixir-getting-started/tree/js/mix

Configuration and Secrets
^^^^^^^^^^^^^^^^^^^^^^^^^

By default, Phoenix creates a :bash:`prod.secret.exs` file to store secrets. If you want to continue using :bash:`prod.secret.exs` you'll have to commit it to version control. This is usually not a good idea, though. 

Gigalixir prefers that you use environment variables for secrets and configuration. To do this, you'll want to delete your :bash:`prod.secret.exs` file, move the contents to your :bash:`config/prod.exs` file, and modify the values to pull from environment variables. 

Open your :bash:`config/prod.exs` file and delete the following line if it is there

.. code-block:: elixir

    import_config "prod.secret.exs"

Then add something like the following in :bash:`prod.exs`

.. code-block:: elixir

     config :gigalixir_getting_started, GigalixirGettingStartedWeb.Endpoint,
       secret_key_base: Map.fetch!(System.get_env(), "SECRET_KEY_BASE"),
       server: true
 
     config :gigalixir_getting_started, GigalixirGettingStarted.Repo,
       adapter: Ecto.Adapters.Postgres,
       url: System.get_env("DATABASE_URL"),
       ssl: true,
       pool_size: 1 # Free tier db only allows 2 connections. Rolling deploys need n+1 connections. Also, save one for psql, jobs, etc.

1. Replace :elixir:`:gigalixir_getting_started` with your app name e.g. :elixir:`:my_app`
2. Replace :elixir:`GigalixirGettingStartedWeb.Endpoint` with your endpoint module name. You can find your endpoint module name by running something like 

   .. code-block:: bash

     grep -R "defmodule.*Endpoint" lib/
     
   Phoenix 1.2 and 1.3 give different names so this is a common source of errors.
3. Replace :elixir:`GigalixirGettingStarted.Repo` with your repo module name e.g. :elixir:`MyApp.Repo`
   
You don't have to worry about setting your :bash:`SECRET_KEY_BASE` config because we generate one and set it for you. If you don't use a gigalixir managed postgres database, you'll have to set the :bash:`DATABASE_URL` yourself. You can do this by running the following, but you'll need to :ref:`install the CLI` and login. For more information on setting configs, see :ref:`configs`.

.. code-block:: bash

    gigalixir config:set DATABASE_URL="ecto://user:pass@host:port/db"

Verify
^^^^^^

Let's make sure everything works. 

.. code-block:: bash

    SECRET_KEY_BASE="$(mix phx.gen.secret)" MIX_ENV=prod DATABASE_URL="postgresql://user:pass@localhost:5432/foo" PORT=4000 mix phx.server

Check it out.

.. code-block:: bash

    curl localhost:4000

If everything works, continue to :ref:`set up deploys`.

Specify Buildpacks (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We rely on buildpacks to compile and build your release. We auto-detect a variety of buildpacks so you probably don't need this, but if you want
to specify your own buildpacks create a :bash:`.buildpacks` file with the buildpacks you want. For example,

.. code-block:: bash

    https://github.com/gigalixir/gigalixir-buildpack-clean-cache.git
    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-mix.git

If you *really* want, the :bash:`gigalixir-buildpack-clean-cache` is optional if you know you will never want to clean your Gigalixir build cache. Also, :bash:`heroku-buildpack-phoenix-static` is optional if you do not have phoenix static assets. For more information about buildpacks, see :ref:`life of a deploy`.

Note, that the command that gets run in production depends on what your last buildpack is.

- If the last buildpack is :bash:`gigalixir-buildpack-mix`, then the command run will be something like :bash:`elixir --name $MY_NODE_NAME --cookie $MY_COOKIE -S mix phx.server`.
- If the last buildpack is :bash:`heroku-buildpack-phoenix-static`, then the command run will be :bash:`mix phx.server`.
- If the last buildpack is :bash:`heroku-buildpack-elixir`, then the command run will be :bash:`mix run --no-halt`. 

If your command is :bash:`mix run --no-halt`, but you are running phoenix (just not the assets pipeline), make sure you set :elixir:`server: true` in :bash:`prod.exs`.

We highly recommend keeping :bash:`gigalixir-buildpack-mix` last so that your node name and cookie are set properly. Without those, remote_console, ps:migrate, observer, etc won't work.

.. _`modifying existing app with distillery`:

Using Distillery
----------------

For an example app that uses distillery and works on gigalixir, see https://github.com/gigalixir/gigalixir-getting-started

Install Distillery to Build Releases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Distillery is currently the only supported release tool. We assume you have followed the `Distillery installation instructions`_. We use Distillery instead of bundling up your source code to support hot upgrades. 

In short, you'll need to add something like this to the :elixir:`deps` list in :bash:`mix.exs`

.. code-block:: elixir

    {:distillery, "~> 1.0.0"}

Note: Distillery 2.0 will also work and we've done our best to test it thoroughly on gigalixir, but it's pretty new so there may still be some rough edges.

Then, run

.. code-block:: bash

    mix deps.get
    mix release.init

.. _`Distillery installation instructions`: https://hexdocs.pm/distillery/getting-started.html#installation-setup

Configuration and Secrets
^^^^^^^^^^^^^^^^^^^^^^^^^

By default, Phoenix creates a :bash:`prod.secret.exs` file to store secrets. If you want to continue using :bash:`prod.secret.exs` you'll have to commit it to version control so we can bundle it into your release. This is usually not a good idea, though. 

Gigalixir prefers that you use environment variables for secrets and configuration. To do this, you'll want to delete your :bash:`prod.secret.exs` file, move the contents to your :bash:`config/prod.exs` file, and modify the values to pull from environment variables. 

Open your :bash:`config/prod.exs` file and delete the following line if it is there

.. code-block:: elixir

    import_config "prod.secret.exs"

Then add something like the following in :bash:`prod.exs`

.. code-block:: elixir

     config :gigalixir_getting_started, GigalixirGettingStartedWeb.Endpoint,
       load_from_system_env: true,
       # http: [port: {:system, "PORT"}], # Uncomment this line if you are running Phoenix 1.2
       server: true, # Without this line, your app will not start the web server!
       secret_key_base: "${SECRET_KEY_BASE}",
       url: [host: "example.com", port: 80],
       cache_static_manifest: "priv/static/cache_manifest.json"
 
     config :gigalixir_getting_started, GigalixirGettingStarted.Repo,
       adapter: Ecto.Adapters.Postgres,
       url: "${DATABASE_URL}",
       database: "",
       ssl: true,
       pool_size: 1 # Free tier db only allows 2 connections. Rolling deploys need n+1 connections. Also, save one for psql, jobs, etc.

:elixir:`server: true` **is very important and is commonly left out. Make sure you have this line.**

1. Replace :elixir:`:gigalixir_getting_started` with your app name e.g. :elixir:`:my_app`
2. Replace :elixir:`GigalixirGettingStartedWeb.Endpoint` with your endpoint module name. You can find your endpoint module name by running something like 

   .. code-block:: bash

     grep -R "defmodule.*Endpoint" lib/
     
   Phoenix 1.2 and 1.3 give different names so this is a common source of errors.
3. Replace :elixir:`GigalixirGettingStarted.Repo` with your repo module name e.g. :elixir:`MyApp.Repo`
   
You don't have to worry about setting your :bash:`SECRET_KEY_BASE` config because we generate one and set it for you. If you don't use a gigalixir managed postgres database, you'll have to set the :bash:`DATABASE_URL` yourself. You can do this by running the following, but you'll need to :ref:`install the CLI` and login. For more information on setting configs, see :ref:`configs`.

.. code-block:: bash

    gigalixir config:set DATABASE_URL="ecto://user:pass@host:port/db"

Verify
^^^^^^

Let's make sure everything works. 

First, try generating building static assets

.. code-block:: bash

    mix deps.get

    # generate static assets
    cd assets
    npm install
    node_modules/brunch/bin/brunch build --production
    cd ..
    mix phx.digest

and building a Distillery release locally

.. code-block:: bash

    MIX_ENV=prod mix release --env=prod

and running it locally

.. code-block:: bash

    MIX_ENV=prod SECRET_KEY_BASE="$(mix phx.gen.secret)" DATABASE_URL="postgresql://user:pass@localhost:5432/foo" MY_HOSTNAME=example.com MY_COOKIE=secret REPLACE_OS_VARS=true MY_NODE_NAME=foo@127.0.0.1 PORT=4000 _build/prod/rel/gigalixir_getting_started/bin/gigalixir_getting_started foreground


Don't forget to replace :bash:`gigalixir_getting_started` with your own app name. Also, change/add the environment variables as needed.

Check it out.

.. code-block:: bash

    curl localhost:4000

If that didn't work, the first place to check is :bash:`prod.exs`. Make sure you have :elixir:`server: true` somewhere and there are no typos.

Also check out :ref:`troubleshooting`.

If it still doesn't work, don't hesitate to `contact us`_.

If everything works, continue to :ref:`set up deploys`.

.. _`buildpacks`:

Specify Buildpacks (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We rely on buildpacks to compile and build your release. We auto-detect a variety of buildpacks so you probably don't need this, but if you want
to specify your own buildpacks create a :bash:`.buildpacks` file with the buildpacks you want. For example,

.. code-block:: bash

    https://github.com/gigalixir/gigalixir-buildpack-clean-cache.git
    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-distillery.git

If you *really* want, the :bash:`gigalixir-buildpack-clean-cache` is optional if you know you will never want to clean your Gigalixir build cache. Also, :bash:`heroku-buildpack-phoenix-static` is optional if you do not have phoenix static assets. For more information about buildpacks, see :ref:`life of a deploy`.

Note, that the command that gets run in production depends on what your last buildpack is.

- If the last buildpack is :bash:`gigalixir-buildpack-distillery`, then the command run will be :bash:`/app/bin/foo foreground`.
- If the last buildpack is :bash:`heroku-buildpack-phoenix-static`, then the command run will be :bash:`mix phx.server`.
- If the last buildpack is :bash:`heroku-buildpack-elixir`, then the command run will be :bash:`mix run --no-halt`. 

If your command is :bash:`mix run --no-halt`, but you are running phoenix (just not the assets pipeline), make sure you set :elixir:`server: true` in :bash:`prod.exs`.

Set up Node Clustering with Libcluster (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to cluster nodes, you should install libcluster. For more information about installing libcluster, see :ref:`cluster your nodes`.

.. _`Mix`: https://hexdocs.pm/mix/Mix.html

Set Up Hot Upgrades with Git v2.9.0
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run hot upgrades, you send an extra http header when running :bash:`git push gigalixir master`. Extra HTTP headers are only supported in git 2.9.0 and above so make sure you upgrade if needed. For information on how to install the latest version of git on Ubuntu, see `this stackoverflow question <http://stackoverflow.com/questions/19109542/installing-latest-version-of-git-in-ubuntu>`_. For information on running hot upgrades, see :ref:`hot-upgrade` and :ref:`life-of-a-hot-upgrade`.

How Does Gigalixir Work?
========================

When you deploy an app on Gigalixir, you :bash:`git push` the source code to a build server. The build server compiles the code and assets and generates a standalone tarball we call a slug. The controller then combines the slug and your app configuration into a release. The release is deployed to run containers which actually run your app.

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
  - *Command-Line Interface*: This is the command-line tool that runs on your local machine that you use to control Gigalixir.

Concepts
--------

  - *User*: The user is you. When you sign up, we create a user.
  - *API Key*: Every user has an API Key which is used to authenticate most API requests. You get one when you login and you can regenerate it at any time. It expires every 365 days.
  - *SSH Key*: SSH keys are what we use to authenticate you when SSHing to your containers. We use them for remote observer, remote console, etc.
  - *App*: An app is your Elixir application.
  - *Release*: A release is a combination of a slug and a config which is deployed to a run container.
  - *Slug*: Each app is compiled and built into a slug. The slug is the actual code that is run in your containers. Each app will have many slugs, one for every deploy.
  - *Config*: A config is a set of key-value pairs that you use to configure your app. They are injected into your run container as environment variables.
  - *Replicas*: An app can have many replicas. A replica is a single instance of your app in a single container in a single pod.
  - *Custom Domain*: A custom domain is a fully qualified domain that you control which you can set up to point to your app.
  - *Payment Method*: Your payment method is the credit card on file you use to pay your bill each month.
  - *Permission*: A permission grants another user the ability to deploy. Even though they can deploy, you remain the owner and are responsible for paying the bill.

.. _`life of a deploy`:

Life of a Deploy
----------------

When you run :bash:`git push gigalixir master`, our git server receives your source code and kicks off a build using a pre-receive hook. We build your app in an isolated docker container which ultimately produces a slug which we store for later. The buildpacks used are defined in your :bash:`.buildpacks` file.

By default, the buildpacks we use include

  - https://github.com/gigalixir/gigalixir-buildpack-clean-cache.git

    - To clean the cache if enabled.

  - https://github.com/HashNuke/heroku-buildpack-elixir.git

    - To run mix compile
    - If you want, you can `configure this buildpack <https://github.com/HashNuke/heroku-buildpack-elixir#configuration>`_.

  - https://github.com/gjaldon/heroku-buildpack-phoenix-static.git

    - To run mix phx.digest
    - This is only included if you have an assets folder present.

  - https://github.com/gigalixir/gigalixir-buildpack-distillery.git

    - To run mix release
    - This is only run if you have a rel/config.exs file present.

  - https://github.com/gigalixir/gigalixir-buildpack-mix.git

    - To set up your Procfile correctly
    - This is only run if you *don't* have a rel/config.exs file present.

We only build the master branch and ignore other branches. When building, we cache compiled files and dependencies so you do not have to repeat the work on every deploy. We support git submodules. 

Once your slug is built, we upload it to slug storage and we combine it with a config to create a new release for your app. The release is tagged with a :bash:`version` number which you can use later on if you need to rollback to this release. 

Then we create or update your Kubernetes configuration to deploy the app. We create a separate Kubernetes namespace for every app, a service account, an ingress for HTTP traffic, an ingress for SSH traffic, a TLS certificate, a service, and finally a deployment which creates pods and containers. 

The `container that runs your app`_ is a derivative of `heroku/cedar:14`_. The entrypoint is a script that sets up necessary environment variables including those from your `app configuration`_. It also starts an SSH server, installs your SSH keys, downloads the current slug, and executes it. We automatically generate and set up your erlang cookie, distributed node name, and phoenix secret key base for you. We also set up the Kubernetes permissions and libcluster selector you need to `cluster your nodes`_. We poll for your SSH keys every minute in case they have changed.

At this point, your app is running. The Kubernetes ingress controller is routing traffic from your host to the appropriate pods and terminating SSL/TLS for you automatically. For more information about how SSL/TLS works, see :ref:`how-tls-works`.

If at any point, the deploy fails, we rollback to the last known good release.

To see how we do zero-downtime deploys, see :ref:`zero-downtime`.

.. _how-tls-works:

How SSL/TLS Works
-----------------

We use kube-lego for automatic TLS certificate generation with Let's Encrypt. For more information, see `kube-lego's documentation`_. When you add a custom domain, we create a Kubernetes ingress for you to route traffic to your app. kube-lego picks this up, obtains certificates for you and installs them. Our ingress controller then handles terminating SSL traffic before sending it to your app.

.. _`kube-lego's documentation`: https://github.com/jetstack/kube-lego

.. _life-of-a-hot-upgrade:

Life of a Hot Upgrade
---------------------

There is an extra flag you can pass to deploy by hot upgrade instead of a restart. You have to make sure you bump your app version in your :bash:`mix.exs`. Distillery autogenerates your appup file, but you can supply a custom appup file if you need it. For more information, look at the `Distillery appup documentation`_.

.. code-block:: bash

    git -c http.extraheader="GIGALIXIR-HOT: true" push gigalixir master

A hot upgrade follows the same steps as a regular deploy, except for a few differences. In order for distillery to build an upgrade, it needs access to your old app so we download it and make it available in the build container. 

Once the slug is generated and uploaded, we execute an upgrade script on each run container instead of restarting. The upgrade script downloads the new slug, and calls `Distillery's upgrade command`_. Your app should now be upgraded in place without any downtime, dropped connections, or loss of in-memory state.

.. _`configure versions`:

How to clean your build cache
=============================

There is an extra flag you can pass to clean your cache before building in case you need it, but you need git 2.9.0 or higher for it to work. For information on how to install the latest version of git on Ubuntu, see `this stackoverflow question <http://stackoverflow.com/questions/19109542/installing-latest-version-of-git-in-ubuntu>`_.

.. code-block:: bash

    git -c http.extraheader="GIGALIXIR-CLEAN: true" push gigalixir master

Known Issues
============

  -  Warning: Multiple default buildpacks reported the ability to handle this app. The first buildpack in the list below will be used.

      - This warning is safe to ignore. It is a temporary warning due to a workaround. 

  - curl: (56) GnuTLS recv error (-110): The TLS connection was non-properly terminated.

      - Currently, the load balancer for domains under gigalixirapp.com has a request timeout of 30 seconds. If your request takes longer than 30 seconds to respond, the load balancer cuts the connection. Often, the cryptic error message you will see when using curl is the above. The load balancer for custom domains does not have this problem.

Can I run my app in AWS instead of Google Cloud Platform?
=========================================================

Yes, we currently support GCP us-central1 and GCP europe-west1 as well as AWS us-east-1 and AWS us-west-2. When creating your app with :bash:`gigalixir create` simply specify the :bash:`--cloud=aws` and :bash:`--region=us-east-1` options.

Can I use a custom Procfile?
============================

Definitely! If you have a :bash:`Procfile` at the root of your repo, we'll use it instead of `the default one <https://github.com/gigalixir/gigalixir-run/blob/master/Procfile>`_.

The only gotcha is that if you want remote console to work, you'll want to make sure the node name and cookie are set properly. For example, your :bash:`Procfile` should look something like this.

.. code-block:: bash

  web: elixir --name $MY_NODE_NAME --cookie $MY_COOKIE -S mix phoenix.server

How do I specify my Elixir, Erlang, Node, NPM, etc versions?
============================================================

Your Elixir and Erlang versions are handled by the heroku-buildpack-elixir buildpack. To configure, see the `heroku-buildpack-elixir configuration`_. In short, you specify them in a :bash:`elixir_buildpack.config` file.

Node and NPM versions are handled by the heroku-buildpack-phoenix-static buildpack. To configure, see the `heroku-buildpack-phoenix-static configuration`_. In short, you specify them in a :bash:`phoenix_static_buildpack.config` file.

.. _`heroku-buildpack-elixir configuration`: https://github.com/HashNuke/heroku-buildpack-elixir#configuration

How do I specify which buildpacks I want to use?
================================================

Normally, the buildpack you need is auto-detected for you, but in some cases, you may want to specify which buildpacks you want to use. To do this, create a :bash:`.buildpacks` file and list each buildpack you want to use. For example, the default buildpacks for elixir apps using distillery would look like this

.. code-block:: bash

    https://github.com/gigalixir/gigalixir-buildpack-clean-cache.git
    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-distillery.git


The default buildpacks for elixir apps running mix looks like this

.. code-block:: bash

    https://github.com/gigalixir/gigalixir-buildpack-clean-cache.git
    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-mix.git

Note the last buildpack. It's there to make sure your :bash:`Procfile` is set up correctly to run on gigalixir. It basically makes sure you have your node name and cookie set correctly so that remote console, migrate, observer, etc will work.

.. _`umbrella`:

How do I deploy an umbrella app?
================================

Umbrella apps are deployed the same way, but the buildpacks need to know which internal app is your phoenix app. Set your :bash:`phoenix_relative_path` in your :bash:`phoenix_static_buildpack.config` file, see the `heroku-buildpack-phoenix-static configuration`_ for more details.

When running migrations, we need to know which internal app contains your migrations. Use the :bash:`--migration_app_name` flag on :bash:`gigalixir ps:migrate`.

If you have multiple Distillery releases in your :bash:`rel/config.exs` file, be sure to set your default release to the one you want to deploy. See :ref:`gigalixir release options`.

.. _`heroku-buildpack-phoenix-static configuration`: https://github.com/gjaldon/heroku-buildpack-phoenix-static#configuration

Can I deploy an app that isn't at the root of my repository?
============================================================

If you just want to push a subtree, try 

.. code-block:: bash

    git subtree push --prefix my-sub-folder gigalixir master

If you want to push the entire repo, but run the app from a subfolder, it becomes a bit trickier, but this pull request should help you.
https://github.com/jesseshieh/nonroot/pull/1/files

Frequently Asked Questions
==========================

*What versions of Phoenix do you support?*
------------------------------------------

All versions.

*What versions of Elixir and OTP do you support?*
-------------------------------------------------

All versions of Elixir and OTP. See :ref:`configure versions`. Some buildpacks don't have the bleeding edge versions so those might not work, but they will eventually.

*Can I have multiple custom domains?*

Yes! Just follow :ref:`custom domains` for each domain.

*Do you support non-Elixir apps?*
---------------------------------

Yes, we support any language that has a buildpack, but hot upgrades, remote observer, etc probably won't work. Built-in buildpacks include

- multi
- ruby
- nodejs
- clojure
- python
- java
- gradle
- scala
- play
- php
- go
- erlang
- static

For details, see https://github.com/gliderlabs/herokuish/tree/v0.3.36/buildpacks

If the buildpack you need is not built-in, you can specify the buildpack(s) you want by listing them in a :bash:`.buildpacks` file.

For an example, see `How to deploy a Ruby app`_.

*What is Elixir? What is Phoenix?*
----------------------------------

This is probably best answered by taking a look at the `elixir homepage`_ and the `phoenix homepage`_.

*How is Gigalixir different from Heroku and Deis Workflow?*
-----------------------------------------------------------

For a feature comparison table between Gigalixir and Heroku see, :ref:`gigalixir heroku feature comparison`.

.. image:: venn.png

Heroku is a really great platform and much of Gigalixir was designed based on their excellent `twelve-factor methodology`_. Heroku and Gigalixir are similar in that they both try to make deployment and operations as simple as possible. Elixir applications, however, aren't very much like most other apps today written in Ruby, Python, Java, etc. Elixir apps are distributed, highly-available, hot-upgradeable, and often use lots of concurrent long-lived connections. Gigalixir made many fundamental design choices that ensure all these things are possible.

For example, Heroku restarts your app every 24 hours regardless of if it is healthy or not. Elixir apps are designed to be long-lived and many use in-memory state so restarting every 24 hours sort of kills that. Heroku also limits the number of concurrent connections you can have. It also has limits to how long these connections can live. Heroku isolates each instance of your app so they cannot communicate with each other, which prevents node clustering. Heroku also restricts SSH access to your containers which makes it impossible to do hot upgrades, remote consoles, remote observers, production tracing, and a bunch of other things. The list goes on, but suffice it to say, running an Elixir app on Heroku forces you to give up a lot of the features that drew you to Elixir in the first place.

Deis Workflow is also really great platform and is very similar to Heroku, except you run it your own infrastructure. Because Deis is open source and runs on Kubernetes, you *could* make modifications to support node clustering and remote observer, but they won't work out of the box and hot upgrades would require some fundamental changes to the way Deis was designed to work. Even so, you'd still have to spend a lot of time solving problems that Gigalixir has already figured out for you.

On the other hand, Heroku and Deis are more mature products that have been around much longer. They have more features, but we are working hard to fill in the holes. Heroku and Deis also support languages other than Elixir.

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

*What if Gigalixir shuts down?*
-------------------------------

Gigalixir is running profitably and has plenty of funding. There is no reason to think Gigalixir will shut down.

*My git push was rejected*
--------------------------

Try force pushing with

.. code-block:: bash

    git push -f gigalixir master

.. _`cluster your nodes`:
.. _`clustering`:

Clustering Nodes
================

We use libcluster to manage node clustering. For more information, see `libcluster's documentation`_. 

To install libcluster, add this to the deps list in :bash:`mix.exs`

.. code-block:: elixir

    {:libcluster, "~> 2.0.3"}

If you are on Elixir 1.3 or lower, add :elixir`:libcluster` and :elixir:`:ssl` to your applications list. Elixir 1.4 and up detect your applications list for you.

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

Gigalixir handles permissions so that you have access to Kubernetes endpoints and we automatically set your node name and erlang cookie so that your nodes can reach each other. We don't firewall each container from each other like Heroku does. We also automatically set the environment variables :bash:`LIBCLUSTER_KUBERNETES_SELECTOR`, :bash:`LIBCLUSTER_KUBERNETES_NODE_BASENAME`, :bash:`APP_NAME`, and :bash:`MY_POD_IP` for you. See `gigalixir-run`_ for more details. 

.. _`libcluster's documentation`: https://github.com/bitwalker/libcluster
.. _`gigalixir-getting-started's vm.args file`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/rel/vm.args
.. _`gigalixir-getting-started's prod.exs file`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/config/prod.exs#L68
.. _`gigalixir-getting-started's mix.exs file`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/mix.exs
.. _`gigalixir-getting-started's rel/config.exs file`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/rel/config.exs#L27
.. _`gigalixir-run`: https://github.com/gigalixir/gigalixir-run

How to use a custom vm.args
===========================

Gigalixir generates a default :bash:`vm.args` file for you and tells Distillery to use it by settingthe :bash:`VMARGS_PATH` envionment variable. By default, it is set to :bash:`/release-config/vm.args`. If you want to use a custom :bash:`vm.args`, we recommend you follow these instructions.

Disable Gigalixir's default vm.args

.. code-block:: bash

    gigalixir config:set GIGALIXIR_DEFAULT_VMARGS=false

Create a :bash:`rel/vm.args` file in your repository. It might look something like `gigalixir-getting-started's vm.args file`_.

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

After a new deploy, verify by SSH'ing into your instance and inspecting your release's vm.arg file like this

.. code-block:: bash

    gigalixir ps:ssh 
    cat /app/var/vm.args

.. _`tiers`:

Tiers
=====

Gigalixir offers 2 tiers of pricing. The free tier is free, but you are limited to 1 instance up to size 0.5 and 1 free tier database. Also, on the free tier, if you haven't deployed anything for over 30 days, we will send you an email to remind you to keep your account active. If you do not, your app may be scaled down to 0 replicas. We know this isn't ideal, but we think it is better than sleeping instances and we appreciate your understanding since the free tier does cost a lot to run.

=======================  ========= =============
Instance Feature         FREE Tier STANDARD Tier
=======================  ========= =============
Zero-downtime deploys    YES       YES
Websockets               YES       YES
Automatic TLS            YES       YES
Log Aggregation          YES       YES
Log Tailing              YES       YES
Hot Upgrades             YES       YES
Remote Observer          YES       YES
No Connection Limits     YES       YES
No Daily Restarts        YES       YES
Custom Domains           YES       YES
Postgres-as-a-Service    YES       YES
SSH Access               YES       YES
Vertical Scaling                   YES
Horizontal Scaling                 YES
Clustering                         YES
Multiple Apps                      YES
Team Permissions                   YES
No Inactivity Checks               YES
=======================  ========= =============

========================  ========= =============
Database Feature          FREE Tier STANDARD Tier
========================  ========= =============
SSL Connections           YES       YES
Data Import/Export        YES       YES
Data Encryption                     YES
Dedicated CPU                       YES*
Dedicated Memory                    YES
Dedicated Disk                      YES
No Connection Limits                YES
No Row Limits                       YES
Backups                             YES
Scalable/Upgradeable                YES
Automatic Data Migration            YES
Postgres Extensions                 YES
========================  ========= =============

* Only sizes 4 and above have dedicated CPU. See :ref:`database sizes`.

.. _`gigalixir heroku feature comparison`:

Gigalixir vs Heroku Feature Comparison
======================================

=======================  =================== ======================= =========== =============== ==================
Feature                  Gigalixir FREE Tier Gigalixir STANDARD Tier Heroku Free Heroku Standard Heroku Performance
=======================  =================== ======================= =========== =============== ==================
Websockets               YES                 YES                     YES         YES             YES
Log Aggregation          YES                 YES                     YES         YES             YES
Log Tailing              YES                 YES                     YES         YES             YES
Custom Domains           YES                 YES                     YES         YES             YES
Postgres-as-a-Service    YES                 YES                     YES         YES             YES
No sleeping              YES                 YES                                 YES             YES
Automatic TLS            YES                 YES                                 YES             YES
Preboot                  YES                 YES                                 YES             YES
Zero-downtime deploys    YES                 YES
SSH Access               YES                 YES
Hot Upgrades             YES                 YES
Remote Observer          YES                 YES
No Connection Limits     YES                 YES
No Daily Restarts        YES                 YES
Flexible Instance Sizes                      YES
Clustering                                   YES
Horizontal Scaling                           YES                                 YES             YES
Built-in Metrics                                                                 YES             YES
Threshold Alerts                                                                 YES             YES
Dedicated Instances                                                                              YES
Autoscaling                                                                                      YES
=======================  =================== ======================= =========== =============== ==================

.. _`pricing`:

Pricing Details
===============

In the free tier, everything is no-credit-card free. Once you upgrade to the standard tier, you pay $10 for every 200MB of memory per month. CPU, bandwidth, and power are free. You get 1 CPU share per GB of memory. See :ref:`replica sizing` for more.

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

For database pricing, see :ref:`database sizes`.
 
.. _`replica sizing`:

Replica Sizing
==============

  - A replica is a docker container that your app runs in.
  - Replica sizes are available in increments of 0.1 between 0.2 and 16. 
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

Gigalixir is designed for Elixir/Phoenix apps and it is common for Elixir/Phoenix apps to have many connections open at a time and to have connections open for long periods of time. Because of this, we do not limit the number of concurrent connections or the duration of each connection[1][2].

We also know that Elixir/Phoenix apps are designed to be long-lived and potentially store state in-memory so we do not restart replicas arbitrarily. In fact, replicas should not restart at all, unless there is an extenuating circumstance that requires it.  For apps that require extreme high availability, we suggest that your app be able to handle node restarts just as you would for any app not running on Gigalixir.

[1] Because Gigalixir runs on Google Compute Engine, you may bump into an issue with connections that stay idle for 10m. For more information and how to work around it, see https://cloud.google.com/compute/docs/troubleshooting
[2] We do have a timeout of 60 minutes for connections after an nginx configuration reload. If you have a long-lived websocket connection and our nginx configuration is reloaded, the connection will be dropped 60 minutes later. Unfortunately, nginx reloads happen frequently under Kubernetes.

Monitoring
==========

Gigalixir doesn't provide any monitoring out of the box, but we are working on it. Also, you can always use a remote observer to inspect your node. See, :ref:`remote observer`.
 
.. _distillery-replace-os-vars:
.. _`app configuration`:

Using Environment Variables in your App
=======================================

Environment variables with Elixir, Distillery, and releases in general are one of those things that always trip up beginners. I think `Distillery's Runtime Configuration`_ explains it better than I can, but in short, never use :elixir:`System.get_env("FOO")` in your :bash:`prod.exs`. Always use :elixir:`"${FOO}"` instead. 

Gigalixir automatically sets :bash:`REPLACE_OS_VARS=true` for you so all you have to do to introduce a new :bash:`MY_CONFIG` env var is add something like this to your :bash:`config.exs` file

.. code-block:: elixir

    ...
    config :myapp,
        my_config: "${MY_CONFIG}"
    ...

Then set the :bash:`MY_CONFIG` environment variable, by running

.. code-block:: bash

    gigalixir config:set MY_CONFIG=foo

In your app code, access the environment variable using 

.. code-block:: elixir

    Application.get_env(:myapp, :my_config) == "foo"

.. _`Distillery's Runtime Configuration`: https://hexdocs.pm/distillery/runtime-configuration.html#content

.. _`troubleshooting`:

Troubleshooting
===============

If you're having trouble getting things working, you can verify a few things locally.

First, try generating and running a Distillery release locally by running

.. code-block:: bash

    mix deps.get
    MIX_ENV=prod mix release --env=prod
    DATABASE_URL="postgresql://user:pass@localhost:5432/foo" MY_HOSTNAME=example.com MY_COOKIE=secret REPLACE_OS_VARS=true MY_NODE_NAME=foo@127.0.0.1 PORT=4000 _build/prod/rel/gigalixir_getting_started/bin/gigalixir_getting_started foreground
    curl localhost:4000

Don't forget to replace :bash:`gigalixir_getting_started` with your own app name. Also, change/add the environment variables as needed.

You can safely ignore Kubernetes errors like :bash:`[libcluster:k8s_example]` errors because you probably aren't running inside Kubernetes.

If they don't work, the first place to check is :bash:`prod.exs`. Make sure you have :elixir:`server: true` somewhere and there are no typos.

In case static assets don't show up, you can try the following and then re-run the commands above.

.. code-block:: bash

    cd assets
    npm install
    node_modules/brunch/bin/brunch build --production
    cd ..
    mix phx.digest

If your problem is with one of the buildpacks, try running the full build using Docker and Herokuish by running

.. code-block:: bash

    APP_ROOT=$(pwd)
    rm -rf /tmp/gigalixir/cache
    rm -rf _build
    mkdir -p /tmp/gigalixir/cache
    docker run -it --rm -v $APP_ROOT:/tmp/app -v /tmp/gigalixir/cache/:/tmp/cache us.gcr.io/gigalixir-152404/herokuish 

Or to inspect closer, run

.. code-block:: bash

    docker run -it --rm -v $APP_ROOT:/tmp/app -v /tmp/gigalixir/cache/:/tmp/cache --entrypoint=/bin/bash us.gcr.io/gigalixir-152404/herokuish

    # and then inside the container run
    build-slug

    # inspect /app folder
    # check /tmp/cache

If the above commands still do not succeed and your app is open source, then please `contact us for help`_. If not open source, `contact us`_ anyway and we'll do our best to help you.

Common Errors
-------------

    - My deploy succeeded, but nothing happened.

        - When :bash:`git push gigalixir master` succeeds, it means your code was compiled and built without any problems, but there can still be problems during runtime. Other platforms will just let your app fail, but gigalixir performs tcp health checks on port 4000 on your new release before terminating the old release. So if your new release is failing health checks, it can appear as if nothing is happening because in a sense, nothing is. Check :bash:`gigalixir logs` for any startup errors.

    - My app takes a long time to startup.

        - Most likely, this is because your CPU reservation isn't enough and there isn't any extra CPU available on the machine to give you. Try scaling up your instance sizes. See :ref:`scale`.

    - failed to connect: ** (Postgrex.Error) FATAL 53300 (too_many_connections): too many connections for database

        - If you have a free tier database, the number of connections is limited to 1. Try lowering the :elixir:`pool_size` in your :bash:`prod.exs` to 1.

    - ~/.netrc access too permissive: access permissions must restrict access to only the owner

        - run :bash:`chmod og-rwx ~/.netrc`

    - :bash:`git push gigalixir master` asks for my password

        - First try running :bash:`gigalixir login` and try again. If that doesn't work, try resetting your git remote by running :bash:`gigalixir git:remote $APP` and trying again.

    - (File.Error) could not read file "foo/bar": no such file or directory

        - Often, this means that Distillery did not package the :bash:`foo` directory into your release tarball. Try using Distillery Overlays to add the :bash:`foo` directory. For example, adjusting your :bash:`rel/config.exs` to something like this

          .. code-block:: bash

              release :gigalixir_getting_started do
                set version: current_version(:gigalixir_getting_started)
                set applications: [
                  :runtime_tools
                ]
                set overlays: [
                  {:copy, "foo", "foo"}
                ]
              end

          For more, see https://github.com/bitwalker/distillery/blob/master/docs/Overlays.md

    - cd: /tmp/build/./assets: No such file or directory

        - This means the phoenix static buildpack could not find your assets folder. Either specify where it is or remove the buildpack. To specify, configure the buildpack following https://github.com/gjaldon/heroku-buildpack-phoenix-static. To remove, create a :bash:`.buildpacks` file with the buildpacks you need. For example, just :bash:`https://github.com/HashNuke/heroku-buildpack-elixir`

    - SMTP/Email Network Failures e.g. {:network_failure, 'smtp.mailgun.org', {:error, :timeout}}

        - Google Cloud Engine does not allow certain email ports like 587. See https://cloud.google.com/compute/docs/tutorials/sending-mail/
          Try using port 2525. See https://cloud.google.com/compute/docs/tutorials/sending-mail/using-mailgun

    - init terminating in do_boot ({cannot get bootfile,no_dot_erlang.boot})

        - This is an issue described here: https://github.com/bitwalker/distillery/issues/426
          Try either upgrading Distillery to 1.5.3 or downgrading OTP below 21.

.. _`contact us for help`:
.. _`contact us`:
.. _`help`:

Support/Help
============

Feel free to email help@gigalixir.com for any questions or issues, we generally respond within hours.

.. _`Stack Overflow`: http://stackoverflow.com/
.. _`the gigalixir tag`: http://stackoverflow.com/questions/tagged/gigalixir

The Gigalixir Command-Line Interface
====================================

The Gigalixir Command-Line Interface or CLI is a tool you install on your local machine to control Gigalixir.

How to Install the CLI
----------------------

Install :bash:`gigalixir` using 

.. code-block:: bash

    sudo pip install gigalixir --ignore-installed six

If you don't have pip installed, take a look at the `pip documentation`_.

How to Upgrade the CLI
----------------------

To upgrade the Gigalixir CLI, run

.. code-block:: bash

    sudo pip install -U gigalixir --ignore-installed six

Encryption
----------

All HTTP requests made between your machine and Gigalixir's servers are encrypted.

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

Bugs in the CLI are reported to Gigalixir's error tracking service. Currently, the only way to disable this is by modifying the source code. `Pull requests`_ are also accepted!

.. _`Pull requests`: https://github.com/gigalixir/gigalixir-cli/pulls

Open Source
-----------

The Gigalixir CLI is open source and we welcome pull requests. See `the gigalixir-cli repository`_.

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

.. _`upgrade account`:

How to Upgrade an Account
=========================

The standard tier offers much more than the free tier, see :ref:`tiers`.

The easiest way to upgrade is through the web interface. Login at https://gigalixir.com/#/signin and click the Upgrade button.

To upgrade with the CLI, first add a payment method

.. code-block:: bash

    gigalixir account:payment_method:set

Then upgrade.

.. code-block:: bash

    gigalixir account:upgrade

How to Create an App
====================

|set up app for deploys|

.. code-block:: bash

    gigalixir create 


.. _`delete-app`:

How to Delete an App
====================

WARNING!! Deleting an app can not be undone and the name can not be reused.

To delete an app, run

.. code-block:: bash

    gigalixir apps:destroy

How to Rename an App
====================

There is no way to rename an app, but you can delete it and then create a new one. Remember to migrate over your configs.

How to Deploy an App
====================

Deploying an app is done using a git push, the same way you would push code to github. For more information about how this works, see `life of a deploy`_.

.. code-block:: bash

    git push gigalixir master
 
How to Deploy a Branch
======================

To deploy a local branch, :bash:`my-branch`, run

.. code-block:: bash

    git push gigalixir my-branch:master

How to Set Up a Staging Environment
===================================

To set up a separate staging app and production app, you'll need to create another gigalixir app. To do this, first rename your current gigalixir git remote to staging.

.. code-block:: bash

    git remote rename gigalixir staging

Then create a new app for production

.. code-block:: bash

    gigalixir create 

If you like, you can also rename the new app remote.

.. code-block:: bash

    git remote rename gigalixir production

From now on, you can run this to push to staging.

.. code-block:: bash

    git push staging master

And this to push to production

.. code-block:: bash

    git push production master

You'll probably also want to check all your environment variables and make sure they are set probably for production and staging. Also, generally speaking, it's best to use :bash:`prod.exs` for both production and staging and let environment variables be the only thing that varies between the two environments. This way staging is as close a simulation of production as possible. If you need to convert any configs into environment variables use :elixir:`"${MYVAR}"`.

How to Set Up Continuous Integration (CI/CD)?
=============================================

Since deploys are just a normal :bash:`git push`, Gigalixir should work with any CI/CD tool out there. For Travis CI, put something like this in your :bash:`.travis.yml`

.. code-block:: yaml

    script:
      - git remote add gigalixir https://$GIGALIXIR_EMAIL:$GIGALIXIR_API_KEY@git.gigalixir.com/$GIGALIXIR_APP_NAME.git
      - mix test && git push -f gigalixir HEAD:refs/heads/master
    language: elixir
    elixir: 1.5.1
    otp_release: 20.0
    services:
      - postgresql
    before_script:
      - PGPASSWORD=postgres psql -c 'create database gigalixir_getting_started_test;' -U postgres

Be sure to replace :bash:`gigalixir_getting_started_test` with your test database name configured in your :bash:`test.exs` file along with your db username and password.

In the Travis CI Settings, add a :bash:`GIGALIXIR_EMAIL` environment variable, but be sure to URI encode it e.g. :bash:`foo%40gigalixir.com`. 

Add a :bash:`GIGALIXIR_API_KEY` environment variable which you can find in your :bash:`~/.netrc` file e.g. :bash:`b9fbde22-fb73-4acb-8f74-f0aa6321ebf7`. 

Finally, add a :bash:`GIGALIXIR_APP_NAME` environment variable with the name of your app e.g. :bash:`real-hasty-fruitbat`

Using GitLab CI or any other CI/CD service should be very similar. For an example GitLab CI yaml file, see this `.gitlab-ci.yml <https://github.com/gigalixir/gigalixir-getting-started/blob/master/.gitlab-ci.yml>`_ file.

If you want to automatically run migrations on each automatic deploy, you have two options

1. (Recommended) Use a Distillery pre-start boot hook by following https://github.com/bitwalker/distillery/blob/master/docs/guides/running_migrations.md and https://github.com/bitwalker/distillery/blob/master/docs/plugins/boot_hooks.md

2. Install the gigalixir CLI in your CI environment and run :bash:`gigalixir ps:migrate`. For example,

   .. code-block:: bash

       # install gigalixir-cli
       sudo apt-get install -y python-pip
       sudo pip install --upgrade setuptools
       sudo pip install gigalixir

       # deploy
       gigalixir login -e "$GIGALIXIR_EMAIL" -p "$GIGALIXIR_PASSWORD" -y
       gigalixir git:remote $GIGALIXIR_APP_NAME
       git push -f gigalixir HEAD:refs/heads/master
       # some code to wait for new release to go live

       # set up ssh so we can migrate
       mkdir ~/.ssh
       printf "Host *\n StrictHostKeyChecking no" > ~/.ssh/config
       echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa

       # migrate
       gigalixir ps:migrate -a $GIGALIXIR_APP_NAME


How to Set Up Review Apps (Feature branch apps)
===============================================

Review Apps let you run a new instance for every branch and tear them down after the branch is deleted. For GitLab CI/CD Review Apps, all you have to do is create a :bash:`.gitlab-ci.yml` file that looks something like `this one <https://github.com/gigalixir/gigalixir-getting-started/blob/master/.gitlab-ci.yml>`_.

Be sure to create CI/CD secrets for :bash:`GIGALIXIR_EMAIL`, :bash:`GIGALIXIR_PASSWORD`, and :bash:`GIGALIXIR_APP_NAME`.

For review apps run on something other than GitLab, the setup should be very similar.

How to Set the Gigalixir Git Remote
===================================

If you have a Gigalixir app already created and want to push a git repository to it, set the git remote by running

.. code-block:: bash

    gigalixir git:remote $APP_NAME

If you prefer to do it manually, run

.. code-block:: bash

    git remote add gigalixir https://git.gigalixir.com/$APP_NAME.git

.. _`scale`:

How to Scale an App
===================

You can scale your app by adding more memory and cpu to each container, also called a replica. You can also scale by adding more replicas. Both are handled by the following command. For more information, see `replica sizing`_.

.. code-block:: bash

    gigalixir ps:scale --replicas=2 --size=0.6

.. _`configs`:

How to Configure an App
=======================

All app configuration is done through envirnoment variables. You can get, set, and delete configs using the following commands. Note that setting configs does not automatically restart your app so you may need to do that yourself. We do this to give you more control at the cost of simplicity. It also potentially enables hot config updates or updating your environment variables without restarting. For more information on hot configuration, see :ref:`hot-configure`. For more information about using environment variables for app configuration, see `The Twelve-Factor App's Config Factor`_. For more information about using environment variables in your Elixir app, see :ref:`distillery-replace-os-vars`.
 
.. code-block:: bash

    gigalixir config
    gigalixir config:set FOO=bar
    gigalixir config:unset FOO                                                               

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

    git -c http.extraheader="GIGALIXIR-HOT: true" push gigalixir master
 
.. _`rollback`:

How to Rollback an App
======================

To rollback one release, run the following command. 
 
.. code-block:: bash

    gigalixir releases:rollback 

To rollback to a specific release, find the :bash:`version` by listing all releases. You can see which SHA the release was built on and when it was built. This will also automatically restart your app
with the new release.

.. code-block:: bash

    gigalixir releases 

You should see something like this

.. code-block:: bash

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

    gigalixir releases:rollback --version=5

The release list is immutable so when you rollback, we create a new release on top of the old releases, but the new release refers to the old slug. 

.. _`custom domains`:

How to Set Up a Custom Domain
=============================

After your first deploy, you can see your app by visiting https://$APP_NAME.gigalixirapp.com/, but if you want, you can point your own domain such as www.example.com to your app. To do this, run the following command and follow the instructions.

.. code-block:: bash

    gigalixir domains:add www.example.com

If you have version 0.27.0 or later of the CLI, you'll be given instructions on what to do next. If not, run :bash:`gigalixir domains` and use the :bash:`cname` value to point your domain at.

This will do a few things. It registers your fully qualified domain name in the load balancer so that it knows to direct traffic to your containers. It also sets up SSL/TLS encryption for you. For more information on how SSL/TLS works, see :ref:`how-tls-works`.

If your DNS provider does not allow CNAME, which is common for naked/root domains, and you are using the gcp us-central1 region, you can also use an A record. Use the IP address 104.198.47.241. For AWS, unfortunately, you have to use a CNAME so the only option is to change DNS providers.

Note that if you want both the naked/root domain and a subdomain such as www, be sure to run `gigalixir add_domain` for each one.

How to Set Up SSL/TLS
=====================

SSL/TLS certificates are set up for you automatically assuming your custom domain is set up properly. You
shouldn't have to lift a finger. For more information on how this works, see :ref:`how-tls-works`.
 
.. _`tail logs`:
.. _`logging`:

How to Tail Logs
================

You can tail logs in real-time aggregated across all containers using the following command. 

.. code-block:: bash

    gigalixir logs 
 
How to Forward Logs Externally
==============================

If you want to forward your logs to another service such as `Timber`_ or `PaperTrail`_, you'll need to set up a log drain. We support HTTPS and syslog drains. To create a log drain, run

.. code-block:: bash

    gigalixir drains:add $URL
    # e.g. gigalixir drains:add https://$TIMBER_API_KEY@logs.timber.io/frames
    # e.g. gigalixir drains:add syslog+tls://logs123.papertrailapp.com:12345

To show all your drains, run

.. code-block:: bash

    gigalixir drains

To delete a drain, run

.. code-block:: bash

    gigalixir drains:remove $DRAIN_ID

.. _`Timber`: https://timber.io

.. _managing-ssh-keys:

Managing SSH Keys
=================

In order to SSH, run remote observer, remote console, etc, you need to set up your SSH keys. It could take up to a minute for the SSH keys to update in your containers.

.. code-block:: bash

    gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_rsa.pub)"

If you don't have an :bash:`id_rsa.pub` file, follow `this guide <https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/>`_ to create one.

To view your SSH keys

.. code-block:: bash

    gigalixir account:ssh_keys

To delete an SSH key, find the key's id and then run delete the key by id.

.. code-block:: bash

    gigalixir account:ssh_keys:remove $ID

How to SSH into a Production Container
======================================

To SSH into a running production container, first, add your public SSH keys to your account. For more information on managing SSH keys, see :ref:`managing-ssh-keys`.

.. code-block:: bash

    gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_rsa.pub)"

Then use the following command to SSH into a live production container. If you are running multiple 
containers, this will put you in a random container. We do not yet support specifying which container you want to SSH to. In order for this work, you must add your public SSH keys to your account.

.. code-block:: bash

    gigalixir ps:ssh 

How to specify SSH key or other SSH options
===========================================

The :bash:`-o` option lets you pass in arbitrary options to :bash:`ssh`. Something like this will let you specify which SSH key to use.

.. code-block:: bash

    gigalixir ps:ssh -o "-i ~/.ssh/id_rsa" 

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
 
How to Change or Reset Your Password
====================================

To change your password, run


.. code-block:: bash

    gigalixir account:password:change

If you forgot your password, send a reset token to your email address by running the following command and following the instructions in the email.

.. code-block:: bash

    gigalixir account:password:reset

How to Change Your Credit Card
==============================

To change your credit card, run

.. code-block:: bash

    gigalixir account:payment_method:set

How to Delete your Account
==========================

There is currently no way to completely delete an account. We are working on implementing this feature. You can delete apps though. See :ref:`delete-app`_.

.. _`restart`:

How to Restart an App
=====================

.. code-block:: bash

    gigalixir ps:restart 

For hot upgrades, See :ref:`hot-upgrade`. We are working on adding custom health checks. 

Restarts should be zero-downtime. See :ref:`zero-downtime`.

.. _`zero-downtime`:

How to Set Up Zero-Downtime Deploys
===================================

Normally, there is nothing you need to do to have zero-downtime deploys. The only caveat is that health checks are currently done by checking if tcp port 4000 is listening. If your app opens the port before it is ready, then it may start receiving traffic before it is ready to serve it. In most cases, with Phoenix, this isn't a problem.

One downside of zero-downtime deploys is that they make deploys slower. What happens during a deploy is

  1. Spawn a new instance
  2. Wait for health check on the new instance to pass
  3. Start sending traffic to the new instance
  4. Stop sending traffic to the old instance
  5. Wait 30 seconds for old instance is finish processing requests
  6. Terminate the old instance
  7. Repeat for every instance

Although you should see your new code running within a few seconds, the entire process takes over 30 seconds per instance so if you have a lot of instances running, this could take a long time.

Heroku opts for faster deploys and restarts instead of zero-downtime deploys.

.. _`jobs`:

How to Run Jobs
===============

There are many ways to run one-off jobs and tasks. You can run them in the container your app is running or you can spin up a new container that runs the command and then destroys itself.

To run a command in your app container, run

.. code-block: bash

    gigalixir ps:run $COMMAND
    # if you're using distillery, you'll probably want $COMMAND to be something like :bash:`bin/app command Elixir.Tasks migrate`
    # if you're using mix, you'll probably want $COMMAND to be something like :bash:`mix ecto.migrate`

To run a command in a separate container, run

.. code-block: bash

    gigalixir run $COMMAND
    # if you're using distillery, you'll probably want $COMMAND to be something like :bash:`bin/app command Elixir.Tasks migrate`
    # if you're using mix, you'll probably want $COMMAND to be something like :bash:`mix ecto.migrate`

.. For an example task, see `gigalixir-getting-started's migrate task`_. 

The task is not run on the same node that your app is running in. Jobs are killed after 5 minutes. 

If you're using the distillery, note that beacuse we start a separate container to run the job, if you need any applications started such as your :elixir:`Repo`, use :elixir:`Application.ensure_all_started/2`. Also, be sure to stop all applications when done, otherwise your job will never complete and just hang until it times out. 

.. For more information about running migrations with Distillery, see `Distillery's Running Migrations`_. 

Distillery commands currently do not support passing arguments into the job. 

We prepend :elixir:`Elixir.` to your module name to let the BEAM virtual machine know that you want to run an Elixir module rather than an Erlang module. The BEAM doesn't know the difference between Elixir code and Erlang code once it is compiled down, but compiled Elixir code is namespaced under the Elixir module.

The size of the container that runs your job will be the same size as the app containers and billed the same way, based on replica-size-seconds. See, :ref:`pricing`.

.. _`gigalixir-getting-started's migrate task`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/lib/tasks.ex
.. _`Distillery's Running Migrations`: https://hexdocs.pm/distillery/running-migrations.html

How to Reset your API Key
=========================

If you lost your API key or it has been stolen, you can reset it by running

.. code-block:: bash

    gigalixir account:api_key:reset

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


.. _`provisioning free database`:

How to provision a Free PostgreSQL database
===========================================

IMPORTANT: Make sure you set your :bash:`pool_size` in :bash:`prod.exs` to 1 beforehand. The free tier database only allows one connection.

The following command will provision a free database for you and set your :bash:`DATABASE_URL` environment variable appropriately. 

.. code-block:: bash

    gigalixir pg:create --free 

List databases by running

.. code-block:: bash

    gigalixir pg 

Delete by running

.. code-block:: bash

    gigalixir pg:destroy $DATABASE_ID

You can only have one database per app because otherwise managing your :bash:`DATABASE_URL` variable would become trickier.

In the free tier, the database is free, but it is really not suitable for production use. It is a multi-tenant postgres database cluster with shared CPU, memory, and disk. You are limited to 2 connections, 10,000 rows, and no backups. Idle connections are terminated after 5 minutes. If you want to upgrade your database, you'll have to migrate the data yourself. For a complete feature comparison see :ref:`tiers`.

For information on upgrading your account, see :ref:`upgrade account`.

.. _`provisioning database`:

How to provision a Standard PostgreSQL database
===============================================

The following command will provision a database for you and set your :bash:`DATABASE_URL` environment variable appropriately. 

.. code-block:: bash

    gigalixir pg:create --size=0.6

It takes a few minutes to provision. You can check the status by running

.. code-block:: bash

    gigalixir pg 

You can only have one database per app because otherwise managing your :bash:`DATABASE_URL` variable would become trickier.

Under the hood, we use Google's Cloud SQL which provides reliability, security, and automatic backups. For more information, see `Google Cloud SQL for PostgreSQL Documentation`_.

.. _`Google Cloud SQL for PostgreSQL Documentation`: https://cloud.google.com/sql/docs/postgres/

How to scale a database
=======================

To change the size of your database, run

.. code-block:: bash

    gigalixir pg:scale $DATABASE_ID --size=1.7

Supported sizes include 0.6, 1.7, 4, 8, 16, 32, 64, and 128. For more information about databases sizes, see :ref:`database sizes`.

How to delete a database
========================

WARNING!! Deleting a database also deletes all of its backups. Please make sure you backup your data first.

To delete a database, run

.. code-block:: bash

    gigalixir pg:destroy $DATABASE_ID

How to install a Postgres Extension
===================================

First, make sure Google Cloud SQL supports your extension by checking `their list of extensions`_. If it is supported, find your database url by running

.. code-block:: bash

    gigalixir pg

Then, get a psql console into your database

.. code-block:: bash

    psql $DATABASE_URL

Then, install your extension

.. code-block:: bash

    CREATE EXTENSION foo;

.. _`their list of extensions`: https://cloud.google.com/sql/docs/postgres/extensions

.. _`database sizes`:

Database Sizes & Pricing
========================

In the free tier, the database is free, but it is really not suitable for production use. It is a multi-tenant postgres database cluster with shared CPU, memory, and disk. You are limited to 2 connections, 10,000 rows, and no backups. Idle connections are terminated after 5 minutes. If you want to upgrade your database, you'll have to migrate the data yourself. For a complete feature comparison see :ref:`tiers`.

In the standard tier, database sizes are defined as a single number for simplicity. The number defines how many GBs of memory your database will have. Supported sizes include 0.6, 1.7, 4, 8, 16, 32, 64, and 128. Sizes 0.6 and 1.7 share CPU with other databases. All other sizes have dedicated CPU, 1 CPU for every 4 GB of memory. For example, size 4 has 1 dedicated CPU and size 64 has 16 dedicated CPUs. All databases start with 10 GB disk and increase automatically as needed. We currently do not set a limit for disk size, but we probably will later.

====  =============
Size  Price / Month
====  =============
0.6   $25
1.7   $50
  4   $400
  8   $800
 16   $1600
 32   $3200
 64   $6400
128   $12800
====  =============

Prices are prorated to the second.

For more, see :ref:`provisioning database` and :ref:`provisioning free database`.

.. _`connect-database`:

How to Connect a Database
=========================

If you followed the :ref:`quick start`, then your database should already be connected. If not, connecting to a database is done no differently from apps running outside Gigalixir. We recommend you set a DATABASE_URL config and configure your database adapter accordingly to read from that variable. In short, you'll want to add something like this to your :bash:`prod.exs` file.

.. code-block:: elixir

     config :gigalixir_getting_started, GigalixirGettingStarted.Repo,
       adapter: Ecto.Adapters.Postgres,
       url: {:system, "DATABASE_URL"},
       database: "",
       ssl: true,
       pool_size: 1

Replace :elixir:`:gigalixir_getting_started` and :elixir:`GigalixirGettingStarted` with your app name. Then, be sure to set your :bash:`DATABASE_URL` config with something like this.  For more information on setting configs, see :ref:`configs`. If you provisioned your database using, :ref:`provisioning database`, then :bash:`DATABASE_URL` should be set for you automatically once the database in provisioned. Otherwise,

.. code-block:: bash

    gigalixir config:set DATABASE_URL="ecto://user:pass@host:port/db"

If you need to provision a database, Gigalixir provides Databases-as-a-Service. See :ref:`provisioning database`. If you prefer to provision your database manually, follow `How to set up a Google Cloud SQL PostgreSQL database`_.

.. _`supports PostgreSQL`: https://cloud.google.com/sql/docs/postgres/
.. _`Phoenix Using MySQL Guide`: http://www.phoenixframework.org/docs/using-mysql
.. _`Amazon Relational Database Service`: https://aws.amazon.com/rds/
.. _`Google Cloud SQL`: https://cloud.google.com/sql/docs/
.. _`gigalixir-getting-started`: https://github.com/gigalixir/gigalixir-getting-started
.. _`lib/gigalixir-getting-started.ex`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/lib/gigalixir_getting_started.ex#L14


.. _`How to set up a Google Cloud SQL PostgreSQL database`:

How to manually set up a Google Cloud SQL PostgreSQL database
-------------------------------------------------------------

Note: You can also use Amazon RDS, but we do not have instructions provided yet.

1. Navigate to https://console.cloud.google.com/sql/instances and click "Create Instance".
#. Select PostgreSQL and click "Next".
#. Configure your database.

   a. Choose any instance id you like. 
   #. Choose us-central1 as the Region. 
   #. Choose how many cores, memory, and disk.
   #. In "Default user password", click "Generate" and save it somewhere secure.
   #. In "Authorized networks", click "Add network" and enter "0.0.0.0/0" in the "Network" field. It will be encrypted with TLS and authenticated with a password so it should be okay to make the instance publically accessible. Click "Done".

#. Click "Create".
#. Wait for the database to create.
#. Make note of the database's external ip. You'll need it later.
#. Click on the new database to see instance details.
#. Click on the "Databases" tab.
#. Click "Create database".
#. Choose any name you like, remember it, and click "Create".
#. Run 
   
   .. code-block:: bash
   
       gigalixir config:set DATABASE_URL="ecto://postgres:$PASSWORD@$EXTERNAL_IP:5432/$DB_NAME"
    
   with $PASSWORD, $EXTERNAL_IP, and $DB_NAME replaced with values from the previous steps.
#. Make sure you have :elixir:`ssl:true` in your :bash:`prod.exs` database configuration. Cloud SQL supports TLS out of the boxso your database traffic should be encrypted.

We hope to provide a database-as-a-service soon and automate the process you just went through. Stay tuned.

.. _`migrations`:

How to Run Migrations
=====================

If you deployed your app without distillery, you can run migrations as a job in a new container.

.. code-block:: bash

    gigalixir run mix ecto.migrate

If you deployed your app as a distillery release, :bash:`mix` isn't available. We try to make it easy by providing a special command, but the command runs on your existing app container so you'll need to make sure your app is running first and set up SSH keys.

.. code-block:: bash

    gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_rsa.pub)"

Then run

.. code-block:: bash

    gigalixir ps:migrate 

This command runs your migrations in a remote console directly on your production node. It makes some assumptions about your project so if it does not work, please `contact us for help`_. 

If you are running an umbrella app, you will probably need to specify which "inner app" within your umbrella to migrate. Do this by passing the :bash:`--migration_app_name` flag like so

.. code-block:: bash

    gigalixir ps:migrate --migration_app_name=$MIGRATION_APP_NAME

More details:

If you need to tweak the migration command to run yourself, all we are doing is dropping into a remote_console and running the following. For information on how to open a remote console, see :ref:`remote console`.

.. code-block:: elixir

    repo = List.first(Application.get_env(:gigalixir_getting_started, :ecto_repos))
    app_dir = Application.app_dir(:gigalixir_getting_started, "priv/repo/migrations")
    Ecto.Migrator.run(repo, app_dir, :up, all: true)

So for example, a tweak you might make is, if you have more than one app, you may not want to use :elixir:`List.first` to find the app that contains the migrations.

.. _`the source code`: https://github.com/gigalixir/gigalixir-cli/blob/master/gigalixir/app.py#L160

If you have a chicken-and-egg problem where your app will not start without migrations run, and migrations won't run without an app running, you can try the following workaround on your local development machine. This will run migrations on your production database from your local machine using your local code.

.. code-block:: bash

    MIX_ENV=prod mix release --env=prod
    MIX_ENV=prod DATABASE_URL="$YOUR_PRODUCTION_DATABASE_URL" mix ecto.migrate

How to reset the database?
==========================

First, `drop into a remote console`_ and run this to "down" migrate. You may have to tweak the command depending on what your app is named and if you're running an umbrella app.

.. code-block:: elixir

    Ecto.Migrator.run(MyApp.Repo, Application.app_dir(:my_app, "priv/repo/migrations"), :down, [all: true])

Then run this to "up" migrate.

.. code-block:: elixir

    Ecto.Migrator.run(MyApp.Repo, Application.app_dir(:my_app, "priv/repo/migrations"), :up, [all: true])

How to run seeds?
=================

Running seeds in production is usually a one-time job, so our recommendation is to `drop into a remote console`_ and run commands manually. If you have a :bash:`seeds.exs` file, you can follow `the Distillery migration guide`_ and run something like this in your remote console.

.. code-block:: elixir

    seed_script = Path.join(["#{:code.priv_dir(:myapp)}", "repo", "seeds.exs"])
    Code.eval_file(seed_script)

.. _`the Distillery migration guide`: https://hexdocs.pm/distillery/running-migrations.html#content

.. _`Launching a remote console`: 
.. _`drop into a remote console`: 
.. _`remote console`: 


How to Drop into a Remote Console
=================================

To get a console on a running production container, first, add your public SSH keys to your account. For more information on managing SSH keys, see :ref:`managing-ssh-keys`.

.. code-block:: bash

    gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_rsa.pub)"

Then run this command to drop into a remote console.

.. code-block:: bash

    gigalixir ps:remote_console 

How to Run Distillery Commands
==============================

Since we use Distillery to build releases, we also get all the commands Distillery provides such as ping, rpc, command, and eval. `Launching a remote console`_ is just a special case of this. To run a Distillery command, run the command below. For a complete list of commands, see `Distillery's boot.eex`_.

.. code-block:: bash

    gigalixir ps:distillery $COMMAND

.. _`Distillery's boot.eex`: https://github.com/bitwalker/distillery/blob/master/priv/templates/boot.eex#L417

.. _app-status:

How to Check App Status
=======================

To see how many replicas are actually running in production compared to how many are desired, run

.. code-block:: bash

    gigalixir ps 

How to Check Account Status
===========================

To see things like which account you are logged in as, what tier you are on, and how many credits you have available, run

.. code-block:: bash

    gigalixir account

.. _`remote observer`:

How to Launch a Remote Observer
===============================

In order to run a remote observer, you need to set up your SSH keys. It could take up to a minute for the SSH keys to update in your containers.

.. code-block:: bash

    gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_rsa.pub)"

Because Observer runs on your local machine and connects to a production node by joining the production cluster, you first have to have clustering set up. You don't have to have multiple nodes, but you need to follow the instructions in :ref:`clustering`.

You also need to have :elixir:`runtime_tools` in your application list in your :bash:`mix.exs` file. Phoenix 1.3 adds it by default, but you have to add it youself in Phoenix 1.2.

Your local machine also needs to have :bash:`lsof`.

Then, to launch observer and connect it to a production node, run

.. code-block:: bash

    gigalixir ps:observer 

and follow the instructions. It will prompt you for your local sudo password so it can modify iptables rules. This connects to a random container using consistent hashing. We don't currently allow you to specify which container you want to connect to, but it will connect to the same container each time based on a hash of your ip address.

How to see the current period's usage
=====================================

To see how many replica-size-seconds you've used so far this month, run

.. code-block:: bash

    gigalixir account:usage

The amount you see here has probably not been charged yet since we do that at the end of the month.

How to see previous invoices
============================

To see all your previous period's invoices, run

.. code-block:: bash

    gigalixir account:invoices

.. _`money back guarantee`:

How to give another user permission to deploy my app
====================================================

Gigalixir has a way to add permissions so many users can deploy the same app, but giving another user permissions also grants them access to managing config vars, rollbacks, and gives them access to ssh, remote_console, observer, etc.

.. code-block:: bash

    gigalixir access:add $USER_EMAIL

.. code-block:: bash

    gigalixir access

.. code-block:: bash

    gigalixir access:remove $USER_EMAIL

.. _`How to deploy a Ruby app`:

How to deploy a Ruby app
========================

.. code-block:: bash

    gigalixir login
    git clone https://github.com/heroku/ruby-getting-started.git
    cd ruby-getting-started
    APP=$(gigalixir create)
    git push gigalixir master
    curl https://$APP.gigalixirapp.com/


.. _`gigalixir release options`:

How to specify which Distillery release, environment, or profile to build
=========================================================================

If you have multiple releases defined in :bash:`rel/config.exs`, which is common for umbrella apps, you can specify which release to build
by setting a config variable on your app that controls the options passed to `mix release`. For example, you can pass the `--profile` option 
using the command below.

.. code-block:: bash

    gigalixir config:set GIGALIXIR_RELEASE_OPTIONS="--profile=$RELEASE_NAME:$RELEASE_ENVIRONMENT"

With this config variable set on each of your gigalixir apps, when you deploy the same repo to each app, you'll get a different release.

How secure is Gigalixir?
========================

Gigalixir takes security very, very seriously. 

#. Every app exists in its own Kubernetes namespaces and we use Kubernetes role-based access controls to ensure no other apps have access to your app or its metadata. 
#. Your build environment is fully isolated using Docker containers. 
#. Your slugs are authenticated using `Signed URLs`_.
#. All API endpoints are authenticated using API keys instead of your password. API keys can be invalidated at any time by regenerating a new one.
#. Remote console and remote observer uses a SSH tunnels to secure traffic. 
#. Erlang does not encrypt distribution traffic between your nodes by default, but you can `set it up to use SSL`_. For an extra layer of security, we route distribution traffic directly to each node so no other apps can sniff the traffic. 
#. We use `Stripe`_ to manage payment methods so Gigalixir never knows your credit card number.
#. Passwords and app configs are encrypted at rest using `Cloak`_.
#. Traffic between Gigalixir services and components are TLS encrypted.

.. _`Signed URLs`: https://cloud.google.com/storage/docs/access-control/signed-urls
.. _`Cloak`: https://github.com/danielberkompas/cloak
.. _`Stripe`: https://stripe.com/
.. _`set it up to use SSL`: http://erlang.org/doc/apps/ssl/ssl_distribution.html

Are there any benchmarks?
=========================

Take a look at our `benchmark data <https://docs.google.com/spreadsheets/d/1KWES-cSH_qXZQN9y3yu6HDSTdweIbZQuL12qLvkJnBo/edit?usp=sharing>`_.

Money-back Guarantee
====================

If you are unhappy for any reason within the first 31 days, contact us to get a refund up to $75. Enough to run a 3 node cluster for 31 days.

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _`pip documentation`: https://packaging.python.org/installing/
.. _`git documentation`: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
.. _`Distillery appup documentation`: https://hexdocs.pm/distillery/upgrades-and-downgrades.html#appups
.. _`Distillery's upgrade command`: https://hexdocs.pm/distillery/walkthrough.html#deploying-an-upgrade
.. _`heroku/cedar:14`: https://hub.docker.com/r/heroku/cedar/
.. _`container that runs your app`: https://github.com/gigalixir/gigalixir-run
.. _`herokuish`: https://github.com/gliderlabs/herokuish
.. _`Gigalixir`: https://gigalixir.com
.. _`elixir homepage`: http://elixir-lang.org/
.. _`phoenix homepage`: http://www.phoenixframework.org/
.. _`twelve-factor methodology`: https://12factor.net/
.. _`PaperTrail`: https://papertrailapp.com/
.. _`Running Elixir and Phoenix projects on a cluster of nodes`: https://dockyard.com/blog/2016/01/28/running-elixir-and-phoenix-projects-on-a-cluster-of-nodes
.. |signup details| replace:: Create an account using the following command. It will prompt you for your email address and password. You will have to confirm your email before continuing. Gigalixir's free tier does not require a credit card, but you will be limited to 1 instance with 0.2GB of memory and 1 postgresql database limited to 10,000 rows.
.. |set up app for deploys| replace:: To create your app, run the following command. It will also set up a git remote. This must be run from within a git repository folder. An app name will be generated for you, but you can also optionally supply an app name if you wish using :bash:`gigalixir create -n $APP_NAME`. There is currently no way to change your app name once it is created. If you like, you can also choose which cloud provider and region using the :bash:`--cloud` and :bash:`--region` options. We currently support :bash:`gcp` in :bash:`us-central1` or :bash:`europe-west1` and :bash:`aws` in :bash:`us-east-1` or :bash:`us-west-2`.
.. _`The Twelve-Factor App's Config Factor`: https://12factor.net/config
.. _`Herokuish`: https://github.com/gliderlabs/herokuish
.. _`gigalixir-getting-started`: https://github.com/gigalixir/gigalixir-getting-started
