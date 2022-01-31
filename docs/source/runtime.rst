SSH, Remote Console & Observer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _managing-ssh-keys:

Managing SSH Keys
=================

In order to SSH, run remote observer, remote console, etc, you need to set up your SSH keys. It could take up to a minute for the SSH keys to update in your containers.

.. code-block:: bash

    gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_ed25519.pub)"

If you don't have an :bash:`id_ed25519.pub` file, follow `this guide <https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/>`_ to create one. Or if you have an RSA key already, run :bash:`gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_rsa.pub)"` instead.

To view your SSH keys

.. code-block:: bash

    gigalixir account:ssh_keys

To delete an SSH key, find the key's id and then run delete the key by id.

.. code-block:: bash

    gigalixir account:ssh_keys:remove $ID

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

If you have multiple SSH keys on your machine, you may need to explicitly specify which one the Gigalixir CLI should use when connecting. If you get a :bash:`Permission denied (publickey)` error when attempting to run commands through the CLI but your :bash:`git push gigalixir master` (or equivalent) succeeds, first try specifying the SSH key you want to use with the option above.

To avoid having to specify the key file on each run, set the :bash:`GIGALIXIR_IDENTITY_FILE` to the path to your private key.

.. code-block:: bash

    export GIGALIXIR_IDENTITY_FILE=$HOME/.ssh/gigalixir
   

You can use :bash:`-o` to specify any option or options to :bash:`ssh`.

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

How to Launch a Remote Observer
===============================

To connect a remote observer, you need to be using Distillery or Elixir releases. See :ref:`mix vs distillery`.

In order to run a remote observer, you need to set up your SSH keys. It could take up to a minute for the SSH keys to update in your containers.

.. code-block:: bash

    gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_rsa.pub)"

Because Observer runs on your local machine and connects to a production node by joining the production cluster, you first have to have clustering set up. You don't have to have multiple nodes, but you need to follow the instructions in :ref:`cluster your nodes`.

You also need to have :elixir:`runtime_tools` in your application list in your :bash:`mix.exs` file. Phoenix 1.3 and later adds it by default, but you have to add it yourself in Phoenix 1.2.

Your local machine also needs to have :bash:`lsof`.

You should also make sure your app has enough memory. Even though observer itself is running on your local machine, the remote machine still needs quite a bit of memory. For a basic app, make sure you have at least 500mb memory (size 0.5).

Then, to launch observer and connect it to a production node, run

.. code-block:: bash

    gigalixir ps:observer

and follow the instructions. It will prompt you for your local sudo password so it can modify iptables rules. This connects to a random container using consistent hashing. We don't currently allow you to specify which container you want to connect to, but it will connect to the same container each time based on a hash of your ip address.

Monitoring
==========

Gigalixir doesn't provide any monitoring out of the box, but we are working on it. Also, you can always use a remote observer to inspect your node. See, :ref:`remote observer`.
