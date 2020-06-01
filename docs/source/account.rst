Account Management
~~~~~~~~~~~~~~~~~~

How to Sign Up for an Account
=============================

Create an account using the following command. It will prompt you for your email address and password. You will have to confirm your email before continuing. Gigalixir's free tier does not require a credit card, but you will be limited to 1 instance with 0.2GB of memory and 1 postgresql database limited to 10,000 rows.

.. code-block:: bash

    gigalixir signup

.. _`upgrade account`:

How to Upgrade an Account
=========================

The standard tier offers much more than the free tier, see :ref:`tiers`.

The easiest way to upgrade is through the web interface at https://console.gigalixir.com/

To upgrade with the CLI, first add a payment method

.. code-block:: bash

    gigalixir account:payment_method:set

Then upgrade.

.. code-block:: bash

    gigalixir account:upgrade

How to Delete an Account
========================

If you just want to make sure you won't be billed anymore, run

.. code-block:: bash

    gigalixir apps

And for every app listed, run

.. code-block:: bash

    gigalixir apps:destroy

This will make sure you've deleted all domains, databases, etc and you won't be charged in the future.

If you really want to completely destroy your account, run

.. code-block:: bash

    gigalixir account:destroy

Managing SSH Keys
=================

In order to SSH, run remote observer, remote console, etc, you need to set up your SSH keys. It could take up to a minute for the SSH keys to update in your containers.

.. code-block:: bash

    gigalixir account:ssh_keys:add "$(cat ~/.ssh/id_rsa.pub)"

If you don't have an :bash:`id_rsa.pub` file, follow `this guide <https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/>`_ to create one.

To view your SSH keys

.. code-block:: bash

    gigalixir account:ssh_keys

To delete an SSH key, find the key's id and then run delete the key by id.

.. code-block:: bash

    gigalixir account:ssh_keys:remove $ID

How to Change or Reset Your Password
====================================

With the web interface, visit https://console.gigalixir.com/#/password/reset

With the CLI, run

.. code-block:: bash

    gigalixir account:password:change

If you forgot your password, send a reset token to your email address by running the following command and following the instructions in the email.

.. code-block:: bash

    gigalixir account:password:reset

How to Change My Email Address
==============================

:ref:`Contact us<help>` and we'll help you out.

How to Resend the Confirmation Email
====================================

With the web interface, visit https://console.gigalixir.com/#/confirmation/resend

With the CLI, run

.. code-block:: bash

    gigalixir account:confirmation:resend

How to Delete your Account
==========================

There is currently no way to completely delete an account. We are working on implementing this feature. You can delete apps though. See :ref:`delete-app`.

How to Reset your API Key
=========================

If you lost your API key or it has been stolen, you can reset it by running

.. code-block:: bash

    gigalixir account:api_key:reset

Your old API key will no longer work and you may have to login again.

How to Log Out
==============

.. code-block:: bash

    gigalixir logout

How to Log In
=============

.. code-block:: bash

    gigalixir login

This modifies your ~/.netrc file so that future API requests will be authenticated. API keys never expire, but can be revoked.
