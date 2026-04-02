from pathlib import Path

from typer.testing import CliRunner

from latdiag.cli import app

runner = CliRunner()


def test_demo_generates_report(tmp_path: Path):
    result = runner.invoke(app, ["demo", "--output-dir", str(tmp_path)])
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "report" / "comparison.html").exists()
