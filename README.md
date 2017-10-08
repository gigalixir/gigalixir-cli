# GIGALIXIR Command-Line Interface

## Installation

    pip install gigalixir

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

    # set up a virtualenv, then
    source venv/bin/activate
    unset GIGALIXIR_ENV
    pip install -e .[dev]
    python setup.py test

    # e2e tests
    source venv/bin/activate
    unset GIGALIXIR_ENV
    pip install pytest
    export GIGALIXIR_EMAIL=foo
    export GIGALIXIR_PASSWORD=bar
    pytest -s e2e/test.py

## Distribute

    python setup.py sdist upload -r pypitest
    python setup.py sdist upload -r pypi

## Modify documentation

    pip install sphinx
    pip install sphinx_rtd_theme
    cd docs
    make html
    xdg-open build/html/index.html

## Credits

Beaker by Eugen Belyakoff from the Noun Project
