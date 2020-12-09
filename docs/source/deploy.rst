Deployment & CI/CD
~~~~~~~~~~~~~~~~~~

How to Deploy an App
====================

Deploying an app is done using a git push, the same way you would push code to github. For more information about how this works, see :ref:`life of a deploy`.

.. code-block:: bash

    git push gigalixir

.. _`cleaning your build cache`:

How to clean your build cache
=============================

There is an extra flag you can pass to clean your cache before building in case you need it, but you need git 2.9.0 or higher for it to work. For information on how to install the latest version of git on Ubuntu, see `this stackoverflow question <http://stackoverflow.com/questions/19109542/installing-latest-version-of-git-in-ubuntu>`_.

.. code-block:: bash

    git -c http.extraheader="GIGALIXIR-CLEAN: true" push gigalixir

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

You'll probably also want to check all your environment variables and make sure they are set probably for production and staging. Also, generally speaking, it's best to use :bash:`prod.exs` for both production and staging and let environment variables be the only thing that varies between the two environments. This way staging is as close a simulation of production as possible. If you need to convert any configs into environment variables, use :elixir:`"${MYVAR}"`.

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

Using GitLab CI or any other CI/CD service should be very similar. For an example GitLab CI yaml file, see this `.gitlab-ci.yml <https://github.com/gigalixir/gigalixir-getting-started/blob/42a73c9e0f7de50cbfabd092a504aa454f9f9fc8/.gitlab-ci.yml>`_ file.

Using GitHub Actions is also similar. For example, see https://gist.github.com/jesseshieh/7b231370874445592a40bf5ed6961460
You might also take a look at this GitHub Action for Gigalixir: https://github.com/marketplace/actions/gigalixir-action

Using CircleCI is also similar. For an example, see this `config.yml <https://github.com/gigalixir/gigalixir-getting-started/blob/42a73c9e0f7de50cbfabd092a504aa454f9f9fc8/.circleci/config.yml>`_.

If you want to automatically run migrations on each automatic deploy, you have two options

1. (Recommended) Use a Distillery pre-start boot hook by following https://github.com/bitwalker/distillery/blob/master/docs/guides/running_migrations.md and https://github.com/bitwalker/distillery/blob/master/docs/extensibility/boot_hooks.md

2. Install the gigalixir CLI in your CI environment and run :bash:`gigalixir ps:migrate`. For example,

   .. code-block:: bash

       # install gigalixir-cli
       sudo apt-get install -y python3 python3-pip
       pip3 install gigalixir

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

Review Apps let you run a new instance for every branch and tear them down after the branch is deleted. For GitLab CI/CD Review Apps, all you have to do is create a :bash:`.gitlab-ci.yml` file that looks something like `this one <https://github.com/gigalixir/gigalixir-getting-started/blob/42a73c9e0f7de50cbfabd092a504aa454f9f9fc8/.gitlab-ci.yml>`_.

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

.. _`hot upgrades`:

How to Hot Upgrade an App
=========================

First of all, be sure you are using Distillery for your deploys and not mix. Hot upgrades only work with Distillery. For instructions on using Distillery, see :ref:`mix vs distillery`.

To do a hot upgrade, deploy your app with the extra header shown below. You'll need git v2.9.0 for this
to work. For information on how to install the latest version of git on Ubuntu, see `this stackoverflow question <http://stackoverflow.com/questions/19109542/installing-latest-version-of-git-in-ubuntu>`_. For more information about how hot upgrades work, see :ref:`life-of-a-hot-upgrade`.

.. code-block:: bash

    git -c http.extraheader="GIGALIXIR-HOT: true" push gigalixir

.. _`rollback`:

How to Rollback an App
======================

.. note::

   We only keep the releases for 1 year from when they were created so rolling back will only work if was created less than 1 year ago.

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

Can I deploy an app that isn't at the root of my repository?
============================================================

If you just want to push a subtree, try

.. code-block:: bash

    git subtree push --prefix my-sub-folder gigalixir

If you want to push the entire repo, but run the app from a subfolder, it becomes a bit trickier, but this pull request should help you.
https://github.com/jesseshieh/nonroot/pull/1/files

How to do blue-green or canary deploys?
=======================================

This feature is in beta as of 3/19/2019. You'll need the CLI v1.0.19 or later.

Apps on Gigalixir can be assigned another app as its canary. An arbitrary weight can also be assigned to control the traffic between the two apps. For example, if you have :bash:`my-app` with a canary assigned to it called :bash:`my-app-canary` with weight of 10, then :bash:`my-app` will receive 90% of the traffic and :bash:`my-app-canary` will receive 10% of the traffic. If you want to do blue-green deploys, simply flip the traffic between 0 and 100 to control which app receives the traffic. For example,

.. code-block:: bash

    # create the "blue" app
    gigalixir create --name my-app-blue
    git remote rename gigalixir blue

    # create the "green" app
    gigalixir create --name my-app-green
    git remote rename gigalixir green

    # deploy the app to blue
    git push blue master

    # wait a few minutes and ensure the app is running
    curl https://my-app-blue.gigalixirapp.com/

    # deploy the app to green
    git push green master

    # wait a few minutes to ensure the app is running
    curl https://my-app-green.gigalixirapp.com/

    # watch the logs on both apps
    gigalixir logs -a my-app-blue
    gigalixir logs -a my-app-green

    # set the canary, this should have no effect because the weight is 0
    gigalixir canary:set -a my-app-blue -c my-app-green -w 0

    # increase the weight to the canary
    gigalixir canary:set -a my-app-blue -w 10

    # ensure traffic is split as expected by watching the logs
    # flip traffic completely to green
    gigalixir canary:set -a my-app-blue -w 100

    # ensure traffic is going totally to green by watching the logs
    # to delete a canary, run
    gigalixir canary:unset -a my-app-blue -c my-app-green

Notice that with canaries, only the domain for :bash:`my-app-blue` gets redirected. Traffic to my-app-green.gigalixirapp.com goes entirely to :bash:`my-app-green`.

If you have custom domains defined on :bash:`my-app-blue`, traffic to those will also be shaped by the canary, but custom domains on :bash:`my-app-green` will still go entirely to :bash:`my-app-green`.

.. _`umbrella`:

How do I deploy an umbrella app?
================================

Umbrella apps are deployed the same way, but the buildpacks need to know which internal app is your Phoenix app. Set your :bash:`phoenix_relative_path` in your :bash:`phoenix_static_buildpack.config` file, see the `heroku-buildpack-phoenix-static configuration <https://github.com/gjaldon/heroku-buildpack-phoenix-static#configuration>`_ for more details.

When running migrations, we need to know which internal app contains your migrations. Use the :bash:`--migration_app_name` flag on :bash:`gigalixir ps:migrate`.

If you have multiple Distillery releases in your :bash:`rel/config.exs` file, be sure to set your default release to the one you want to deploy. See :ref:`gigalixir release options`.

If you have multiple Phoenix apps in the umbrella, you'll need to use something like this `master_proxy <https://github.com/jesseshieh/master_proxy>`_ to proxy requests to the two apps.

.. _`How to deploy a Ruby app`:

How to deploy a Ruby app
========================

.. code-block:: bash

    gigalixir login
    git clone https://github.com/heroku/ruby-getting-started.git
    cd ruby-getting-started
    APP=$(gigalixir create)
    git push gigalixir
    curl https://$APP.gigalixirapp.com/

Does Gigalixir have any web hooks?
==================================

We haven't built-in any web hooks, but most of what you need can be accomplished with buildpacks at build time and distillery hooks or modifying your Procfile.

To hit a web hook when building your app, you can use https://github.com/jesseshieh/buildpack-webhook

For runtime prestart hooks, see https://hexdocs.pm/distillery/extensibility/boot_hooks.html

Or if you aren't using distillery, see :ref:`custom procfile`. You can add any command you like.

