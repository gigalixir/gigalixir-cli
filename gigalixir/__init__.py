# This Python file uses the following encoding: utf-8
"""Bootstrap launcher for the GIGALIXIR CLI.

`pip install gigalixir` no longer installs the CLI itself. It installs this
launcher: on first invocation it resolves the current version from
get.gigalixir.com/cli/VERSION, downloads the matching binary, verifies
it against that release's checksums.txt, caches it under $XDG_CACHE_HOME,
and hands over. Every later invocation just execs the cached binary -- the
Go CLI owns its own updates from that point on. Stdlib only, deliberately.
"""
import hashlib
import os
import platform
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

__version__ = "2.0.0"

BASE_URL = "https://get.gigalixir.com/cli"
REQUEST_TIMEOUT = 15  # seconds
USER_AGENT = "gigalixir-pip-launcher/{}".format(__version__)

# Go's own names for the platforms we ship. platform.machine() spellings
# vary by OS (x86_64 vs AMD64, aarch64 vs ARM64); this normalizes them.
_GOARCH_BY_MACHINE = {
    "x86_64": "amd64",
    "amd64": "amd64",
    "aarch64": "arm64",
    "arm64": "arm64",
}

# A bare version, no leading "v". Rejects an empty body or an HTML error
# page (a CDN hiccup) rather than turning it into a URL we then fetch.
_VERSION_RE = re.compile(r"^\d[\w.+-]*$")


class LauncherError(Exception):
    """Anything that should stop before caching or executing a binary."""


def _fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return response.read()
    except urllib.error.URLError as e:
        raise LauncherError("could not reach {}: {}".format(url, e))


def _current_version():
    body = _fetch("{}/VERSION".format(BASE_URL))
    version = body.decode("utf-8", errors="replace").strip()
    if not _VERSION_RE.match(version):
        raise LauncherError(
            "VERSION was empty or malformed: {!r} -- try again shortly".format(version)
        )
    return version


def _platform_key():
    goos = platform.system().lower()
    if goos not in ("linux", "darwin", "windows"):
        raise LauncherError("unsupported platform: {}".format(platform.system()))
    goarch = _GOARCH_BY_MACHINE.get(platform.machine().lower())
    if goarch is None:
        raise LauncherError(
            "unsupported CPU architecture: {}".format(platform.machine())
        )
    return goos, goarch


def _binary_filename(goos, goarch):
    suffix = ".exe" if goos == "windows" else ""
    return "gigalixir-{}-{}{}".format(goos, goarch, suffix)


def _checksum_for(version, filename):
    body = _fetch("{}/v{}/checksums.txt".format(BASE_URL, version))
    for line in body.decode("utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == filename:
            return parts[0]
    raise LauncherError(
        "{} is not listed in checksums.txt for v{} -- "
        "this platform may not be built for this release".format(filename, version)
    )


def _cache_dir():
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(
        os.path.expanduser("~"), ".cache"
    )
    return os.path.join(base, "gigalixir")


def _download_and_verify(url, expected_sha256, dest_dir, dest_name):
    """Download to a temp file in dest_dir, verify it, then atomically
    rename it into place -- a checksum mismatch or a download that dies
    partway through never becomes a file this module will execute."""
    os.makedirs(dest_dir, exist_ok=True)
    final_path = os.path.join(dest_dir, dest_name)
    fd, tmp_path = tempfile.mkstemp(prefix="." + dest_name + ".", dir=dest_dir)
    try:
        digest = hashlib.sha256()
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with os.fdopen(fd, "wb") as tmp_file:
                with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        digest.update(chunk)
                        tmp_file.write(chunk)
        except urllib.error.URLError as e:
            raise LauncherError("could not download {}: {}".format(url, e))

        actual_sha256 = digest.hexdigest()
        if actual_sha256 != expected_sha256:
            raise LauncherError(
                "checksum mismatch for {}: expected {}, got {} "
                "(the download was corrupted or truncated)".format(
                    dest_name, expected_sha256, actual_sha256
                )
            )

        os.chmod(tmp_path, 0o755)
        os.replace(tmp_path, final_path)
    except BaseException:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise
    return final_path


def _resolve_binary():
    """Find the cached binary, or fetch it. The cache path deliberately
    does not encode the version: after the first run this must never hit
    the network to check "current" again, or every invocation would pay a
    round trip -- the Go CLI owns its own updates from here on, not this
    launcher."""
    goos, goarch = _platform_key()
    cache_dir = _cache_dir()
    cached_name = "gigalixir.exe" if goos == "windows" else "gigalixir"
    cached_path = os.path.join(cache_dir, cached_name)
    if os.path.exists(cached_path):
        return cached_path

    version = _current_version()
    filename = _binary_filename(goos, goarch)
    expected_sha256 = _checksum_for(version, filename)
    url = "{}/v{}/{}".format(BASE_URL, version, filename)
    return _download_and_verify(url, expected_sha256, cache_dir, cached_name)


def cli():
    """Console-script entry point: resolve, verify, cache, and hand over."""
    try:
        binary_path = _resolve_binary()
    except LauncherError as e:
        sys.stderr.write("gigalixir: {}\n".format(e))
        sys.exit(1)

    args = [binary_path] + sys.argv[1:]
    if platform.system().lower() == "windows":
        # Windows has no real exec(); propagate the child's exit code by hand.
        sys.exit(subprocess.run(args).returncode)
    else:
        os.execv(binary_path, args)
