.. _`modifying existing app with distillery`:

Using Distillery
----------------

For an example app that uses distillery and works on gigalixir, see https://github.com/gigalixir/gigalixir-getting-started

Install Distillery to Build Releases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In short, you'll need to add something like this to the :elixir:`deps` list in :bash:`mix.exs`

.. code-block:: elixir

    {:distillery, "~> 2.1"}

.. Important:: If you are running Elixir 1.9, then you *must* use distillery 2.1 or greater. Elixir 1.9 and distillery below 2.1 both use `mix release` and Elixir's always takes precedence. Distillery 2.1 renames the task to `mix distillery.release`.

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

.. Attention:: :elixir:`server: true` **is very important and is commonly left out. Make sure you have this line.**

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

First, try building static assets

.. code-block:: bash

    mix deps.get
    cd assets
    npm install
    npm run deploy
    cd ..
    mix phx.digest

and building a Distillery release locally

.. code-block:: bash

    SECRET_KEY_BASE="$(mix phx.gen.secret)" MIX_ENV=prod DATABASE_URL="postgresql://user:pass@localhost:5432/foo" mix distillery.release --env=prod
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

To run hot upgrades, you send an extra http header when running :bash:`git push gigalixir`. Extra HTTP headers are only supported in git 2.9.0 and above so make sure you upgrade if needed. For information on how to install the latest version of git on Ubuntu, see `this stackoverflow question <http://stackoverflow.com/questions/19109542/installing-latest-version-of-git-in-ubuntu>`_. For information on running hot upgrades, see :ref:`hot-upgrade` and :ref:`life-of-a-hot-upgrade`.


