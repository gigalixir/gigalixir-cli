# This Python file uses the following encoding: utf-8
import hashlib
import os
import platform
from unittest import mock

import pytest

import gigalixir


VERSION_TXT = b"1.32.1\n"

CHECKSUMS_TXT = (
    b"deb2ae35bfd004c67d55df7b20bc32c049d1d200f46b9ace90662070cd317afe  gigalixir-linux-amd64\n"
    b"73fb771e7764540b658d856ffbeb9b28f06eaa44c5575af4f6a1fc177c1b049e  gigalixir-windows-amd64.exe\n"
)


def _urlopen_returning(bodies_by_url):
    def urlopen(request, timeout=None):
        url = request.full_url if hasattr(request, "full_url") else request
        body = bodies_by_url[url]
        cm = mock.MagicMock()
        cm.__enter__.return_value = mock.MagicMock(read=mock.Mock(side_effect=_chunker(body)))
        cm.__exit__.return_value = False
        return cm
    return urlopen


def _chunker(body):
    # First call returns the whole body, subsequent calls return b"" --
    # matches the read(size) loop in _download_and_verify closing out.
    state = {"done": False}

    def read(*args, **kwargs):
        if state["done"]:
            return b""
        state["done"] = True
        return body

    return read


def test_platform_key_linux_amd64():
    with mock.patch("platform.system", return_value="Linux"), \
         mock.patch("platform.machine", return_value="x86_64"):
        assert gigalixir._platform_key() == ("linux", "amd64")


def test_platform_key_darwin_arm64():
    with mock.patch("platform.system", return_value="Darwin"), \
         mock.patch("platform.machine", return_value="arm64"):
        assert gigalixir._platform_key() == ("darwin", "arm64")


def test_platform_key_windows_amd64():
    with mock.patch("platform.system", return_value="Windows"), \
         mock.patch("platform.machine", return_value="AMD64"):
        assert gigalixir._platform_key() == ("windows", "amd64")


def test_platform_key_rejects_unsupported_os():
    with mock.patch("platform.system", return_value="SunOS"), \
         mock.patch("platform.machine", return_value="x86_64"):
        with pytest.raises(gigalixir.LauncherError):
            gigalixir._platform_key()


def test_platform_key_rejects_unsupported_arch():
    with mock.patch("platform.system", return_value="Linux"), \
         mock.patch("platform.machine", return_value="i686"):
        with pytest.raises(gigalixir.LauncherError):
            gigalixir._platform_key()


def test_binary_filename_adds_exe_suffix_only_on_windows():
    assert gigalixir._binary_filename("linux", "amd64") == "gigalixir-linux-amd64"
    assert gigalixir._binary_filename("windows", "amd64") == "gigalixir-windows-amd64.exe"


def test_current_version_reads_and_strips_the_body():
    urlopen = _urlopen_returning({
        "https://get.gigalixir.com/cli/VERSION": VERSION_TXT,
    })
    with mock.patch("urllib.request.urlopen", side_effect=urlopen):
        assert gigalixir._current_version() == "1.32.1"


def test_current_version_rejects_an_empty_body():
    urlopen = _urlopen_returning({
        "https://get.gigalixir.com/cli/VERSION": b"",
    })
    with mock.patch("urllib.request.urlopen", side_effect=urlopen):
        with pytest.raises(gigalixir.LauncherError):
            gigalixir._current_version()


def test_current_version_rejects_an_html_error_page():
    urlopen = _urlopen_returning({
        "https://get.gigalixir.com/cli/VERSION": b"<html>502 Bad Gateway</html>",
    })
    with mock.patch("urllib.request.urlopen", side_effect=urlopen):
        with pytest.raises(gigalixir.LauncherError):
            gigalixir._current_version()


def test_checksum_for_finds_the_matching_line():
    urlopen = _urlopen_returning({
        "https://get.gigalixir.com/cli/v1.32.1/checksums.txt": CHECKSUMS_TXT,
    })
    with mock.patch("urllib.request.urlopen", side_effect=urlopen):
        checksum = gigalixir._checksum_for("1.32.1", "gigalixir-linux-amd64")
    assert checksum == "deb2ae35bfd004c67d55df7b20bc32c049d1d200f46b9ace90662070cd317afe"


def test_checksum_for_raises_when_platform_missing():
    urlopen = _urlopen_returning({
        "https://get.gigalixir.com/cli/v1.32.1/checksums.txt": CHECKSUMS_TXT,
    })
    with mock.patch("urllib.request.urlopen", side_effect=urlopen):
        with pytest.raises(gigalixir.LauncherError):
            gigalixir._checksum_for("1.32.1", "gigalixir-freebsd-amd64")


def test_download_and_verify_accepts_a_matching_checksum(tmp_path):
    payload = b"pretend this is a binary"
    expected = hashlib.sha256(payload).hexdigest()
    urlopen = _urlopen_returning({
        "https://example.invalid/gigalixir-linux-amd64": payload,
    })
    with mock.patch("urllib.request.urlopen", side_effect=urlopen):
        path = gigalixir._download_and_verify(
            "https://example.invalid/gigalixir-linux-amd64",
            expected,
            str(tmp_path),
            "gigalixir-linux-amd64",
        )
    assert path == str(tmp_path / "gigalixir-linux-amd64")
    assert os.path.exists(path)
    with open(path, "rb") as f:
        assert f.read() == payload
    if platform.system().lower() != "windows":
        assert os.stat(path).st_mode & 0o111  # executable


def test_download_and_verify_rejects_a_corrupted_download(tmp_path):
    payload = b"truncated or tampered bytes"
    urlopen = _urlopen_returning({
        "https://example.invalid/gigalixir-linux-amd64": payload,
    })
    with mock.patch("urllib.request.urlopen", side_effect=urlopen):
        with pytest.raises(gigalixir.LauncherError):
            gigalixir._download_and_verify(
                "https://example.invalid/gigalixir-linux-amd64",
                "0" * 64,  # deliberately wrong
                str(tmp_path),
                "gigalixir-linux-amd64",
            )
    # Nothing executable was left behind, and no stray temp file either.
    assert not os.path.exists(str(tmp_path / "gigalixir-linux-amd64"))
    assert list(tmp_path.iterdir()) == []


def test_resolve_binary_skips_the_network_when_already_cached(tmp_path):
    cache_dir = tmp_path / "gigalixir"
    cache_dir.mkdir(parents=True)
    cached = cache_dir / "gigalixir"
    cached.write_bytes(b"already here")

    # Not just the download: _current_version() itself must not run, or a
    # cache hit would still pay a round trip to VERSION every time.
    with mock.patch("platform.system", return_value="Linux"), \
         mock.patch("platform.machine", return_value="x86_64"), \
         mock.patch("gigalixir._cache_dir", return_value=str(cache_dir)), \
         mock.patch("gigalixir._current_version", side_effect=AssertionError("should not resolve a version")), \
         mock.patch("urllib.request.urlopen", side_effect=AssertionError("should not hit the network")):
        path = gigalixir._resolve_binary()

    assert path == str(cached)


def test_resolve_binary_downloads_when_not_cached(tmp_path):
    cache_dir = tmp_path / "gigalixir"
    payload = b"pretend go binary"
    expected = hashlib.sha256(payload).hexdigest()
    checksums = "{}  gigalixir-linux-amd64\n".format(expected).encode("utf-8")
    urlopen = _urlopen_returning({
        "https://get.gigalixir.com/cli/VERSION": VERSION_TXT,
        "https://get.gigalixir.com/cli/v1.32.1/checksums.txt": checksums,
        "https://get.gigalixir.com/cli/v1.32.1/gigalixir-linux-amd64": payload,
    })
    with mock.patch("platform.system", return_value="Linux"), \
         mock.patch("platform.machine", return_value="x86_64"), \
         mock.patch("gigalixir._cache_dir", return_value=str(cache_dir)), \
         mock.patch("urllib.request.urlopen", side_effect=urlopen):
        path = gigalixir._resolve_binary()

    assert path == str(cache_dir / "gigalixir")
    with open(path, "rb") as f:
        assert f.read() == payload


def test_cache_dir_honors_xdg_cache_home(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    assert gigalixir._cache_dir() == str(tmp_path / "gigalixir")


def test_cache_dir_falls_back_to_dot_cache(monkeypatch):
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.setattr(os.path, "expanduser", lambda p: p.replace("~", "/home/nobody"))
    assert gigalixir._cache_dir() == os.path.join("/home/nobody", ".cache", "gigalixir")
