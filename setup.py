from setuptools import setup, find_packages

setup(
    name='gigalixir',
    url='https://github.com/gigalixir/gigalixir-cli',
    author='Jesse Shieh',
    author_email='jesse@gigalixir.com',
    version='1.2.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=6.7',
        'requests>=2.20.0',
        'stripe>=1.28.0',
        'rollbar>=0.13.11',
        'pygments>=2.2.0',
        'qrcode>=6.1',
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
            'sphinx-tabs',
        ],
        'test': [
            'pytest',
            'HTTPretty',
            'sure',
        ],
    }
)
