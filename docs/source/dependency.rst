Packages & Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

What packages are available to my Gigalixir app?
================================================

Gigalixir's stacks are based on Heroku's stacks so anything you find here, you can find on Gigalixir.
https://devcenter.heroku.com/articles/stack-packages#installed-ubuntu-packages

To find what stack you are on, run `gigalixir apps:info` or `gigalixir ps`. If you are on gigalixir-18, check the heroku-18 column. Same for the other stacks.

You can also explore and verify by SSH'ing into your container. For example

.. code-block:: bash

   gigalixir ps:ssh
   convert --help

How do I install extra binaries I need for my app?
==================================================

The process is different if you are using releases (distillery, Elixir releases) or mix. We recommend switching to mix mode as it's much easier. To switch to mix mode, see :ref:`mix mode`.

In mix mode, all you have to do is add the relevant, buildpack to your :bash:`.buildpacks` file. Probably at the top. Make sure you also have the required Elixir, Phoenix, and mix buildpacks. For example, if you need rust installed, your :bash:`.buildpacks` file might look like this

.. code-block:: bash

    https://github.com/emk/heroku-buildpack-rust
    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-mix.git

For rust specifically, also be sure to run :bash:`echo "RUST_SKIP_BUILD=1" > RustConfig` since you just need the rust binaries, and don't want to build a rust project.

In mix mode, the entire build folder is packed up and shipped to your run container which means it will pack up the extra binaries you've installed and any .profile.d scripts needed to make them available. That's it!

If you want to continue using distillery, you need to manually figure out which folders and files need to be packed into your release tarball and copy them over using distillery overlays. See https://github.com/bitwalker/distillery/blob/master/docs/extensibility/overlays.md

If you are using Elixir releases, you also need to manually figure out which folders and files you need to be packed into your release tarball and copy them over using an extra "step". See https://hexdocs.pm/mix/Mix.Tasks.Release.html#module-steps

How do I use a private git dependency?
======================================

If you want to use a private git repository as a dependency in :bash:`mix.exs`, our recommended approach is to use the netrc buildpack found at https://github.com/timshadel/heroku-buildpack-github-netrc

To use the buildpack, insert it in your :bash:`.buildpacks` file above the Elixir and Phoenix buildpacks. For example, if you are using distillery, your :bash:`.buildpacks` file will look like this

.. code-block:: bash

    https://github.com/timshadel/heroku-buildpack-github-netrc.git
    https://github.com/HashNuke/heroku-buildpack-elixir
    https://github.com/gjaldon/heroku-buildpack-phoenix-static
    https://github.com/gigalixir/gigalixir-buildpack-distillery.git

Next, create a personal access token by following https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/

Just make sure you give the token "repo" access so that it can access your private repository.

Add your personal access token as a config var by running

.. code-block:: bash

    gigalixir config:set -a $APP_NAME GITHUB_AUTH_TOKEN="$GITHUB_TOKEN"

The last step is to add the dependency to your :bash:`mix.exs` file. Add it as you would any other git dependency, but be sure you use the https url and not the ssh url. For example, 

.. code-block:: elixir

    {:foo, git: "https://github.com/jesseshieh/foo.git", override: true}

That should be it. 

Alternatively, you could also put your github username and personal access token directly into the git url, but it's generally not a good idea to check in secrets to source control. You could use :elixir:`System.get_env` interpolated inside the git url, but then you run the risk of the secrets getting saved to :bash:`mix.lock`.
