Teams & Organizations
~~~~~~~~~~~~~~~~~~~~~

How do I give someone access to my app?
=======================================

If you work in a team, you'll probably want to collaborate with other users. With gigalixir's access permissions, you can grant access using the commands below. They'll be able to deploy & rollback, manage configs, ssh, remote_console, observer, hot upgrade, and scale.

First, they need to sign up for their own gigalixir account. Then run the command below to give them access.

.. code-block:: bash

    gigalixir access:add $USER_EMAIL

To see, who has access, run

.. code-block:: bash

    gigalixir access

To deny access to a user, run

.. code-block:: bash

    gigalixir access:remove $USER_EMAIL

If you don't have access to the CLI and want to modify access, :ref:`contact us<help>` and we'll help you out.

The "owner", the user who created the app, is responsible for the bill each month. 

For organizations, we recommend creating an "organization account" that is upgraded to the standard tier and has the billing information on file. Then create individual accounts for all developers and grant access to all contributors.

How do I change the owner of my app?
====================================

No problem. :ref:`Contact us<help>` and we'll help you out.

