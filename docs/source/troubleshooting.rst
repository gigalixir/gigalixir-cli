.. _`troubleshooting-page`:

Troubleshooting
~~~~~~~~~~~~~~~

Troubleshooting
===============

Also see :ref:`known-issues`

If your app isn't working and you're seeing either 504s or an "unhealthy" message, you're in the right place. The first places to check for clues are `gigalixir logs` and `gigalixir ps`. For example, check if the :bash:`lastState` shows :bash:`OOMKilled`, which indicates your app is using more memory than it has provisioned. If nothing pops out at you there, keep reading.

A 504 means that our load balancer isn't able to reach your app. This is usually because the app isn't running. An app that isn't running
is usually failing health checks and we constantly restart apps that fail health checks in hopes that it will become healthy.

If you've just deployed, and you're not seeing 504s, but you're still seeing the old version of your app instead of the new version, it's the same problem. This happens when the new version does not pass health checks. When the new version doesn't pass health checks, we don't route traffic to it and we don't terminate the old version.

Our health checks simply check that your app is listening on port $PORT. If you're running a non-HTTP Elixir app, but need to just get health checks to pass, take a look at https://github.com/jesseshieh/elixir-tcp-accept-and-close

If you're using Mix, see `troubleshooting mix`_. 

If you're using Distillery, see `troubleshooting distillery`_. 

If you're using Elixir Releases, see `troubleshooting Elixir releases`_. 

.. _`troubleshooting mix`:

Mix
---

Let's verify that your app works locally.

Run the following commands

.. code-block:: bash

    mix deps.get
    mix compile
    SECRET_KEY_BASE="$(mix phx.gen.secret)" MIX_ENV=prod DATABASE_URL="postgresql://user:pass@localhost:5432/foo" PORT=4000 mix phx.server
    curl localhost:4000

If it doesn't work, the first thing to check is your :bash:`prod.exs` file. Often, it is missing an :elixir:`http` configuration or there is a typo in the :elixir:`FooWeb.Endpoint` module name.

If everything works locally, you might be running a different version of Elixir in production. See :ref:`configure versions`.

Another possibility is that your app is running out of memory and can't start up properly. To fix this, try scaling up. See :ref:`scaling`.

If the above commands still do not succeed and your app is open source, then please :ref:`contact us for help<help>`. If not open source, :ref:`contact us<help>` anyway and we'll do our best to help you.

.. _`troubleshooting distillery`:

Distillery
----------

If you're having trouble getting things working, you can verify a few things locally.

First, try generating and running a Distillery release locally by running

.. code-block:: bash

    mix deps.get
    mix compile
    export SECRET_KEY_BASE="$(mix phx.gen.secret)"
    export DATABASE_URL="postgresql://user:pass@localhost:5432/foo" 
    MIX_ENV=prod mix distillery.release --env=prod
    # if you are a running distillery below 2.1, then run this instead: MIX_ENV=prod mix release --env=prod
    APP_NAME=gigalixir_getting_started
    MY_HOSTNAME=example.com MY_COOKIE=secret REPLACE_OS_VARS=true MY_NODE_NAME=foo@127.0.0.1 PORT=4000 _build/prod/rel/$APP_NAME/bin/$APP_NAME foreground
    curl localhost:4000

Don't forget to replace :bash:`gigalixir_getting_started` with your own app name. Also, change/add the environment variables as needed.

You can safely ignore Kubernetes errors like :bash:`[libcluster:k8s_example]` errors because you probably aren't running inside Kubernetes.

If they don't work, the first place to check is :bash:`prod.exs`. Make sure you have :elixir:`server: true` somewhere and there are no typos.

In case static assets don't show up, you can try the following and then re-run the commands above.

.. code-block:: bash

    cd assets
    npm install
    npm run deploy
    cd ..
    mix phx.digest

If your problem is with one of the buildpacks, try running the full build using Docker and Herokuish by running

.. code-block:: bash

    APP_ROOT=$(pwd)
    rm -rf /tmp/gigalixir/cache
    rm -rf _build
    mkdir -p /tmp/gigalixir/cache
    docker run -it --rm -v $APP_ROOT:/tmp/app -v /tmp/gigalixir/cache/:/tmp/cache us.gcr.io/gigalixir-152404/build-18

Or to inspect closer, run

.. code-block:: bash

    docker run -it --rm -v $APP_ROOT:/tmp/app -v /tmp/gigalixir/cache/:/tmp/cache --entrypoint=/bin/bash us.gcr.io/gigalixir-152404/build-18

    # and then inside the container run
    build-slug

    # inspect /app folder
    # check /tmp/cache

If everything works locally, you might be running a different version of Elixir in production. See :ref:`configure versions`.

Another possibility is that your app is running out of memory and can't start up properly. To fix this, try scaling up. See :ref:`scaling`.

If the above commands still do not succeed and your app is open source, then please :ref:`contact us for help<help>`. If not open source, :ref:`contact us<help>` anyway and we'll do our best to help you.

.. _`troubleshooting Elixir releases`:

Elixir Releases
---------------

If you're having trouble getting things working, you can verify a few things locally.

First, try generating and running a release locally by running

.. code-block:: bash

    mix deps.get
    export SECRET_KEY_BASE="$(mix phx.gen.secret)"
    export DATABASE_URL="postgresql://user:pass@localhost:5432/foo" 
    MIX_ENV=prod mix release
    APP_NAME=gigalixir_getting_started
    PORT=4000 _build/prod/rel/$APP_NAME/bin/$APP_NAME start
    curl localhost:4000

Don't forget to replace :bash:`gigalixir_getting_started` with your own app name. Also, change/add the environment variables as needed.

You can safely ignore Kubernetes errors like :bash:`[libcluster:k8s_example]` errors because you probably aren't running inside Kubernetes.

If they don't work, the first place to check is :bash:`prod.exs`. Make sure you have :elixir:`server: true` somewhere and there are no typos.

In case static assets don't show up, you can try the following and then re-run the commands above.

.. code-block:: bash

    cd assets
    npm install
    npm run deploy
    cd ..
    mix phx.digest

If your problem is with one of the buildpacks, try running the full build using Docker and Herokuish by running

.. code-block:: bash

    APP_ROOT=$(pwd)
    rm -rf /tmp/gigalixir/cache
    rm -rf _build
    mkdir -p /tmp/gigalixir/cache
    docker run -it --rm -v $APP_ROOT:/tmp/app -v /tmp/gigalixir/cache/:/tmp/cache us.gcr.io/gigalixir-152404/build-18

Or to inspect closer, run

.. code-block:: bash

    docker run -it --rm -v $APP_ROOT:/tmp/app -v /tmp/gigalixir/cache/:/tmp/cache --entrypoint=/bin/bash us.gcr.io/gigalixir-152404/build-18

    # and then inside the container run
    build-slug

    # inspect /app folder
    # check /tmp/cache

If everything works locally, you might be running a different version of Elixir in production. See :ref:`configure versions`.

Another possibility is that your app is running out of memory and can't start up properly. To fix this, try scaling up. See :ref:`scaling`.

If the above commands still do not succeed and your app is open source, then please :ref:`contact us for help<help>`. If not open source, :ref:`contact us<help>` anyway and we'll do our best to help you.


.. _`known-issues`:

Known Issues
============

  -  warning: the --remsh option will be ignored because IEx is running on limited shell

      - Try running :bash:`export TERM=xterm` and trying again.

  -  git push hangs and then times out

      - Try running :bash:`git config --local http.version HTTP/1.1`. We've seen this issue happen with many customers and we've been able to narrow it down to an HTTP/2 issue of some kind with some versions of curl or git, but haven't been able to reproduce it. Many customers report that switching to HTTP/1.1 seems to fix the issue. For more information, try setting :bash:`GIT_TRACE=1 GIT_CURL_VERBOSE=1` when pushing. If you can also send us the output, that would be helpful. Often what we'll see in the output is something like :bash:`17 bytes stray data read before trying h2 connection`.

  - (FunctionClauseError) no function clause matching in List.first/1 when running `gigalixir ps:migrate`

      - If you have a `releases` config in your mix.exs, make sure it is named the same as your app a few lines above. This is something we need to figure out how to fix, but in the meantime, we need the release name to match the app name. Let us know if you encounter this issue so we can bump the priority!

  -  Warning: Multiple default buildpacks reported the ability to handle this app. The first buildpack in the list below will be used.

      - This warning is safe to ignore. It is a temporary warning due to a workaround.

  - curl: (56) GnuTLS recv error (-110): The TLS connection was non-properly terminated.

      - Currently, the load balancer for domains under gigalixirapp.com has a request timeout of 30 seconds. If your request takes longer than 30 seconds to respond, the load balancer cuts the connection. Often, the cryptic error message you will see when using curl is the above. The load balancer for custom domains does not have this problem.

  - php apps don't work well with the stack gigalixir-18. If you are deploying php, please downgrade your stack to gigalixir-16 with something like :bash:`gigalixir stack:set -s gigalixir-16`. The reason is because gigalixir-18 is based on heroku-18 which does not have libreadline.so preinstalled for some reason where gigalixir-16, based on heroku-16, does.

  - Did not find exactly 1 release

      - This can happen for a few different reasons, but usually clearing your build cache or retrying will resolve it. In some cases, if you added :bash:`release=true` to your :bash:`elixir_buildpack.config` file, it caches the release and is never deleted even when you bump the app version in your mix.exs. This results in two release folders and gigalixir does not know which release you intend to deploy and errors out. Clearing the cache resolves this issue. In some cases, if two deploys are running concurrently, you can end up with two release tarballs at the same time. This is a known issue we intend to fix, but usually re-running the deploy will work fine since it is a race condition.

Common Errors
-------------

A good first thing to try when you get a `git push` error is :ref:`cleaning your build cache<cleaning your build cache>`.

    - My deploy succeeded, but nothing happened.

        - When :bash:`git push gigalixir` succeeds, it means your code was compiled and built without any problems, but there can still be problems during runtime. Other platforms will just let your app fail, but gigalixir performs tcp health checks on port 4000 on your new release before terminating the old release. So if your new release is failing health checks, it can appear as if nothing is happening because in a sense, nothing is. Check :bash:`gigalixir logs` for any startup errors.

    - My app takes a long time to startup.

        - Most likely, this is because your CPU reservation isn't enough and there isn't any extra CPU available on the machine to give you. Try scaling up your instance sizes. See :ref:`scale`.

    - failed to connect: ** (Postgrex.Error) FATAL 53300 (too_many_connections): too many connections for database

        - If you have a free tier database, the number of connections is limited. Try lowering the :elixir:`pool_size` in your :bash:`prod.exs` to 2, or if you're using :bash:`prod.secret.exs` setting the :bash:`POOL_SIZE` environment variable using :bash:`gigalixir config:set POOL_SIZE=2`.

    - ~/.netrc access too permissive: access permissions must restrict access to only the owner

        - run :bash:`chmod og-rwx ~/.netrc`

    - :bash:`git push gigalixir` asks for my password

        - First try running :bash:`gigalixir login` and try again. If that doesn't work, try resetting your git remote by running :bash:`gigalixir git:remote $APP` and trying again.

    - remote: cp: cannot overwrite directory ‘/tmp/cache/node_modules/phoenix_html’ with non-directory

        - Try :ref:`cleaning your build cache`. Looks like something changed in your app that makes the cache non-overwritable.

    - remote: cp: cannot stat '/tmp/cache/node_modules/': No such file or directory

        - Try :ref:`cleaning your build cache`. 

    - :elixir:`conn.remote_ip` has :elixir:`127.0.0.1` instead of the real client ip

        - Try using https://github.com/kbrw/plug_forwarded_peer or otherwise use the :elixir:`X-Forwarded-For` header instead. Gigalixir apps run behind load balancers which write the real client ip in that header.

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

        - This means the Phoenix static buildpack could not find your assets folder. Either specify where it is or remove the buildpack. To specify, configure the buildpack following https://github.com/gjaldon/heroku-buildpack-phoenix-static. To remove, create a :bash:`.buildpacks` file with the buildpacks you need. For example, just :bash:`https://github.com/HashNuke/heroku-buildpack-elixir`

    - SMTP/Email Network Failures e.g. {:network_failure, 'smtp.mailgun.org', {:error, :timeout}}

        - Google Cloud Engine does not allow certain email ports like 587. See https://cloud.google.com/compute/docs/tutorials/sending-mail/
          Try using port 2525. See https://cloud.google.com/compute/docs/tutorials/sending-mail/using-mailgun

    - unknown command: MIX_ENV=prod mix phx.server

        - If you are you are using a custom Procfile with an environment variable at the front of the command, you'll get this error. Try adding :bash:`env` to the front of the command. See https://github.com/ddollar/foreman/issues/265. We use the most command Ruby Foreman which behaves differently from Heroku's for this situation.

    - init terminating in do_boot ({cannot get bootfile,no_dot_erlang.boot})

        - This is an issue described here: https://github.com/bitwalker/distillery/issues/426
          Try either upgrading Distillery to 1.5.3 or downgrading OTP below 21.

    - Could not invoke task "release": --env : Unknown option

        - This happens when you upgrade to elixir 1.9, but are still using distillery older than 2.1. Upgrade distillery to fix this issue, but be sure to also change your rel/config.exs file. Mix.Releases.Config needs to be renamed to Distillery.Releases.Config

    - sh: 1: mix: not found

        - If you have an old Phoenix project where a :bash:`package.json` file exists in the project root folder, the :bash:`herokuish` buildpack might `mistakenly recognize it <https://github.com/gliderlabs/herokuish/issues/232>`_ as a Node.js project, and thus fail to build it properly. You may need to manually add a :bash:`.buildpacks` file in your root folder, as documented in the "Specify Buildpacks" sections above.

.. _`contact us for help`:
.. _`contact us`:
.. _`help`:

Support/Help
============

Feel free to email help@gigalixir.com for any questions or issues, we generally respond quickly.

