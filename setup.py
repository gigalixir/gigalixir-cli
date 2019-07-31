from setuptools import setup, find_packages

setup(
    name='gigalixir',
    url='https://github.com/gigalixir/gigalixir-cli',
    author='Jesse Shieh',
    author_email='jesse@gigalixir.com',
    version='1.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click~=6.7',
        'requests~=2.13.0',
        'stripe~=1.51.0',
        'rollbar~=0.13.11',
        'pygments~=2.2.0',
    ],
    entry_points='''
        [console_scripts]
        gigalixir=gigalixir:cli
    ''',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'HTTPretty',
        'sure',
    ],
    extras_require={
        'dev': [
            'Sphinx',
            'sphinx_rtd_theme',
        ],
        'test': [
            'pytest',
            'HTTPretty',
            'sure',
        ],
    }
)
