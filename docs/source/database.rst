Database Management
~~~~~~~~~~~~~~~~~~~

.. _`provisioning free database`:

How to provision a Free PostgreSQL database
===========================================

IMPORTANT: Make sure you set your :bash:`pool_size` in :bash:`prod.exs` to 2 beforehand. The free tier database only allows limited connections.

The following command will provision a free database for you and set your :bash:`DATABASE_URL` environment variable appropriately.

.. code-block:: bash

    gigalixir pg:create --free

List databases by running

.. code-block:: bash

    gigalixir pg

Delete by running

.. code-block:: bash

    gigalixir pg:destroy -d $DATABASE_ID

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

You may also want to adjust your pool_size. We recommend setting the pool size to (M-6)/(n+1) where M is the max connections and n is the num app replicas. We subtract 6 because cloud sql will sometimes, but rarely, use 6 for maintenance purposes. We use n+1 because rolling deploys will temporarily have an extra replica during the transition. For example, if you are running a size 0.6 database with 1 app replica, the pool size should be (25-6)/(1+1)=9.

You can only have one database per app because otherwise managing your :bash:`DATABASE_URL` variable would become trickier.

Under the hood, we use Google's Cloud SQL which provides reliability, security, and automatic backups. For more information, see `Google Cloud SQL for PostgreSQL Documentation`_.

.. _`Google Cloud SQL for PostgreSQL Documentation`: https://cloud.google.com/sql/docs/postgres/

.. _`upgrade db`:

How to upgrade a Free DB to a Standard DB
=========================================

If you started out with a free tier database and then upgraded to the standard tier, we highly recommend you migrate to a standard tier database. The standard tier databases support encryption, backups, extensions, functions, trigers, and dedicated cpu, memory, & disk. There are no row limits, connection limits*, and they are automatically scalable.

Unfortunately, we can't automatically migrate your free tier db to a standard tier db. You'll have to

  1. :bash:`pg_dump` the free database
  2. Delete the free database with :bash:`gigalixir pg:destroy --help`. Note postgres may make you scale down to 0 app replicas to do this so you'll have some downtime.
  3. Create the standard tier database with :bash:`gigalixir pg:create`.
  4. Restore the data with :bash:`psql` or :bash:`pg_restore`. You can find the url to use with :bash:`gigalixir pg` once the standard tier database is created.

Please don't hesitate to :ref:`contact us<help>` if you need help.

* Databases still have connection limits based on Google Cloud SQL limits. See https://cloud.google.com/sql/docs/postgres/quotas#fixed-limits

How to scale a database
=======================

To change the size of your database, run

.. code-block:: bash

    gigalixir pg:scale -d $DATABASE_ID --size=1.7

You can find your database id by running

.. code-block:: bash

    gigalixir pg

Supported sizes include 0.6, 1.7, 4, 8, 16, 32, 64, and 128. For more information about databases sizes, see :ref:`database sizes`.

How to dump the database to a file
==================================

We recommend :bash:`pg_dump`. You can find all the connection paramters you need from :bash:`gigalixir pg`. This should dump the database contents as a sql file which you can load back in with :bash:`psql`. If you dump a binary file, then you can use :bash:`pg_restore`.

How to restore a database backup
================================

We use Cloud SQL under the hood which takes automatic backups every day and keeps 7 backups available. For more, see https://cloud.google.com/sql/docs/postgres/backup-recovery/backups

First, get your database id by running

.. code-block:: bash

    gigalixir pg

View what backups you have available by running

.. code-block:: bash

    gigalixir pg:backups -d $DATABASE_ID

.. Note:: We required the database_id even though we could probably detect it automatically because these are sensitive operations and we prefer to be explicit.

Find the backup id you want and run

.. code-block:: bash

    gigalixir pg:backups:restore -d $DATABASE_ID -b $BACKUP_ID

This can take a while. Sometimes over ten minutes. To check the status, run

.. code-block:: bash

    gigalixir pg

How to restart a database
=========================

:ref:`Contact us<help>` and we'll help you out. Only standard tier databases can be restarted.

How to delete a database
========================

WARNING!! Deleting a database also deletes all of its backups. Please make sure you backup your data first.

To delete a database, run

.. code-block:: bash

    gigalixir pg:destroy -d $DATABASE_ID

How to install a Postgres Extension
===================================

.. Note:: Free Databases do not support extensions except for citext which is preinstalled. See :ref:`tiers`.

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
       pool_size: 2

Replace :elixir:`:gigalixir_getting_started` and :elixir:`GigalixirGettingStarted` with your app name. Then, be sure to set your :bash:`DATABASE_URL` config with something like this.  For more information on setting configs, see :ref:`configs`. If you provisioned your database using, :ref:`provisioning database`, then :bash:`DATABASE_URL` should be set for you automatically once the database is provisioned. Otherwise,

.. code-block:: bash

    gigalixir config:set DATABASE_URL="ecto://user:pass@host:port/db"

If you need to provision a database, Gigalixir provides Databases-as-a-Service. See :ref:`provisioning database`. If you prefer to provision your database manually, follow :ref:`How to set up a Google Cloud SQL PostgreSQL database`.

.. _`supports PostgreSQL`: https://cloud.google.com/sql/docs/postgres/
.. _`Phoenix Using MySQL Guide`: http://www.phoenixframework.org/docs/using-mysql
.. _`Amazon Relational Database Service`: https://aws.amazon.com/rds/
.. _`Google Cloud SQL`: https://cloud.google.com/sql/docs/
.. _`gigalixir-getting-started`: https://github.com/gigalixir/gigalixir-getting-started
.. _`lib/gigalixir-getting-started.ex`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/lib/gigalixir_getting_started.ex#L14


.. _`How to set up a Google Cloud SQL PostgreSQL database`:

How to manually set up a Google Cloud SQL PostgreSQL database
-------------------------------------------------------------

.. Note:: You can also use Amazon RDS, but we do not have instructions provided yet.

1. Navigate to https://console.cloud.google.com/sql/instances and click "Create Instance".
#. Select PostgreSQL and click "Next".
#. Configure your database.

   a. Choose any instance id you like.
   #. Choose us-central1 as the Region.
   #. Choose how many cores, memory, and disk.
   #. In "Default user password", click "Generate" and save it somewhere secure.
   #. In "Authorized networks", click "Add network" and enter "0.0.0.0/0" in the "Network" field. It will be encrypted with TLS and authenticated with a password so it should be okay to make the instance publicly accessible. Click "Done".

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
#. Make sure you have :elixir:`ssl:true` in your :bash:`prod.exs` database configuration. Cloud SQL supports TLS out of the box so your database traffic should be encrypted.

We hope to provide a database-as-a-service soon and automate the process you just went through. Stay tuned.

.. _`migrations`:

How to Run Migrations
=====================

If you deployed your app without distillery or elixir releases, meaning you are in mix mode, you can run migrations as a job in a new container with

.. code-block:: bash

    gigalixir run mix ecto.migrate

If you deployed your app as a distillery release or elixir release, :bash:`mix` isn't available. We try to make it easy by providing a special command, but the command runs on your existing app container so you'll need to make sure your app is running first and set up SSH keys.

.. code-block:: bash

    gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_rsa.pub)"

Then run

.. code-block:: bash

    gigalixir ps:migrate

This command runs your migrations in a remote console directly on your production node. It makes some assumptions about your project so if it does not work, please :ref:`contact us for help<help>`.

If you are running an umbrella app, you will probably need to specify which "inner app" within your umbrella to migrate. Do this by passing the :bash:`--migration_app_name` flag like so

.. code-block:: bash

    gigalixir ps:migrate --migration_app_name=$MIGRATION_APP_NAME

When running :bash:`gigalixir ps:migrate`, sometimes the migration doesn't do exactly what you want. If you need to tweak the migration command to fit your situation, all :bash:`gigalixir ps:migrate` is doing is dropping into a remote_console and running the following. For information on how to open a remote console, see :ref:`remote console`.

.. code-block:: elixir

    repo = List.first(Application.get_env(:gigalixir_getting_started, :ecto_repos))
    app_dir = Application.app_dir(:gigalixir_getting_started, "priv/repo/migrations")
    Ecto.Migrator.run(repo, app_dir, :up, all: true)

So for example, a tweak you might make is, if you have more than one app, you may not want to use :elixir:`List.first` to find the app that contains the migrations.

.. _`the source code`: https://github.com/gigalixir/gigalixir-cli/blob/master/gigalixir/app.py#L160

If you have a chicken-and-egg problem where your app will not start without migrations run, and migrations won't run without an app running, you can try the following workaround on your local development machine. This will run migrations on your production database from your local machine using your local code.

.. code-block:: bash

    MIX_ENV=prod DATABASE_URL="$YOUR_PRODUCTION_DATABASE_URL" mix ecto.migrate

How to run migrations on startup
================================

If you are using distillery, we suggest using a distillery pre-start boot hook by following https://github.com/bitwalker/distillery/blob/master/docs/guides/running_migrations.md and https://github.com/bitwalker/distillery/blob/master/docs/extensibility/boot_hooks.md

If you are using elixir releases, we suggest creating a custom Procfile and overlaying it into your release tarball. To do this create a file :bash:`rel/overlays/Procfile` with something like this

.. code-block:: bash

    web: /app/bin/$GIGALIXIR_APP_NAME eval "MyApp.Release.migrate" && /app/bin/$GIGALIXIR_APP_NAME $GIGALIXIR_COMMAND

You have to implement the :elixir:`MyApp.Release.migrate` function with something like https://hexdocs.pm/phoenix/releases.html#ecto-migrations-and-custom-commands. You might also be interested in reading https://elixirforum.com/t/equivalent-to-distillerys-boot-hooks-in-mix-release-elixir-1-9/23431

If you aren't running distillery or elixir releases, meaning you are in mix mode, you can try modifying your :bash:`Procfile` to something like this

.. code-block:: bash

    web: mix ecto.migrate && elixir --name $MY_NODE_NAME --cookie $MY_COOKIE -S mix phx.server

For more details, see :ref:`custom procfile`.

How to reset the database?
==========================

First, :ref:`drop into a remote console<remote console>` and run this to "down" migrate. You may have to tweak the command depending on what your app is named and if you're running an umbrella app.

.. code-block:: elixir

    Ecto.Migrator.run(MyApp.Repo, Application.app_dir(:my_app, "priv/repo/migrations"), :down, [all: true])

Then run this to "up" migrate.

.. code-block:: elixir

    Ecto.Migrator.run(MyApp.Repo, Application.app_dir(:my_app, "priv/repo/migrations"), :up, [all: true])

How to run seeds?
=================

If you are in mix mode (not using distillery or elixir releases) and have a seeds.exs file, you can just run

.. code-block:: bash

    gigalixir run -- mix run priv/repo/seeds.exs

Otherwise, you'll need to :ref:`drop into a remote console<remote console>` and run commands manually. If you have a :bash:`seeds.exs` file, you can follow `the Distillery migration guide`_ and run something like this in your remote console.

.. code-block:: elixir

    seed_script = Path.join(["#{:code.priv_dir(:myapp)}", "repo", "seeds.exs"])
    Code.eval_file(seed_script)

.. _`the Distillery migration guide`: https://hexdocs.pm/distillery/running-migrations.html#content
