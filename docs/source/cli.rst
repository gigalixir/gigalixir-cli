The Gigalixir Command-Line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Gigalixir Command-Line Interface or CLI is a tool you install on your local machine to control Gigalixir.

.. _`installation`:

How to Install the CLI
----------------------

See :ref:`install the CLI`.

There is also an Arch AUR Package here: https://aur.archlinux.org/packages/gigalixir-cli/

If you're interested in creating a macOS Brew formula, :ref:`contact us!<help>`

If you're interested in creating an Ubuntu/Debian package, :ref:`contact us!<help>`

.. _`cli-upgrade`:

How to Upgrade the CLI
----------------------

.. tabs::

  .. group-tab:: macOS

      .. code-block:: bash

          brew upgrade gigalixir

  .. group-tab:: Linux

      .. code-block:: bash

          pip3 install -U gigalixir --user

  .. group-tab:: Windows

      .. code-block:: bash

          pip3 install -U gigalixir --user

Encryption
----------

All HTTP requests made between your machine and Gigalixir's servers are encrypted.

Conventions
-----------

  - No news is good news: If you run a command that produces no output, then the command probably succeeded.
  - Exit codes: Commands that succeed will return a 0 exit code, and non-zero otherwise.
  - stderr vs stdout: Stderr is used for errors and for log output. Stdout is for the data output of your command.

Authentication
--------------

When you login with your email and password, you receive an API key. This API key is stored in your :bash:`~/.netrc` file. Commands generally use your :bash:`~/.netrc` file to authenticate with few exceptions.

Error Reporting
---------------

Bugs in the CLI are reported to Gigalixir's error tracking service. Currently, the only way to disable this is by modifying the source code. `Pull requests`_ are also accepted!

.. _`Pull requests`: https://github.com/gigalixir/gigalixir-cli/pulls

Open Source
-----------

The Gigalixir CLI is open source and we welcome pull requests. See `the gigalixir-cli repository`_.

.. _`the gigalixir-cli repository`: https://github.com/gigalixir/gigalixir-cli

How do I enable bash auto-completion?
-------------------------------------

Add the following to your :bash:`.bashrc` file and restart your shell.

.. code-block:: bash

    eval "$(_GIGALIXIR_COMPLETE=source gigalixir)"
