import subprocess
from textwrap import dedent

import pytest

from dvc.exceptions import MetricsError

LIVE_SCRITP = dedent(
    """
        from dvclive import dvclive
        import sys
        r = 5
        for i in range(r):
           dvclive.log("loss", -i/5)
           dvclive.log("accuracy", i/5)"""
)


@pytest.mark.parametrize("summary", (True, False))
def test_export_config_tmp(tmp_dir, dvc, mocker, summary):
    proc_spy = mocker.spy(subprocess, "Popen")
    tmp_dir.gen("src", "dependency")
    dvc.run(
        cmd="mkdir logs && touch logs.json",
        deps=["src"],
        name="run_logger",
        live=["logs"],
        live_summary=summary,
    )

    assert proc_spy.call_count == 1
    _, kwargs = proc_spy.call_args

    assert "DVCLIVE_PATH" in kwargs["env"]
    assert kwargs["env"]["DVCLIVE_PATH"] == "logs"

    assert "DVCLIVE_SUMMARY" in kwargs["env"]
    assert kwargs["env"]["DVCLIVE_SUMMARY"] == str(int(summary))


@pytest.mark.skip(reason="dvclive does not exist yet")
@pytest.mark.parametrize("summary", (True, False))
def test_export_config(tmp_dir, dvc, mocker, summary):
    proc_spy = mocker.spy(subprocess, "Popen")
    tmp_dir.gen("log.py", LIVE_SCRITP.format(log_path="logs"))
    dvc.run(
        cmd="python log.py",
        deps=["log.py"],
        name="run_logger",
        live=["logs"],
        live_summary=summary,
    )
    assert proc_spy.call_count == 1
    _, kwargs = proc_spy.call_args

    assert "DVCLIVE_PATH" in kwargs["env"]
    assert kwargs["env"]["DVCLIVE_PATH"] == "logs"

    assert "DVCLIVE_SUMMARY" in kwargs["env"]
    assert kwargs["env"]["DVCLIVE_SUMMARY"] == str(int(summary))


@pytest.mark.skip(reason="dvclive does not exist yet")
def test_live_provides_metrics(tmp_dir, dvc):
    tmp_dir.gen("log.py", LIVE_SCRITP.format(log_path="logs"))
    dvc.run(
        cmd="python log.py",
        deps=["log.py"],
        name="run_logger",
        live=["logs"],
        live_summary=True,
    )

    assert (tmp_dir / "logs.json").is_file()
    assert dvc.metrics.show() == {
        "": {"logs.json": {"step": 3, "loss": -0.6, "accuracy": 0.6}}
    }

    assert (tmp_dir / "logs").is_dir()
    plots = dvc.plots.show()
    assert "logs/accuracy.tsv" in plots
    assert "logs/loss.tsv" in plots


@pytest.mark.skip(reason="dvclive does not exist yet")
def test_live_provides_no_metrics(tmp_dir, dvc):
    tmp_dir.gen("log.py", LIVE_SCRITP.format(log_path="logs"))
    dvc.run(
        cmd="python log.py",
        deps=["log.py"],
        name="run_logger",
        live=["logs"],
        live_summary=False,
    )

    assert not (tmp_dir / "logs.json").is_file()
    with pytest.raises(MetricsError):
        assert dvc.metrics.show() == {}

    assert (tmp_dir / "logs").is_dir()
    plots = dvc.plots.show()
    assert "logs/accuracy.tsv" in plots
    assert "logs/loss.tsv" in plots