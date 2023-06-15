## Deploying

    # may have to upgrade pip and setuptools with
    # pip3 install --upgrade pip
    # pip3 install --upgrade setuptools
    python setup.py sdist upload -r pypitest
    python setup.py sdist upload -r pypi


## Testing from pypitest version

    pip3 uninstall gigalixir
    python3 -m pip install --user --index-url https://test.pypi.org/simple/ gigalixir
