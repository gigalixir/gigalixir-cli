.. _`quick start`:

Getting Started Guide
~~~~~~~~~~~~~~~~~~~~~

The goal of this guide is to get your app up and running on Gigalixir. You will sign up for an account, prepare your app, deploy, and provision a database.

If you're deploying an open source project, we provide consulting services free of charge. :ref:`Contact us<help>` and we'll send you a pull request with everything you need to get started.

Prerequisites
-------------

.. tabs::

   .. group-tab:: macOS

      #. :bash:`brew`. For help, take a look at the `homebrew documentation <https://docs.brew.sh/Installation>`_.
      #. :bash:`git`. For help, take a look at the `git documentation <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.

   .. group-tab:: Linux

      #. :bash:`python3`. :bash:`python2` also works, but it is EOL as of January 1st, 2020.
      #. :bash:`pip3`. For help, take a look at the `pip documentation <https://packaging.python.org/installing/>`_.
      #. :bash:`git`. For help, take a look at the `git documentation <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.

      For example, run

      .. code-block:: bash

          sudo apt-get update
          sudo apt-get install -y python3 python3-pip git-core curl

   .. group-tab:: Windows

      #. :bash:`python3`. :bash:`python2` also works, but it is EOL as of January 1st, 2020.
      #. :bash:`pip3`. For help, take a look at the `pip documentation <https://packaging.python.org/installing/>`_.
      #. :bash:`git`. For help, take a look at the `git documentation <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.

.. _`buildpack configuration file`: https://github.com/HashNuke/heroku-buildpack-elixir#configuration
.. _`beta sign up form`: https://docs.google.com/forms/d/e/1FAIpQLSdB1Uh1mGQHqIIX7puoZvwm9L93bR88cM1uGeSOCXh06_smVg/viewform
.. _`gigalixir-getting-started-phx-1-3-rc-2`: https://github.com/gigalixir/gigalixir-getting-started-phx-1-3-rc-2

.. _`install the CLI`:

Install the Command-Line Interface
----------------------------------

Next, install the command-line interface. Gigalixir has a web interface at https://console.gigalixir.com/, but you will likely still want the CLI.

.. tabs::

   .. group-tab:: macOS

      .. code-block:: bash

          brew tap gigalixir/brew && brew install gigalixir

      .. warning::

         You may need to update Xcode command-line tools otherwise you might get an error like this

         .. code-block:: bash

             xcrun: error: invalid active developer path

         To upgrade Xcode command-line tools, see https://stackoverflow.com/questions/52522565/git-is-not-working-after-macos-update-xcrun-error-invalid-active-developer-pa

   .. group-tab:: Linux

      .. code-block:: bash

          pip3 install gigalixir --user

      Make sure the executable is in your path, if it isn't already. 

      .. code-block:: bash

          echo 'export PATH=~/.local/bin:$PATH' >> ~/.bash_profile
          source ~/.bash_profile

   .. group-tab:: Windows

      .. code-block:: bash

          pip3 install gigalixir --user

      Make sure the executable is in your path, if it isn't already. 

      On Windows Powershell, try something similar to this. Note this may vary based on your python version.

      .. code-block:: bash

        [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$HOME\appdata\roaming\python\python38\Scripts", "Machine")

Verify by running

.. code-block:: bash

    gigalixir --help


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


If someone in your organization has already created the gigalixir app and you only need to add the proper git remote to your local repository configuration, you can skip the app creation and add a the :bash:`gigalixir` git remote by using the :bash:`git:remote` command:

.. code-block:: bash

    gigalixir git:remote $APP_NAME
    

Specify Versions
----------------

The default Elixir version is defined `here <https://github.com/HashNuke/heroku-buildpack-elixir/blob/master/elixir_buildpack.config>`_ which is quite old and it's a good idea to use the same version in production as you use in development so let's specify them. Supported Elixir and erlang versions can be found at https://github.com/HashNuke/heroku-buildpack-elixir#version-support

.. code-block:: bash

    echo "elixir_version=1.11.3" > elixir_buildpack.config
    echo "erlang_version=23.2" >> elixir_buildpack.config

Same for nodejs

.. code-block:: bash

    echo "node_version=14.15.4" > phoenix_static_buildpack.config

Don't forget to commit

.. code-block:: bash

    git add elixir_buildpack.config phoenix_static_buildpack.config
    git commit -m "set elixir, erlang, and node version"

If you're using Phoenix v1.6, it uses :bash:`esbuild` to compile your assets but Gigalixir images come with npm, so we will configure npm directly to deploy our assets. Add a :bash:`assets/package.json` file if you don't have any with the following:

.. code-block:: bash

    {
      "scripts": {
        "deploy": "cd .. && mix assets.deploy && rm -f _build/esbuild"
      }
    }

Don't forget to commit

.. code-block:: bash

    git add assets/package.json
    git commit -m "assets deploy script"


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

    git push gigalixir

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


