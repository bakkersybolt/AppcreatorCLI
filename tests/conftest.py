"""Shared fixtures: keep tests away from the real ~/.appcreator registry."""

import pytest


@pytest.fixture(autouse=True)
def isolated_appcreator_home(tmp_path, monkeypatch):
    home = tmp_path / "appcreator-home"
    monkeypatch.setenv("APPCREATOR_HOME", str(home))
    for key in ("BACKEND_PORT", "FRONTEND_PORT", "POSTGRES_PORT"):
        monkeypatch.delenv(key, raising=False)
    return home
