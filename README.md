# GIGALIXIR Command-Line Interface

> **Deprecation notice: the Python CLI (`v1.x`) is deprecated.**
>
> The original Python implementation of the CLI, published at the `v1.x` tags and as
> `gigalixir` 1.x on PyPI, is deprecated. It receives no new features and no fixes, and
> is not guaranteed to work, or to keep working, against the GIGALIXIR platform.
>
> The supported way to run the CLI is the `gigalixir` 2.x pip package described below.
> It is a small launcher for the Go CLI, so upgrade with `pip3 install gigalixir --upgrade`.

This package is a small bootstrap launcher, not the CLI itself. On first run it downloads,
verifies, and caches the real `gigalixir` binary, then hands over to it; every later
invocation just runs the cached binary directly.

`pip install gigalixir` is no longer how the CLI is installed. If you already have it
installed via pip, this upgrades the launcher:

    pip3 install gigalixir --upgrade

For current installation instructions, see https://docs.gigalixir.com/cli
