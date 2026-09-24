# GIGALIXIR Command-Line Interface

This package is a small bootstrap launcher, not the CLI itself. On first run it downloads,
verifies, and caches the real `gigalixir` binary, then hands over to it; every later
invocation just runs the cached binary directly.

`pip install gigalixir` is no longer how the CLI is installed. If you already have it
installed via pip, this upgrades the launcher:

    pip3 install gigalixir --upgrade

For current installation instructions, see https://docs.gigalixir.com/cli
