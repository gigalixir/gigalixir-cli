.. _`make your existing app work on Gigalixir`:
.. _`modifying existing app`:

Modifying an Existing App to Run on Gigalixir
=============================================

Whether you have an existing app or you just ran :bash:`mix phx.new`, the goal of this guide is to get your app ready for deployment on Gigalixir. We assume that you are using Phoenix here. If you aren't, feel free to :ref:`contact us<help>` for help. As long as your app is serving HTTP traffic on :bash:`$PORT`, you should be fine.

.. Important:: If you have an umbrella app, be sure to *also* see :ref:`umbrella`.

.. _`mix vs distillery`:

Mix vs Distillery vs Elixir Releases
------------------------------------

Probably the hardest part of deploying Elixir is choosing which method of deploying you prefer, but don't worry, it's easy to change your mind later and switch. We typically recommend elixir releases because it is easy to set up and unlocks the most important features like observer.  Here is a comparison table to help you choose. 

=======================  =================== ======================= =========== 
Feature                  Mix                 Elixir Releases         Distillery
=======================  =================== ======================= ===========
Hot Upgrades                                                         YES
Remote Observer                              YES                     YES
Mix Tasks                YES
Built-in to Elixir       YES                 YES
Easy Configuration[1]    YES
Clustering               YES                 YES                     YES
gigalixir ps:migrate     YES                 YES                     YES
Fast startup[2]                              YES                     YES 
Hidden Source Code[3]                        YES                     YES
=======================  =================== ======================= ===========

If you choose mix, see :ref:`modifying existing app with mix`.

If you choose Elixir releases, see :ref:`modifying existing app with Elixir releases`.

If you choose distillery, see :ref:`modifying existing app with distillery`.

[1] We say easy configuration here because some customers get confused about the difference between prod.exs and releases.exs. Distillery can be even more confusing with its :bash:`REPLACE_OS_VARS` syntax.
[2] Due to smaller slug sizes
[3] Mix deploys the source code to the runtime container rather than just the compiled BEAM files

.. toctree::
    :hidden:

    mix
    distillery
    releases

.. _`mix mode`:

How do I switch to mix mode?
----------------------------

Mix mode is sort of the default, but we automatically detect and switch you to distillery mode if you have a :bash:`rel/config.exs` file so one option is to delete that file.
We also automatically detect and switch you to Elixir releases mode if you have a :bash:`config/releases.exs` file so also be sure that file is deleted.

If you don't want to delete those files, you can manually force mix mode by specifying the mix buildpack. Create a :bash:`.buildpacks` file and make sure you have something like the following. Notice that the last buildpack is the mix buildpack.

.. code-block:: bash

    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-mix.git

If you wanted to force distillery or Elixir releases, you'd want the last buildpack to be either the :bash:`https://github.com/gigalixir/gigalixir-buildpack-distillery.git` or the :bash:`https://github.com/gigalixir/gigalixir-buildpack-releases.git` buildpacks, respectively.

