Jobs
~~~~

.. _`jobs`:

How to Run Jobs
===============

There are many ways to run one-off jobs and tasks. You can run them in the container your app is running or you can spin up a new container that runs the command and then destroys itself.

To run a command in your app container, run

.. code-block:: bash

    gigalixir ps:run $COMMAND
    # if you're using distillery, you'll probably want $COMMAND to be something like `bin/app eval 'IO.inspect Node.self'`
    # if you're using mix, you'll probably want $COMMAND to be something like `mix ecto.migrate`

To run a command in a separate container, run

.. code-block:: bash

    gigalixir run $COMMAND
    # if you're using distillery, you'll probably want $COMMAND to be something like `bin/app eval 'IO.inspect Node.self'`
    # if you're using mix, you'll probably want $COMMAND to be something like `mix ecto.migrate`

.. For an example task, see `gigalixir-getting-started's migrate task`_.

The task is not run on the same node that your app is running in. Jobs are killed after 5 minutes.

If you're using the distillery, note that because we start a separate container to run the job, if you need any applications started such as your :elixir:`Repo`, use :elixir:`Application.ensure_all_started/2`. Also, be sure to stop all applications when done, otherwise your job will never complete and just hang until it times out.

.. For more information about running migrations with Distillery, see `Distillery's Running Migrations`_.

Distillery commands currently do not support passing arguments into the job.

We prepend :elixir:`Elixir.` to your module name to let the BEAM virtual machine know that you want to run an Elixir module rather than an Erlang module. The BEAM doesn't know the difference between Elixir code and Erlang code once it is compiled down, but compiled Elixir code is namespaced under the Elixir module.

The size of the container that runs your job will be the same size as the app containers and billed the same way, based on replica-size-seconds. See, :ref:`pricing`.

.. _`gigalixir-getting-started's migrate task`: https://github.com/gigalixir/gigalixir-getting-started/blob/js/hooks/lib/tasks.ex
.. _`Distillery's Running Migrations`: https://hexdocs.pm/distillery/running-migrations.html
