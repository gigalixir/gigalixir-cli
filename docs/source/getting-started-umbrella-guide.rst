.. _`quick start umbrella`:

Getting Started Umbrella Guide
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This guide is a follow up of the :ref:`quick start` guide. If you haven't applied it until the end of the :bash:`Provision a Database` part, you should do so and come back after.

Git Submodules
--------------

If you organised your code base on `Git submodules`_, you may have some troubles cloning your repository, especially if they are private.

Unfortunately, you won't be able to do it in a secure way. This is due to two reasons

1) There is no hook called before the submodules clone command

2) You can't use env variable nor can you import a SSH key

Therefore, you will have to go to your :bash:`.gitmodules` file, and add your username and password before each url. As it isn't secured, it is strongly advised to create another use and set only the read rights.

.. code-blokc:: git

  [submodule "my_app"]
	  path = apps/my_app
	  url = https://username:password@github.com/my_project/my_repo

By doing so, you may need to update the pushurl of the submodule repository to be equal to the base url:

.. code-block:: bash

  git config remote.origin.pushurl https://github.com/my_project/my_repo

.. Note:: If you find a solution which doesn't expose the password, please let us know, so we can provide a more secured guide to everyone.

Umbrella Base Setup
----------

.. Important:: Be certain to follow the part first paragraph of the :ref:`umbrella`. This should be enough if you only have one Phoenix.

Multiple Phoenix App
--------------------

Once you finished to setup `phoenix_static_buildpack.config` as describe in the previous part, there is more to be done.

First, create a :bash:`.buildpacks` file and make sure you have something like the following.

.. code-block:: bash

  https://github.com/HashNuke/heroku-buildpack-elixir
  https://github.com/gjaldon/heroku-buildpack-phoenix-static
  https://github.com/gigalixir/gigalixir-buildpack-mix.git

Depending of your deployment preference, this file will be modified later on the :ref:`modifying existing app` chapter.

Once the buildpack is created, you will have to add another file, called :bash:`compile`, which contains bash commands. This file is called by the heroku-buildpack-phoenix-static, and will overwrite the existing one, which focus on a single phoenix app.

.. code-block:: bash

  # app_root/compile

  # Build first phoenix app
  # Set variables
  phoenix_dir=$build_dir/apps/my_app
  assets_dir=$build_dir/apps/my_app/assets
  info "Phoenix dir ${phoenix_dir}"
   
  # Go to the asset dir
  cd $assets_dir
  info "Caching node modules"

  cp -R node_modules $cache_dir
  PATH=$assets_dir/node_modules/.bin:$PATH
  install_bower_deps
  
  npm run deploy
  export PATH=$(p=$(echo $PATH | tr ":" "\n" | grep -v "/$assets_dir/node_modules/.bin" | tr "\n" ":"); echo ${p%:})
  rm -rf $assets_dir/node_modules
  
  cd $phoenix_dir
  mix "phx.digest"
  mix "phx.digest.clean"
  
  # Build second phoenix app
  # Set variables
  phoenix_dir=$build_dir/apps/another_app
  assets_dir=$build_dir/apps/another_app/assets
  info "Phoenix dir ${phoenix_dir}"
  
  # Get node deps
  install_and_cache_deps
  npm run deploy
  export PATH=$(p=$(echo $PATH | tr ":" "\n" | grep -v "/$assets_dir/node_modules/.bin" | tr "\n" ":"); echo ${p%:})
  rm -rf $assets_dir/node_modules
  
  cd $phoenix_dir
  mix "phx.digest"
  mix "phx.digest.clean"

As you can see, the first and the second app don't use the same commands. It is because the first app should be the one pointed by :bash:`phoenix_relative_path` in the :bash:`phoenix_static_buildpack.config` file.

As it it point by this configuration, some action will be already done, such as creating the node_modules folder.

.. _Git submodules: https://git-scm.com/book/en/v2/Git-Tools-Submodules
