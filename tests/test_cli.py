"""CLI command tests for AppCreator."""

import tempfile
from pathlib import Path
from typer.testing import CliRunner

from appcreator.main import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "appcreator" in result.output.lower()
    assert "dev" in result.output
    assert "start" in result.output


def test_cli_dev_help():
    result = runner.invoke(app, ["dev", "--help"])
    assert result.exit_code == 0
    assert "ontwikkelingsservices" in result.output


def test_cli_dev_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["dev", "--dir", tmpdir])
        assert result.exit_code == 0
        assert "Geen backend of frontend aangetroffen" in result.output
