.. _`quick start`:

Getting Started Guide
=====================

The goal of this guide is to get your app up and running on Gigalixir. You will sign up for an account, prepare your app, deploy, and provision a database.

If you're deploying an open source project, we provide consulting services free of charge. :ref:`Contact us<help>` and we'll send you a pull request with everything you need to get started.

Prerequisites
-------------

.. role:: elixir(code)
    :language: elixir

.. role:: bash(code)
    :language: bash

#. :bash:`python3`. :bash:`python2` also works, but it is EOL as of January 1st, 2020.
#. :bash:`pip3`. For help, take a look at the `pip documentation <https://packaging.python.org/installing/>`_.
#. :bash:`git`. For help, take a look at the `git documentation <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.
#. Linux, OS X, or Windows (beta).

For example, on Ubuntu, run

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install -y python3 python3-pip git-core curl

.. _`buildpack configuration file`: https://github.com/HashNuke/heroku-buildpack-elixir#configuration
.. _`beta sign up form`: https://docs.google.com/forms/d/e/1FAIpQLSdB1Uh1mGQHqIIX7puoZvwm9L93bR88cM1uGeSOCXh06_smVg/viewform
.. _`gigalixir-getting-started-phx-1-3-rc-2`: https://github.com/gigalixir/gigalixir-getting-started-phx-1-3-rc-2

.. _`install the CLI`:

Install the Command-Line Interface
----------------------------------

Next, install the command-line interface. Gigalixir has a web interface at https://console.gigalixir.com/, but you will still need the CLI to do anything other than signup, deploy, and scale.

.. code-block:: bash

    pip3 install gigalixir --ignore-installed six

Make sure the executable is in your path, if it isn't already. 

.. code-block:: bash

    echo 'export PATH=~/.local/bin:$PATH' >> ~/.bash_profile

Reload the profile

.. code-block:: bash

    source ~/.bash_profile

Verify by running

.. code-block:: bash

    gigalixir --help

The reason we ignore six is because OS X has a pre-installed version of six that is incompatible. When pip tries to upgrade it, OS X won't let us. For more, see https://github.com/pypa/pip/issues/3165

Create an Account
-----------------

If you already have an account, skip this step.

Create an account using the following command. It will prompt you for your email address and password. You will have to confirm your email before continuing. Gigalixir's free tier does not require a credit card, but you will be limited to 1 instance with 0.2GB of memory and 1 postgresql database limited to 10,000 rows.

.. code-block:: bash

    gigalixir signup


Log In
------

Next, log in. This will grant you an api key. It will also optionally modify your ~/.netrc file so that all future commands are authenticated.

.. code-block:: bash

    gigalixir login

Verify by running

.. code-block:: bash

    gigalixir account

Prepare Your App
----------------

Most likely, there is nothing you need to do here and you can skip this step and "just deploy", but it depends on what version of phoenix you're running and whether you are okay running in mix mode without distillery or elixir releases. 

For more information, click here: :ref:`modifying existing app`. 

Or if you just want to give gigalixir a spin, clone our reference app.

.. code-block:: bash

    git clone https://github.com/gigalixir/gigalixir-getting-started.git


.. _`set up deploys`:

Set Up App for Deploys
----------------------

To create your app, run the following command. It will also set up a git remote. This must be run from within a git repository folder. An app name will be generated for you, but you can also optionally supply an app name if you wish using :bash:`gigalixir create -n $APP_NAME`. There is currently no way to change your app name once it is created. If you like, you can also choose which cloud provider and region using the :bash:`--cloud` and :bash:`--region` options. We currently support :bash:`gcp` in :bash:`v2018-us-central1` or :bash:`europe-west1` and :bash:`aws` in :bash:`us-east-1` or :bash:`us-west-2`. The default is v2018-us-central1 on gcp.

.. code-block:: bash

    cd gigalixir-getting-started
    APP_NAME=$(gigalixir create)

Verify that the app was created, by running

.. code-block:: bash

    gigalixir apps

Verify that a git remote was created by running

.. code-block:: bash

    git remote -v

Specify Versions
----------------

The default Elixir version is defined `here <https://github.com/HashNuke/heroku-buildpack-elixir/blob/master/elixir_buildpack.config>`_ which is quite old and it's a good idea to use the same version in production as you use in development so let's specify them. Supported Elixir and erlang versions can be found at https://github.com/HashNuke/heroku-buildpack-elixir#version-support

.. code-block:: bash

    echo "elixir_version=1.10.3" > elixir_buildpack.config
    echo "erlang_version=22.3" >> elixir_buildpack.config

Same for nodejs

.. code-block:: bash

    echo "node_version=12.16.3" > phoenix_static_buildpack.config

Don't forget to commit

.. code-block:: bash

    git add elixir_buildpack.config phoenix_static_buildpack.config
    git commit -m "set elixir, erlang, and node version"

Provision a Database
--------------------

Phoenix 1.4+ enforces the DATABASE_URL env var at compile time so let's create a database first, before deploying.

.. code-block:: bash

    gigalixir pg:create --free

Verify by running

.. code-block:: bash

    gigalixir pg

Once the database is created, verify your configuration includes a :bash:`DATABASE_URL` by running

.. code-block:: bash

    gigalixir config

Deploy!
-------

Finally, build and deploy.

.. code-block:: bash

    git push gigalixir master

Wait a minute or two for the app to pass health checks. You can check the status by running

.. code-block:: bash

    gigalixir ps

Once it's healthy, verify it works

.. code-block:: bash

    curl https://$APP_NAME.gigalixirapp.com/
    # or you could also run
    # gigalixir open

Run Migrations
--------------

If you are not using releases, the easiest way to run migrations is as a job.

.. code-block:: bash

    gigalixir run mix ecto.migrate
    # this is run asynchronously as a job, so to see the progress, you need to run
    gigalixir logs

If you are using distillery or Elixir releases, your app needs to be up and running, then run

.. code-block:: bash

    # pg:migrate runs migrations from your app node so we need to add ssh keys first
    gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_rsa.pub)"
    gigalixir ps:migrate

For more, see :ref:`migrations`.

What's Next?
------------

- :ref:`configs`
- :ref:`app-status`
- :ref:`logging`
- :ref:`scale`
- :ref:`restart`
- :ref:`rollback`
- :ref:`remote console`
- :ref:`remote observer`
- :ref:`hot-upgrade`

.. _`make your existing app work on Gigalixir`:
.. _`modifying existing app`:

Modifying an Existing App to Run on Gigalixir
=============================================

Whether you have an existing app or you just ran :bash:`mix phx.new`, the goal of this guide is to get your app ready for deployment on Gigalixir. We assume that you are using Phoenix here. If you aren't, feel free to :ref:`contact us<help>` for help. As long as your app is serving HTTP traffic on :bash:`$PORT`, you should be fine.

Important: If you have an umbrella app, be sure to *also* see :ref:`umbrella`.

.. _`mix vs distillery`:
.. _`deploy-types`:

Mix vs Distillery vs Elixir Releases
------------------------------------

Probably the hardest part of deploying Elixir is choosing which method of deploying you prefer. We typically recommend Distillery because it has the most features, but Mix is much simpler and Elixir releases give you a bit of both. Here is a comparison table to help you choose. Any features not in the table are available for all three.

=======================  =================== ======================= =========== 
Feature                  Mix                 Elixir Releases         Distillery
=======================  =================== ======================= ===========
Hot Upgrades                                                         YES
Remote Observer                              YES                     YES
Mix Tasks                YES
Included with Elixir     YES                 YES
Easy Configuration       YES
=======================  =================== ======================= ===========

If you choose mix, see :ref:`modifying existing app with mix`.

If you choose distillery, see :ref:`modifying existing app with distillery`.

If you choose Elixir releases, see :ref:`modifying existing app with Elixir releases`.

.. _`modifying existing app with mix`:

Using Mix
---------

For an example app that uses mix and works on gigalixir, see https://github.com/gigalixir/gigalixir-getting-started/tree/js/mix

Configuration and Secrets
^^^^^^^^^^^^^^^^^^^^^^^^^

Then append something like the following in :bash:`prod.exs`. Don't replace what you already have, just add this to the bottom.

.. code-block:: elixir

     config :gigalixir_getting_started, GigalixirGettingStartedWeb.Endpoint,
       http: [port: {:system, "PORT"}], # Possibly not needed, but doesn't hurt
       url: [host: System.get_env("APP_NAME") <> ".gigalixirapp.com", port: 80],
       secret_key_base: Map.fetch!(System.get_env(), "SECRET_KEY_BASE"),
       server: true

     config :gigalixir_getting_started, GigalixirGettingStarted.Repo,
       adapter: Ecto.Adapters.Postgres,
       url: System.get_env("DATABASE_URL"),
       ssl: true,
       pool_size: 2 # Free tier db only allows 4 connections. Rolling deploys need pool_size*(n+1) connections where n is the number of app replicas.

1. Replace :elixir:`:gigalixir_getting_started` with your app name e.g. :elixir:`:my_app`
2. Replace :elixir:`GigalixirGettingStartedWeb.Endpoint` with your endpoint module name. You can find your endpoint module name by running something like

   .. code-block:: bash

     grep -R "defmodule.*Endpoint" lib/

   Phoenix 1.2, 1.3, and 1.4 give different names so this is a common source of errors.
3. Replace :elixir:`GigalixirGettingStarted.Repo` with your repo module name e.g. :elixir:`MyApp.Repo`

You don't have to worry about setting your :bash:`SECRET_KEY_BASE` config because we generate one and set it for you. 

Don't forget to commit your changes

.. code-block:: bash

    git add config/prod.exs
    git commit -m "setup production deploys"

Verify
^^^^^^

Let's make sure everything works.

.. code-block:: bash

    APP_NAME=foo SECRET_KEY_BASE="$(mix phx.gen.secret)" MIX_ENV=prod DATABASE_URL="postgresql://user:pass@localhost:5432/foo" PORT=4000 mix phx.server

Check it out.

.. code-block:: bash

    curl localhost:4000

If everything works, continue to :ref:`set up deploys`.

Specify Buildpacks (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We rely on buildpacks to compile and build your release. We auto-detect a variety of buildpacks so you probably don't need this, but if you want
to specify your own buildpacks create a :bash:`.buildpacks` file with the buildpacks you want. For example,

.. code-block:: bash

    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-mix.git

:bash:`heroku-buildpack-phoenix-static` is optional if you do not have Phoenix static assets. For more information about buildpacks, see :ref:`life of a deploy`.

Note, that the command that gets run in production depends on what your last buildpack is.

- If the last buildpack is :bash:`gigalixir-buildpack-mix`, then the command run will be something like :bash:`elixir --name $MY_NODE_NAME --cookie $MY_COOKIE -S mix phx.server`.
- If the last buildpack is :bash:`heroku-buildpack-phoenix-static`, then the command run will be :bash:`mix phx.server`.
- If the last buildpack is :bash:`heroku-buildpack-elixir`, then the command run will be :bash:`mix run --no-halt`.

If your command is :bash:`mix run --no-halt`, but you are running Phoenix (just not the assets pipeline), make sure you set :elixir:`server: true` in :bash:`prod.exs`.

We highly recommend keeping :bash:`gigalixir-buildpack-mix` last so that your node name and cookie are set properly. Without those, remote_console, ps:migrate, observer, etc won't work.

.. _`modifying existing app with distillery`:

Using Distillery
----------------

For an example app that uses distillery and works on gigalixir, see https://github.com/gigalixir/gigalixir-getting-started

Install Distillery to Build Releases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In short, you'll need to add something like this to the :elixir:`deps` list in :bash:`mix.exs`

.. code-block:: elixir

    {:distillery, "~> 2.1"}

Important: If you are running Elixir 1.9, then you *must* use distillery 2.1 or greater. Elixir 1.9 and distillery below 2.1 both use `mix release` and Elixir's always takes precedence. Distillery 2.1 renames the task to `mix distillery.release`.

Then, run

.. code-block:: bash

    mix deps.get
    mix distillery.init
    # if you are running distillery below version 2.1, you'll want to run `mix release.init` instead

Don't forget to commit

.. code-block:: bash

    git add mix.exs mix.lock rel/
    git commit -m 'install distillery'


.. _`Distillery installation instructions`: https://hexdocs.pm/distillery/introduction/installation.html

Configuration and Secrets
^^^^^^^^^^^^^^^^^^^^^^^^^

Add something like the following in :bash:`prod.exs`

.. code-block:: elixir

     config :gigalixir_getting_started, GigalixirGettingStartedWeb.Endpoint,
       server: true, # Without this line, your app will not start the web server!
       load_from_system_env: true, # Needed for Phoenix 1.3. Doesn't hurt for other versions
       http: [port: {:system, "PORT"}], # Needed for Phoenix 1.2 and 1.4. Doesn't hurt for 1.3.
       secret_key_base: "${SECRET_KEY_BASE}",
       url: [host: "${APP_NAME}.gigalixirapp.com", port: 443],
       cache_static_manifest: "priv/static/cache_manifest.json",
       version: Mix.Project.config[:version] # To bust cache during hot upgrades

     config :gigalixir_getting_started, GigalixirGettingStarted.Repo,
       adapter: Ecto.Adapters.Postgres,
       url: "${DATABASE_URL}",
       database: "", # Works around a bug in older versions of ecto. Doesn't hurt for other versions.
       ssl: true,
       pool_size: 2 # Free tier db only allows 4 connections. Rolling deploys need pool_size*(n+1) connections where n is the number of app replicas.

:elixir:`server: true` **is very important and is commonly left out. Make sure you have this line.**

1. Replace :elixir:`:gigalixir_getting_started` with your app name e.g. :elixir:`:my_app`
2. Replace :elixir:`GigalixirGettingStartedWeb.Endpoint` with your endpoint module name. You can find your endpoint module name by running something like

   .. code-block:: bash

     grep -R "defmodule.*Endpoint" lib/

   Phoenix 1.2, 1.3, and 1.4 give different names so this is a common source of errors.
3. Replace :elixir:`GigalixirGettingStarted.Repo` with your repo module name e.g. :elixir:`MyApp.Repo`

You don't have to worry about setting your :bash:`SECRET_KEY_BASE` config because we generate one and set it for you. If you don't use a gigalixir managed postgres database, you'll have to set the :bash:`DATABASE_URL` yourself. 

Verify
^^^^^^

Let's make sure everything works.

First, try generating building static assets

.. code-block:: bash

    mix deps.get

    # generate static assets
    cd assets
    npm install
    npm run deploy
    cd ..
    mix phx.digest

and building a Distillery release locally

.. code-block:: bash

    MIX_ENV=prod mix distillery.release --env=prod
    # if you are running distillery below 2.1, you'll want to run this instead: MIX_ENV=prod mix release --env=prod

and running it locally

.. code-block:: bash

    MIX_ENV=prod APP_NAME=gigalixir_getting_started SECRET_KEY_BASE="$(mix phx.gen.secret)" DATABASE_URL="postgresql://user:pass@localhost:5432/foo" MY_HOSTNAME=example.com MY_COOKIE=secret REPLACE_OS_VARS=true MY_NODE_NAME=foo@127.0.0.1 PORT=4000 _build/prod/rel/gigalixir_getting_started/bin/gigalixir_getting_started foreground

Don't forget to replace :bash:`gigalixir_getting_started` with your own app name. Also, change/add the environment variables as needed.

Commit the changes

.. code-block:: bash

    git add config/prod.exs assets/package-lock.json
    git commit -m 'distillery configuration'

Check it out.

.. code-block:: bash

    curl localhost:4000

If that didn't work, the first place to check is :bash:`prod.exs`. Make sure you have :elixir:`server: true` somewhere and there are no typos.

Also check out :ref:`troubleshooting`.

If it still doesn't work, don't hesitate to :ref:`contact us<help>`.

If everything works, continue to :ref:`set up deploys`.

.. _`buildpacks`:

Specify Buildpacks (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We rely on buildpacks to compile and build your release. We auto-detect a variety of buildpacks so you probably don't need this, but if you want
to specify your own buildpacks create a :bash:`.buildpacks` file with the buildpacks you want. For example,

.. code-block:: bash

    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-distillery.git

:bash:`heroku-buildpack-phoenix-static` is optional if you do not have Phoenix static assets. For more information about buildpacks, see :ref:`life of a deploy`.

Note, that the command that gets run in production depends on what your last buildpack is.

- If the last buildpack is :bash:`gigalixir-buildpack-distillery`, then the command run will be :bash:`/app/bin/foo foreground`.
- If the last buildpack is :bash:`heroku-buildpack-phoenix-static`, then the command run will be :bash:`mix phx.server`.
- If the last buildpack is :bash:`heroku-buildpack-elixir`, then the command run will be :bash:`mix run --no-halt`.

If your command is :bash:`mix run --no-halt`, but you are running Phoenix (just not the assets pipeline), make sure you set :elixir:`server: true` in :bash:`prod.exs`.

Set up Node Clustering with Libcluster (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to cluster nodes, you should install libcluster. For more information about installing libcluster, see :ref:`cluster your nodes`.

.. _`Mix`: https://hexdocs.pm/mix/Mix.html

Set Up Hot Upgrades with Git v2.9.0
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run hot upgrades, you send an extra http header when running :bash:`git push gigalixir master`. Extra HTTP headers are only supported in git 2.9.0 and above so make sure you upgrade if needed. For information on how to install the latest version of git on Ubuntu, see `this stackoverflow question <http://stackoverflow.com/questions/19109542/installing-latest-version-of-git-in-ubuntu>`_. For information on running hot upgrades, see :ref:`hot-upgrade` and :ref:`life-of-a-hot-upgrade`.

.. _`modifying existing app with Elixir releases`:

Using Elixir Releases
---------------------

Configuration and Secrets
^^^^^^^^^^^^^^^^^^^^^^^^^

Gigalixir auto-detects that you want to use Elixir Releases if you have a :bash:`config/releases.exs` file, so let's create one.

.. code-block:: bash

    echo "import Config" > config/releases.exs

The only configuration change we really need to do now is make sure the web server is started. Add the following to your :bash:`releases.exs`.

.. code-block:: bash

    config :gigalixir_getting_started, GigalixirGettingStartedWeb.Endpoint,
      server: true,
      http: [port: {:system, "PORT"}], # Needed for Phoenix 1.2 and 1.4. Doesn't hurt for 1.3.
      url: [host: System.get_env("APP_NAME") <> ".gigalixirapp.com", port: 443]

1. Replace :elixir:`:gigalixir_getting_started` with your app name e.g. :elixir:`:my_app`
2. Replace :elixir:`GigalixirGettingStartedWeb.Endpoint` with your endpoint module name. You can find your endpoint module name by running something like

   .. code-block:: bash

     grep -R "defmodule.*Endpoint" lib/

   Phoenix 1.2, 1.3, and 1.4 give different names so this is a common source of errors.

If you're using a free tier database, be sure to also set your pool size to 2 in :bash:`prod.exs`.

You don't have to worry about setting your :bash:`SECRET_KEY_BASE` config because we generate one and set it for you. 

Verify
^^^^^^

Let's make sure everything works.

First, try generating building static assets

.. code-block:: bash

    mix deps.get

    # generate static assets
    cd assets
    npm install
    npm run deploy
    cd ..
    mix phx.digest

and building a release locally

.. code-block:: bash

    export SECRET_KEY_BASE="$(mix phx.gen.secret)" 
    export DATABASE_URL="postgresql://user:pass@localhost:5432/foo"
    MIX_ENV=prod mix release 

and running it locally

.. code-block:: bash

    MIX_ENV=prod APP_NAME=gigalixir_getting_started PORT=4000 _build/prod/rel/gigalixir_getting_started/bin/gigalixir_getting_started start

Don't forget to replace :bash:`gigalixir_getting_started` with your own app name. Also, change/add the environment variables as needed.

Check it out.

.. code-block:: bash

    curl localhost:4000

If that didn't work, the first place to check is :bash:`prod.exs`. Make sure you have :elixir:`server: true` somewhere and there are no typos.

Also check out :ref:`troubleshooting`.

If it still doesn't work, don't hesitate to :ref:`contact us<help>`.

If everything works, commit the changes

.. code-block:: bash

    git add config/prod.exs assets/package-lock.json config/releases.exs
    git commit -m 'releases configuration'

Continue to :ref:`set up deploys`.

Specify Buildpacks (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We rely on buildpacks to compile and build your release. We auto-detect a variety of buildpacks so you probably don't need this, but if you want
to specify your own buildpacks create a :bash:`.buildpacks` file with the buildpacks you want. For example,

.. code-block:: bash

    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-releases.git

:bash:`heroku-buildpack-phoenix-static` is optional if you do not have Phoenix static assets. For more information about buildpacks, see :ref:`life of a deploy`.

Note, that the command that gets run in production depends on what your last buildpack is.

- If the last buildpack is :bash:`gigalixir-buildpack-releases`, then the command run will be :bash:`/app/bin/foo start`.
- If the last buildpack is :bash:`heroku-buildpack-phoenix-static`, then the command run will be :bash:`mix phx.server`.
- If the last buildpack is :bash:`heroku-buildpack-elixir`, then the command run will be :bash:`mix run --no-halt`.

If your command is :bash:`mix run --no-halt`, but you are running Phoenix (just not the assets pipeline), make sure you set :elixir:`server: true` in :bash:`prod.exs`.

