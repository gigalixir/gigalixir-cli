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

## Credits

Beaker by Eugen Belyakoff from the Noun Project
