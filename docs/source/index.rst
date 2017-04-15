.. GIGALIXIR documentation master file, created by
   sphinx-quickstart on Fri Apr 14 16:43:23 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=====================================
GIGALIXIR Documentation
=====================================

GIGALIXIR is a platform-as-a-service designed just for Elixir and Phoenix.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

Quick Start
===========

Prequisites
-----------

.. role:: bash(code)
    :language: bash

You should make sure you have :bash:`pip` installed. For help, take a look at the `pip documentation`_.

Install gigalixir-cli
---------------------

Next install, the command-line interface. GIGALIXIR currently does not have a web interface. We want the command-line to be a first-class citizen so that you can build scripts and tools easily.

.. code-block:: bash

    pip install gigalixir

Create an account
-----------------

Create an account using the following command. It will prompt you for your email address and password. You will have to confirm your email before continuing. It will also prompt you for credit card information. GIGALIXIR currently does not offer a free trial, but we do offer a `money back guarantee`_. Please don't hesitate to use it.

.. code-block:: bash

    gigalixir create user

Log in
------

Next, log in. This will grant you an api key which expires in 365 days. It will also optionally modify your ~/.netrc file so that all future commands are authenticated.

.. code-block:: bash

    gigalixir login 

Prepare your app
----------------

There are a few steps involved to `make your app work on GIGALIXIR`_, but if you are starting a project from scratch, we recommend you clone the :bash:`gigalixir-getting-started` repo.

.. code-block:: bash

    git clone https://github.com/gigalixir/gigalixir-getting-started.git

You also need to let GIGALIXIR know about your app and set up your git remote.

.. code-block:: bash

    cd gigalixir-getting-started
    gigalixir create app $YOUR_APP_NAME

Deploy!
-------

Finally, build and deploy.

.. code-block:: bash

    git push gigalixir
    curl https://$YOUR_APP_NAME.gigalixirapp.com/

.. _`make your app work on GIGALIXIR`:

Modifying an existing app to run on GIGALIXIR
=============================================

TODO

.. _`money back guarantee`:

Money-back Guarantee
====================

If you are unhappy for any reason within the first 31 days, contact us to get a refund up to $75. Enough to run a 3 node cluster for 31 days.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _`pip documentation`: https://packaging.python.org/installing/
