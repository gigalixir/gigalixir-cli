Configuration
~~~~~~~~~~~~~

.. _`configs`:

How to Configure an App
=======================

All app configuration is done through environment variables. You can get, set, and delete configs using the following commands. Note that setting configs automatically restarts your app.

.. code-block:: bash

    gigalixir config
    gigalixir config:set FOO=bar
    gigalixir config:unset FOO

.. _distillery-replace-os-vars:
.. _`app configuration`:

Environment variables and secrets
=================================

Environment variables in general are confusing because mix, distillery, and elixir releases all handle it differently. 

For distillery, I think `Distillery's Runtime Configuration`_ explains it better than I can, but in short, never use :elixir:`System.get_env("FOO")` in your :bash:`prod.exs`. Always use :elixir:`"${FOO}"` instead. Gigalixir automatically sets :bash:`REPLACE_OS_VARS=true` for you so you can skip that step.

For mix, always use :elixir:`System.get_env("FOO")` in your :bash:`prod.exs`.

For elixir releases, always use :elixir:`System.get_env("FOO")`, but put it in your :bash:`releases.exs` file if you want it loaded at runtime, which is usually what you want.

For example with distillery, to introduce a new :bash:`MY_CONFIG` env var is add something like this to your :bash:`prod.exs` file

.. Note:: Elixir 1.11 adds :bash:`config/runtime.exs`. If you use that instead, then you'll want to specify buildpacks since we can no longer detect if you want releases or mix mode. See :ref:`buildpacks-releases`.

.. code-block:: elixir

    config :myapp,
        my_config: "${MY_CONFIG}"

Then set the :bash:`MY_CONFIG` environment variable, by running

.. code-block:: bash

    gigalixir config:set MY_CONFIG=foo

In your app code, access the environment variable using

.. code-block:: elixir

    Application.get_env(:myapp, :my_config) == "foo"

.. _`Distillery's Runtime Configuration`: https://hexdocs.pm/distillery/config/runtime.html
.. _`Stack Overflow`: http://stackoverflow.com/
.. _`the gigalixir tag`: http://stackoverflow.com/questions/tagged/gigalixir


How to Copy Configuration Variables
===================================

.. code-block:: bash

    gigalixir config:copy -s $SOURCE_APP -d $DESTINATION_APP

Note, this will copy all configuration variables from the source to the destination. If there are duplicate keys, the destination config will be overwritten. Variables that only exist on the destination app will not be deleted.

.. _`hot-configure`:
.. _`hot configuration updates`:

How to Hot Configure an App
===========================

This feature is still a work in progress.

How to use a custom vm.args
===========================

Gigalixir generates a default :bash:`vm.args` file for you and tells Distillery to use it by setting the :bash:`VMARGS_PATH` environment variable. By default, it is set to :bash:`/release-config/vm.args`. If you want to use a custom :bash:`vm.args`, we recommend you follow these instructions.

Disable Gigalixir's default vm.args

.. code-block:: bash

    gigalixir config:set GIGALIXIR_DEFAULT_VMARGS=false

Create a :bash:`rel/vm.args` file in your repository. It might look something like `gigalixir-getting-started's vm.args file`_.

.. _`gigalixir-getting-started's vm.args file`: https://github.com/gigalixir/gigalixir-getting-started/blob/js/distillery-2.0/rel/vm.args

Lastly, you need to modify your distillery config so it knows where to find your :bash:`vm.args` file. Something like this. For a full example, see `gigalixir-getting-started's rel/config.exs file`_.

.. _`gigalixir-getting-started's rel/config.exs file`: https://github.com/gigalixir/gigalixir-getting-started/blob/js/distillery-2.0/rel/config.exs#L41

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

.. _`gigalixir release options`:

How to specify which release, environment, or profile to build
=========================================================================

Distillery
----------

If you have multiple releases defined in :bash:`rel/config.exs`, which is common for umbrella apps, you can specify which release to build
by setting a config variable on your app that controls the options passed to `mix distillery.release`. For example, you can pass the `--profile` option
using the command below.

.. code-block:: bash

    gigalixir config:set GIGALIXIR_RELEASE_OPTIONS="--profile=$RELEASE_NAME:$RELEASE_ENVIRONMENT"

With this config variable set on each of your gigalixir apps, when you deploy the same repo to each app, you'll get a different release.

If you have multiple Phoenix apps in the umbrella, instead of deploying each as a separate distillery release, you could also consider something like this `master_proxy <https://github.com/jesseshieh/master_proxy>`_ to proxy requests to the two apps.

Elixir Releases
---------------

If you want to pass options to :bash:`mix release` such as the release name, you can specify options with the :bash:`GIGALIXIR_RELEASE_OPTIONS` env var. 

For example, to build a different release other than the default, run

.. code-block:: bash

    gigalixir config:set GIGALIXIR_RELEASE_OPTIONS="my-release"

How do I use a private hex dependency?
======================================

First, take a look at the following page and generate an auth key for your org
https://hex.pm/docs/private#authenticating-on-ci-and-build-servers

Add something like this to your :bash:`elixir_buildpack.config` file

.. code-block:: bash

    hook_pre_fetch_dependencies="mix hex.organization auth myorg --key ${HEX_ORG_AUTH}"

Then run

.. code-block:: bash

    gigalixir config:set HEX_ORG_AUTH="authkeyhere"

How do I use webpack, yarn, bower, gulp, etc instead of brunch?
===============================================================

You can use a custom compile script. For more details, see https://github.com/gjaldon/heroku-buildpack-phoenix-static#compile
Here is an example script that we've used for webpack.

.. code-block:: bash

    cd $assets_dir
    node_modules/.bin/webpack -p

    cd $phoenix_dir
    mix "${phoenix_ex}.digest"

.. _`configure versions`:

How do I specify my Elixir, Erlang, Node, NPM, etc versions?
============================================================

Your Elixir and Erlang versions are handled by the heroku-buildpack-elixir buildpack. To configure, see the `heroku-buildpack-elixir configuration`_. In short, you specify them in a :bash:`elixir_buildpack.config` file.

Node and NPM versions are handled by the heroku-buildpack-phoenix-static buildpack. To configure, see the `heroku-buildpack-phoenix-static configuration <https://github.com/gjaldon/heroku-buildpack-phoenix-static#configuration>`_. In short, you specify them in a :bash:`phoenix_static_buildpack.config` file.

Supported Elixir and erlang versions can be found at https://github.com/HashNuke/heroku-buildpack-elixir#version-support

.. _`heroku-buildpack-elixir configuration`: https://github.com/HashNuke/heroku-buildpack-elixir#configuration

How do I specify which buildpacks I want to use?
================================================

Normally, the buildpack you need is auto-detected for you, but in some cases, you may want to specify which buildpacks you want to use. To do this, create a :bash:`.buildpacks` file and list each buildpack you want to use. For example, the default buildpacks for Elixir apps using distillery would look like this

.. code-block:: bash

    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-distillery.git


The default buildpacks for Elixir apps running mix looks like this

.. code-block:: bash

    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-mix.git

Note the last buildpack. It's there to make sure your :bash:`Procfile` is set up correctly to run on gigalixir. It basically makes sure you have your node name and cookie set correctly so that remote console, migrate, observer, etc will work.

.. _`custom procfile`:

Can I use a custom Procfile?
============================

Definitely! If you are using mix (not distillery) and you have a :bash:`Procfile` at the root of your repo, we'll use it instead of `the default one <https://github.com/gigalixir/gigalixir-run/blob/master/Procfile>`_. If you are using Distillery, you'll have to use distillery overlays to include the Procfile inside your release tarball i.e. slug. If you are using Elixir releases, then you want to place the Procfile inside rel/overlays so that it gets copied into the release tarball.

The only gotcha is that if you want remote console to work, you'll want to make sure the node name and cookie are set properly. For example, your :bash:`Procfile` should look something like this.

.. code-block:: bash

  web: elixir --name $MY_NODE_NAME --cookie $MY_COOKIE -S mix phoenix.server

Can I choose my operating system, stack, or image?
==================================================

We have 2 stacks you can choose from: gigalixir-18, and gigalixir-20.
These stacks are based on Heroku's heroku-18 and heroku-20, respectively which are based on Ubuntu 18 and 20 respectively.
gigalixir-20 is the default.

Note that some older apps on gigalixir might be running gigalixir-14 or gigalixir-16, based on Heroku's cedar-14 and heroku-16, which will be end-of-life on November 2nd, 2020 and May 1st, 2021. gigalixir-14 and gigalixir-16 will be also be end-of-life on the same day. See 
https://devcenter.heroku.com/changelog-items/1757 and https://help.heroku.com/0S5P41DC/heroku-16-end-of-life-faq

You can choose your stack when you create your app with 

.. code-block:: bash

    gigalixir create --stack gigalixir-20
    
or you can change it later on with

.. code-block:: bash

    # Note that depending on the situation, you may have to re-deploy your app after changing the stack in case
    # the shared libraries have changed locations.
    gigalixir stack:set --stack gigalixir-20

You can see what stack you are running with :bash:`gigalixir apps:info` or :bash:`gigalixir ps`.

For information about what packages are available in each stack, see https://devcenter.heroku.com/articles/stack-packages as well as the Dockerfiles at https://github.com/gigalixir/gigalixir-run

Can I run my app in AWS instead of Google Cloud Platform? What about Europe?
============================================================================

Yes, if your current infrastructure is on AWS, you'll probably want to run your gigalixir app on AWS too. Or if most of your users are in Europe, you probably want to host your app in Europe. We currently support GCP v2018-us-central1 and GCP europe-west1 as well as AWS us-east-1 and AWS us-west-2. When creating your app with :bash:`gigalixir create` simply specify the :bash:`--cloud=aws` and :bash:`--region=us-east-1` options.

Once the app is created, it's difficult to migrate to another region. If you want to do this, Heroku's guide is a good overview of what you should consider. If you don't mind downtime, the transition could be easy, but unfortunately gigalixir isn't able to do it for you with a button press. See https://devcenter.heroku.com/articles/app-migration

One thing to keep in mind is that Gigalixir Postgres databases are as of right now only available in GCP/v2018-us-central1 and GCP/europe-west1, however, we can set up a database for you in AWS manually if you like. Just :ref:`contact us<help>` and we'll create one for you. We plan to add AWS to the Gigalixir CLI soon. 

If you don't see the region you want, please :ref:`contact us<help>` and let us know. We open new regions based purely on demand.

What built-in environment variables are available to my app?
============================================================

SOURCE_VERSION contains the current SHA

HOST_INDEX contains the index of the replica. The hostname for each replica is randomly generated which can be a problem for services like DataDog and NewRelic who charge by the host. We also keep a sort of ordered list of your replicas that you can use to report hostnames to keep your number of hosts low. Each replica currently running will have a different HOST_INDEX, but once a replica is terminated, its HOST_INDEX can be re-used in another replica.

APP_NAME contains your gigalixir app name.

APP_KEY contains the app specific key you need to fetch information about your app from inside the replica. You probably don't need to use this unless you're doing something really low level, but it's there if you need it. 

ERLANG_COOKIE contains a randomly generated UUID that we use as your erlang distribution cookie. We set it for you automatically and it's used in your default vm.args file so you don't need to mess with anything, but it's here if you should want to use it.

LOGPLEX_TOKEN contains the app specific token we use to send your app logs to logplex. Logplex is our central log router which handles aggregating, draining, and tailing your logs. You can use this if you want to do something custom with logs that can't be done by printing to stdout from your app.

MY_POD_IP contains your replica/container/pod's ip address.

PORT contains the port your app needs to listen on to pass health checks and receive traffic. It is almost always 4000, but we reserve the right to change or randomize it.

SECRET_KEY_BASE contains a randomly generated string that we use as your Elixir app's secret key base.

HOME contains the location of your app's home directly. It is almost always /app, but we reserve the right to change it.

How can I get a static outgoing ip address?
===========================================

Gigalixir doesn't support static outgoing ip addresses at the moment, but some customers have had success using IPBurger.com which is affordable and simple. Just configure your http client to make requests through the proxy. For example, with HTTPoison, something like this

.. code-block:: elixir

    HTTPoison.get(url, [], [proxy: {:socks5, String.to_charlist("server_domain"), port_num}, socks5_user: "username", socks5_pass: "password"])

