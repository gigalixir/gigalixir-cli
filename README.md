# GIGALIXIR Command-Line Interface

## Installation

    pip3 install gigalixir

If you don't have pip install, see https://pip.pypa.io/en/stable/installing/

## Quickstart

    gigalixir signup
    gigalixir login
    gigalixir create 
    git push gigalixir
    curl https://$APP_NAME.gigalixirapp.com/

## Documentation

    http://gigalixir.readthedocs.io/en/latest/
    https://www.gigalixir.com

## Testing

    # for python3 
    sudo apt-get install -y python3-venv
    sudo apt-get install -y python3-pip
    python3 -m venv venv3
    source venv3/bin/activate

    # Make sure you have pip >= 20.3
    # See https://pip.pypa.io/en/stable/topics/dependency-resolution/#backtracking
    pip3 install --upgrade pip
    pip3 install -e .[dev]
    pip3 install -e .[test]
    python setup.py test

    # e2e tests
    asdf plugin-add elixir https://github.com/asdf-vm/asdf-elixir.git
    asdf plugin add erlang https://github.com/asdf-vm/asdf-erlang.git
    sudo apt-get -y install build-essential autoconf m4 libncurses5-dev libwxgtk3.0-gtk3-dev libgl1-mesa-dev libglu1-mesa-dev libpng-dev libssh-dev unixodbc-dev xsltproc fop libxml2-utils libncurses-dev openjdk-11-jdk
    asdf install elixir 1.10.3
    asdf install erlang 22.3
    mix local.hex
    mix archive.install hex phx_new 1.5.8


    source venv3/bin/activate
    unset GIGALIXIR_ENV
    pip3 install pytest
    export GIGALIXIR_EMAIL=foo
    export GIGALIXIR_PASSWORD=bar
    pytest -s e2e/test.py

    # hit a development server
    # get into the venv (see above)
    GIGALIXIR_ENV=dev gigalixir account

## Distribute

    # may have to upgrade pip and setuptools with
    # pip3 install --upgrade pip
    # pip3 install --upgrade setuptools
    python setup.py sdist upload -r pypitest
    python setup.py sdist upload -r pypi

## Modify documentation

    pip3 install sphinx
    pip3 install sphinx_rtd_theme
    cd docs
    make html
    xdg-open build/html/index.html

    # Be sure to update
    # 1. Phoenix Guides
    # 2. Marketing Emails
    # 3. Console & Homepage Links
    # 4. Blog Links

## Clean up e2e test

    # the test cleans itself up unless there was a failure, then it does not clean up
    # to clean up failed tests, run
    APPS=$(gigalixir apps | jq -r '.[] | select(.replicas > 0) | .unique_name')
    for app in $APPS; do gigalixir ps:scale -r 0 -a $app; done

    # you may also have to clean up databases, which is not described here.

## Credits

Beaker by Eugen Belyakoff from the Noun Project
