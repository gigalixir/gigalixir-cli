Logging
~~~~~~~

.. _`tail logs`:
.. _`logging`:

How to Tail Logs
================

You can tail logs in real-time aggregated across all containers using the following command.

.. code-block:: bash

    gigalixir logs

How to Forward Logs Externally
==============================

If you want to forward your logs to another service such as `Logflare`_, `Timber`_ or `PaperTrail`_, you'll need to set up a log drain. We support HTTPS and syslog drains. To create a log drain, run

.. code-block:: bash

    gigalixir drains:add $URL
    # e.g. gigalixir drains:add https://api.logflare.app/logs/logplex?api_key=$API_KEY&source=$SOURCE_ID
    # e.g. gigalixir drains:add https://user:$TIMBER_API_KEY@logs.timber.io/sources/$TIMBER_SOURCE_ID/frames
    # e.g. gigalixir drains:add syslog+tls://logs123.papertrailapp.com:12345

To show all your drains, run

.. code-block:: bash

    gigalixir drains

To delete a drain, run

.. code-block:: bash

    gigalixir drains:remove $DRAIN_ID

.. _`Logflare`: https://logflare.app/
.. _`Timber`: https://timber.io
.. _`PaperTrail`: https://papertrailapp.com/
