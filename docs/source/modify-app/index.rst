.. _`make your existing app work on Gigalixir`:
.. _`modifying existing app`:

Modifying an Existing App to Run on Gigalixir
=============================================

Whether you have an existing app or you just ran :bash:`mix phx.new`, the goal of this guide is to get your app ready for deployment on Gigalixir. We assume that you are using Phoenix here. If you aren't, feel free to :ref:`contact us<help>` for help. As long as your app is serving HTTP traffic on :bash:`$PORT`, you should be fine.

Important: If you have an umbrella app, be sure to *also* see :ref:`umbrella`.

.. _`mix vs distillery`:

Mix vs Distillery vs Elixir Releases
------------------------------------

Probably the hardest part of deploying Elixir is choosing which method of deploying you prefer. We typically recommend Distillery because it has the most features, but Mix is much simpler and Elixir releases give you a bit of both. Here is a comparison table to help you choose. Any features not in the table are available for all three.

=======================  =================== ======================= =========== 
Feature                  Mix                 Elixir Releases         Distillery
=======================  =================== ======================= ===========
Hot Upgrades                                                         YES
Remote Observer                              YES                     YES
Mix Tasks                YES
Included with Elixir     YES                 YES
Easy Configuration       YES
=======================  =================== ======================= ===========

If you choose mix, see :ref:`modifying existing app with mix`.

If you choose distillery, see :ref:`modifying existing app with distillery`.

If you choose Elixir releases, see :ref:`modifying existing app with Elixir releases`.

