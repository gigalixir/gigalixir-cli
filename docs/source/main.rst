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
  - *API Key*: Every user has an API Key which is used to authenticate most API requests. You get one when you login and you can regenerate it at any time. It never expires.
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

  - https://github.com/HashNuke/heroku-buildpack-elixir.git

    - To run mix compile
    - If you want, you can `configure this buildpack <https://github.com/HashNuke/heroku-buildpack-elixir#configuration>`_.

  - https://github.com/gjaldon/heroku-buildpack-phoenix-static.git

    - To run mix phx.digest
    - This is only included if you have an assets folder present.

  - https://github.com/gigalixir/gigalixir-buildpack-distillery.git

    - To run mix release or mix distillery.release
    - This is only run if you have a rel/config.exs file present.

  - https://github.com/gigalixir/gigalixir-buildpack-releases

    - To run mix release if you are running Elixir 1.9 and using the built-in releases
    - This is only run if you have a config/releases.exs file present.

  - https://github.com/gigalixir/gigalixir-buildpack-mix.git

    - To set up your Procfile correctly
    - This is only run if you *don't* have a rel/config.exs file present.

We only build the master branch and ignore other branches. When building, we cache compiled files and dependencies so you do not have to repeat the work on every deploy. We support git submodules.

Once your slug is built, we upload it to slug storage and we combine it with a config to create a new release for your app. The release is tagged with a :bash:`version` number which you can use later on if you need to rollback to this release.

Then we create or update your Kubernetes configuration to deploy the app. We create a separate Kubernetes namespace for every app, a service account, an ingress for HTTP traffic, an ingress for SSH traffic, a TLS certificate, a service, and finally a deployment which creates pods and containers.

The `container that runs your app`_ is a derivative of `heroku/cedar:14`_. The entrypoint is a script that sets up necessary environment variables including those from your :ref:`app configuration<app configuration>`. It also starts an SSH server, installs your SSH keys, downloads the current slug, and executes it. We automatically generate and set up your erlang cookie, distributed node name, and Phoenix secret key base for you. We also set up the Kubernetes permissions and libcluster selector you need to :ref:`cluster your nodes<cluster your nodes>`. We poll for your SSH keys every minute in case they have changed.

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

.. _`cleaning your build cache`:

How to clean your build cache
=============================

There is an extra flag you can pass to clean your cache before building in case you need it, but you need git 2.9.0 or higher for it to work. For information on how to install the latest version of git on Ubuntu, see `this stackoverflow question <http://stackoverflow.com/questions/19109542/installing-latest-version-of-git-in-ubuntu>`_.

.. code-block:: bash

    git -c http.extraheader="GIGALIXIR-CLEAN: true" push gigalixir master

Can I run my app in AWS instead of Google Cloud Platform? What about Europe?
============================================================================

Yes, if your current infrastructure is on AWS, you'll probably want to run your gigalixir app on AWS too. Or if most of your users are in Europe, you probably want to host your app in Europe. We currently support GCP v2018-us-central1 and GCP europe-west1 as well as AWS us-east-1 and AWS us-west-2. When creating your app with :bash:`gigalixir create` simply specify the :bash:`--cloud=aws` and :bash:`--region=us-east-1` options.

Once the app is created, it's difficult to migrate to another region. If you want to do this, Heroku's guide is a good overview of what you should consider. If you don't mind downtime, the transition could be easy, but unfortunately gigalixir isn't able to do it for you with a button press. See https://devcenter.heroku.com/articles/app-migration

One thing to keep in mind is that Gigalixir Postgres databases are as of right now only available in GCP/v2018-us-central1 and GCP/europe-west1, however, we can set up a database for you in AWS manually if you like. Just :ref:`contact us<help>` and we'll create one for you. We plan to add AWS to the Gigalixir CLI soon. 

If you don't see the region you want, please :ref:`contact us<help>` and let us know. We open new regions based purely on demand.


.. _`cluster your nodes`:
.. _`clustering`:

Clustering Nodes
================

First of all, be sure you are using either Distillery or Elixir Releases for your deploys and not mix. Clustering won't work with just mix. For instructions on using Distillery or Releases, see :ref:`mix vs distillery`.

We use libcluster to manage node clustering. For more information, see `libcluster's documentation`_.

To install libcluster, add this to the deps list in :bash:`mix.exs`

.. code-block:: elixir

    {:libcluster, "~> 3.2"}

If you are on Elixir 1.3 or lower, add :elixir:`libcluster` and :elixir:`:ssl` to your applications list. Elixir 1.4 and up detect your applications list for you.

Next, add the following to the existing :elixir:`start` function in your :bash:`application.ex` file. Remember to replace :elixir:`GigalixirGettingStarted` with your application name.

.. code-block:: elixir

  def start(_type, _args) do
    topologies = Application.get_env(:libcluster, :topologies) || []

    children = [
      {Cluster.Supervisor, [topologies, [name: GigalixirGettingStarted.ClusterSupervisor]]},
      ... # other children
    ]
    ...
  end

Your app configuration needs to have something like this in it. For a full example, see `gigalixir-getting-started's prod.exs file`_.

.. code-block:: elixir

    ...
    config :libcluster,
      topologies: [
        k8s_example: [
          strategy: Cluster.Strategy.Kubernetes,
          config: [
            # For Elixir Releases, use System.get_env instead of the distillery env vars below.
            kubernetes_selector: "${LIBCLUSTER_KUBERNETES_SELECTOR}",
            kubernetes_node_basename: "${LIBCLUSTER_KUBERNETES_NODE_BASENAME}"]]]
    ...

Gigalixir handles permissions so that you have access to Kubernetes endpoints and we automatically set your node name and erlang cookie so that your nodes can reach each other. We don't firewall each container from each other like Heroku does. We also automatically set the environment variables :bash:`LIBCLUSTER_KUBERNETES_SELECTOR`, :bash:`LIBCLUSTER_KUBERNETES_NODE_BASENAME`, :bash:`APP_NAME`, and :bash:`MY_POD_IP` for you. See `gigalixir-run`_ for more details.

.. _`libcluster's documentation`: https://github.com/bitwalker/libcluster
.. _`gigalixir-getting-started's prod.exs file`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/config/prod.exs#L68
.. _`gigalixir-getting-started's mix.exs file`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/mix.exs
.. _`gigalixir-run`: https://github.com/gigalixir/gigalixir-run

Releases
========

One common pitfall for beginners is how releases differ from running apps with mix. In development, you typically have access to mix tasks to run your app, migrate your database, etc. In production, we use releases. With releases, your code is distributed in it's compiled form and is almost no different from an Erlang release. You no longer have access to mix commands. However, in return, you also have access to hot upgrades and smaller slug sizes, and a "single package which can be deployed anywhere, independently of an Erlang/Elixir installation. No dependencies, no hassle" [1].

[1]: https://github.com/bitwalker/distillery

Monitoring
==========

Gigalixir doesn't provide any monitoring out of the box, but we are working on it. Also, you can always use a remote observer to inspect your node. See, :ref:`remote observer`.




How to Set Up Distributed Phoenix Channels
==========================================

If you have successfully clustered your nodes, then distributed Phoenix channels *just work* out of
the box. No need to follow any of the steps described in `Running Elixir and Phoenix projects on a
cluster of nodes`_. See more information on how to `cluster your nodes`_.




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
    # e.g. gigalixir drains:add https://user:$TIMBER_API_KEY@logs.timber.io/sources/$TIMBER_SOURCE_ID/frames
    # e.g. gigalixir drains:add syslog+tls://logs123.papertrailapp.com:12345

To show all your drains, run

.. code-block:: bash

    gigalixir drains

To delete a drain, run

.. code-block:: bash

    gigalixir drains:remove $DRAIN_ID

.. _`Timber`: https://timber.io

.. _managing-ssh-keys:

How to SSH into a Production Container
======================================

If your app is running, but not behaving, SSH'ing in might give you some insight into what is happening. A major caveat, though, is that the app has to be running. If it isn't running, then it isn't passing health checks, and we'll keep restarting the entire container. You won't be able to SSH into a container that is restarting non-stop. If your app isn't running, try taking a look at :ref:`troubleshooting-page`.

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

.. _`jobs`:

How to Run Jobs
===============

There are many ways to run one-off jobs and tasks. You can run them in the container your app is running or you can spin up a new container that runs the command and then destroys itself.

To run a command in your app container, run

.. code-block:: bash

    gigalixir ps:run $COMMAND
    # if you're using distillery, you'll probably want $COMMAND to be something like `bin/app eval 'IO.inspect Node.self'`
    # if you're using mix, you'll probably want $COMMAND to be something like `mix ecto.migrate`

To run a command in a separate container, run

.. code-block:: bash

    gigalixir run $COMMAND
    # if you're using distillery, you'll probably want $COMMAND to be something like `bin/app eval 'IO.inspect Node.self'`
    # if you're using mix, you'll probably want $COMMAND to be something like `mix ecto.migrate`

.. For an example task, see `gigalixir-getting-started's migrate task`_.

The task is not run on the same node that your app is running in. Jobs are killed after 5 minutes.

If you're using the distillery, note that because we start a separate container to run the job, if you need any applications started such as your :elixir:`Repo`, use :elixir:`Application.ensure_all_started/2`. Also, be sure to stop all applications when done, otherwise your job will never complete and just hang until it times out.

.. For more information about running migrations with Distillery, see `Distillery's Running Migrations`_.

Distillery commands currently do not support passing arguments into the job.

We prepend :elixir:`Elixir.` to your module name to let the BEAM virtual machine know that you want to run an Elixir module rather than an Erlang module. The BEAM doesn't know the difference between Elixir code and Erlang code once it is compiled down, but compiled Elixir code is namespaced under the Elixir module.

The size of the container that runs your job will be the same size as the app containers and billed the same way, based on replica-size-seconds. See, :ref:`pricing`.

.. _`gigalixir-getting-started's migrate task`: https://github.com/gigalixir/gigalixir-getting-started/blob/js/hooks/lib/tasks.ex
.. _`Distillery's Running Migrations`: https://hexdocs.pm/distillery/running-migrations.html



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

.. _`remote observer`:
.. _`observer`:

How to Launch a Remote Observer
===============================

To connect a remote observer, you need to be using Distillery or Elixir releases. See :ref:`mix vs distillery`.

In order to run a remote observer, you need to set up your SSH keys. It could take up to a minute for the SSH keys to update in your containers.

.. code-block:: bash

    gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_rsa.pub)"

Because Observer runs on your local machine and connects to a production node by joining the production cluster, you first have to have clustering set up. You don't have to have multiple nodes, but you need to follow the instructions in :ref:`clustering`.

You also need to have :elixir:`runtime_tools` in your application list in your :bash:`mix.exs` file. Phoenix 1.3 and later adds it by default, but you have to add it yourself in Phoenix 1.2.

Your local machine also needs to have :bash:`lsof`.

You should also make sure your app has enough memory. Even though observer itself is running on your local machine, the remote machine still needs quite a bit of memory. For a basic app, make sure you have at least 500mb memory (size 0.5).

Then, to launch observer and connect it to a production node, run

.. code-block:: bash

    gigalixir ps:observer

and follow the instructions. It will prompt you for your local sudo password so it can modify iptables rules. This connects to a random container using consistent hashing. We don't currently allow you to specify which container you want to connect to, but it will connect to the same container each time based on a hash of your ip address.


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




How can I get the current SHA my app is running?
================================================

There are a number of environment variables set in your app container. :bash:`SOURCE_VERSION` contains your current SHA. 

What environment variables are available to my app?
===================================================

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

Does Gigalixir have any web hooks?
==================================

We haven't built-in any web hooks, but most of what you need can be accomplished with buildpacks at build time and distillery hooks or modifying your Procfile.

To hit a web hook when building your app, you can use https://github.com/jesseshieh/buildpack-webhook

For runtime prestart hooks, see https://hexdocs.pm/distillery/extensibility/boot_hooks.html

Or if you aren't using distillery, see :ref:`custom procfile`. You can add any command you like.


How secure is Gigalixir?
========================

Gigalixir takes security very, very seriously.

#. Every app exists in its own Kubernetes namespaces and we use Kubernetes role-based access controls to ensure no other apps have access to your app or its metadata.
#. Your build environment is fully isolated using Docker containers.
#. Your slugs are authenticated using `Signed URLs`_.
#. All API endpoints are authenticated using API keys instead of your password. API keys can be invalidated at any time by regenerating a new one.
#. Remote console and remote observer use SSH tunnels to secure traffic.
#. Erlang does not encrypt distribution traffic between your nodes by default, but you can `set it up to use SSL`_. For an extra layer of security, we route distribution traffic directly to each node so no other apps can sniff the traffic.
#. We use `Stripe`_ to manage payment methods so Gigalixir never knows your credit card number.
#. Passwords and app configs are encrypted at rest using `Cloak`_.
#. Traffic between Gigalixir services and components is TLS encrypted.

.. _`Signed URLs`: https://cloud.google.com/storage/docs/access-control/signed-urls
.. _`Cloak`: https://github.com/danielberkompas/cloak
.. _`Stripe`: https://stripe.com/
.. _`set it up to use SSL`: http://erlang.org/doc/apps/ssl/ssl_distribution.html

Are there any benchmarks?
=========================

Take a look at our `benchmark data <https://docs.google.com/spreadsheets/d/1KWES-cSH_qXZQN9y3yu6HDSTdweIbZQuL12qLvkJnBo/edit?usp=sharing>`_.

Moved
=====

.. _`getting-started-guide`:

Getting Started Guide
---------------------

This section has moved here: :ref:`quick start`

.. _`deploy-types`:

Mix vs Distillery vs Elixir Releases
------------------------------------

This section has moved here: :ref:`mix vs distillery`

.. _`troubleshooting`:

Troubleshooting
---------------

This section has moved here: :ref:`troubleshooting-page`

.. _`Distillery appup documentation`: https://hexdocs.pm/distillery/upgrades-and-downgrades.html#appups
.. _`Distillery's upgrade command`: https://hexdocs.pm/distillery/walkthrough.html#deploying-an-upgrade
.. _`heroku/cedar:14`: https://hub.docker.com/r/heroku/cedar/
.. _`container that runs your app`: https://github.com/gigalixir/gigalixir-run
.. _`herokuish`: https://github.com/gliderlabs/herokuish
.. _`PaperTrail`: https://papertrailapp.com/
.. _`Running Elixir and Phoenix projects on a cluster of nodes`: https://dockyard.com/blog/2016/01/28/running-elixir-and-phoenix-projects-on-a-cluster-of-nodes
.. _`The Twelve-Factor App's Config Factor`: https://12factor.net/config
.. _`Herokuish`: https://github.com/gliderlabs/herokuish
.. _`gigalixir-getting-started`: https://github.com/gigalixir/gigalixir-getting-started
