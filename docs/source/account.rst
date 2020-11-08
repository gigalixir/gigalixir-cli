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

How to change your email address
================================

.. code-block:: bash

    gigalixir account:email:set

You will be sent a confirmation email with a link to confirm the email change.
The current email address will be sent an email with a link to revoke the change.

How to Change or Reset Your Password
====================================

With the web interface, visit https://console.gigalixir.com/#/password/reset

With the CLI, run

.. code-block:: bash

    gigalixir account:password:change

If you forgot your password, send a reset token to your email address by running the following command and following the instructions in the email.

.. code-block:: bash

    gigalixir account:password:reset

How to Resend the Confirmation Email
====================================

With the web interface, visit https://console.gigalixir.com/#/confirmation/resend

With the CLI, run

.. code-block:: bash

    gigalixir account:confirmation:resend

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

How to use  multi-factor authentication
=======================================

Also known as 2-factor authentication or 2fa, this gives your account an extra layer of security so someone with just your password still won't be able to login to your account.

To activate mfa with the CLI, first make sure you have version 1.2 or higher. To upgrade your CLI. See :ref:`cli-upgrade`.  Then run

.. code-block:: bash

    gigalixir account:mfa:activate

This logs you out, so re-login.

.. code-block:: bash

    gigalixir login 

Also, try it out on the web console: https://console.gigalixir.com/#/login

To deactivate, run

.. code-block:: bash

    gigalixir account:mfa:deactivate

To regenerate recovery codes, run

.. code-block:: bash

    gigalixir account:mfa:recovery_codes:regenerate

How to Check Account Status
===========================

To see things like which account you are logged in as, what tier you are on, and how many credits you have available, run

.. code-block:: bash

    gigalixir account
