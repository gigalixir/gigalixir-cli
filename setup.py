from setuptools import setup, find_packages

from gigalixir import __version__

setup(
    name='gigalixir',
    url='https://github.com/gigalixir/gigalixir-cli',
    author='Gigalixir',
    author_email='support@gigalixir.com',
    version=__version__,
    description='Bootstrap launcher for the GIGALIXIR CLI',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    # Stdlib only, deliberately. The Go binary this launcher fetches
    # owns its own updates from then on.
    install_requires=[],
    entry_points='''
        [console_scripts]
        gigalixir=gigalixir:cli
    ''',
    extras_require={
        'test': [
            'pytest',
        ],
    },
)
