Deploying
--

## Required packages

Install these outside the virtualenv
* build
* twine

## Build the pip

```
rm dist/*
python3 -m build
```

## Install locally

```
pip install dist/gigalixir-X.Y.Z.tar.gz
```


## Upload and tsting from pypitest

```
twine upload -r pypitest dist/*
pip3 uninstall gigalixir
python3 -m pip install --user --extra-index-url https://test.pypi.org/simple/ gigalixir==X.Y.Z
```

## Upload to production

```
twine upload -r pypi dist/*
pip3 uninstall gigalixir
python3 -m pip install --user gigalixir
```
