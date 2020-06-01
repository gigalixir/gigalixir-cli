Clustering
~~~~~~~~~~

.. _`cluster your nodes`:

Clustering Nodes
================

First of all, be sure you are using either Distillery or Elixir Releases for your deploys and not mix. Clustering won't work with just mix. For instructions on using Distillery or Releases, see :ref:`mix vs distillery`.

We use libcluster to manage node clustering. For more information, see `libcluster's documentation`_.

To install libcluster, add this to the deps list in :bash:`mix.exs`

.. code-block:: elixir

    {:libcluster, "~> 3.2"}

If you are on Elixir 1.3 or lower, add :elixir:`libcluster` and :elixir:`:ssl` to your applications list. Elixir 1.4 and up detect your applications list for you.

Next, add the following to the existing :elixir:`start` function in your :bash:`application.ex` file. Remember to replace :elixir:`GigalixirGettingStarted` with your application name.

.. code-block:: elixir

  def start(_type, _args) do
    topologies = Application.get_env(:libcluster, :topologies) || []

    children = [
      {Cluster.Supervisor, [topologies, [name: GigalixirGettingStarted.ClusterSupervisor]]},
      ... # other children
    ]
    ...
  end

Your app configuration needs to have something like this in it. For a full example, see `gigalixir-getting-started's prod.exs file`_.

.. code-block:: elixir

    ...
    config :libcluster,
      topologies: [
        k8s_example: [
          strategy: Cluster.Strategy.Kubernetes,
          config: [
            # For Elixir Releases, use System.get_env instead of the distillery env vars below.
            kubernetes_selector: "${LIBCLUSTER_KUBERNETES_SELECTOR}",
            kubernetes_node_basename: "${LIBCLUSTER_KUBERNETES_NODE_BASENAME}"]]]
    ...

Gigalixir handles permissions so that you have access to Kubernetes endpoints and we automatically set your node name and erlang cookie so that your nodes can reach each other. We don't firewall each container from each other like Heroku does. We also automatically set the environment variables :bash:`LIBCLUSTER_KUBERNETES_SELECTOR`, :bash:`LIBCLUSTER_KUBERNETES_NODE_BASENAME`, :bash:`APP_NAME`, and :bash:`MY_POD_IP` for you. See `gigalixir-run`_ for more details.

.. _`libcluster's documentation`: https://github.com/bitwalker/libcluster
.. _`gigalixir-getting-started's prod.exs file`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/config/prod.exs#L68
.. _`gigalixir-getting-started's mix.exs file`: https://github.com/gigalixir/gigalixir-getting-started/blob/master/mix.exs
.. _`gigalixir-run`: https://github.com/gigalixir/gigalixir-run


How to Set Up Distributed Phoenix Channels
==========================================

If you have successfully clustered your nodes, then distributed Phoenix channels *just work* out of
the box. No need to follow any of the steps described in `Running Elixir and Phoenix projects on a
cluster of nodes`_. See more information on how to :ref:`cluster your nodes<cluster your nodes>`.

.. _`Running Elixir and Phoenix projects on a cluster of nodes`: https://dockyard.com/blog/2016/01/28/running-elixir-and-phoenix-projects-on-a-cluster-of-nodes
