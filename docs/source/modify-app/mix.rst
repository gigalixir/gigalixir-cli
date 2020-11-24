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
       url: [host: System.get_env("APP_NAME") <> ".gigalixirapp.com", port: 443],
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

