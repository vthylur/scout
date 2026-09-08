import subprocess

import pytest

from scout1_tools.health_check import backend
from scout1_tools.health_check.backend import health_check_symbol


def test_health_check_symbol_returns_reliance_golden_values():
    def query_runner(symbol):
        assert symbol == "RELIANCE"
        return {
            "row_count": "1043761",
            "min_ts": "2015-02-02 03:45:00+00",
            "max_ts": "2026-05-19 09:59:00+00",
            "min_close": "188.25",
            "max_close": "1609.7",
        }

    result = health_check_symbol("RELIANCE", query_runner=query_runner)

    assert result.row_count == 1_043_761
    assert result.min_ts.isoformat() == "2015-02-02T03:45:00+00:00"
    assert result.max_ts.isoformat() == "2026-05-19T09:59:00+00:00"
    assert result.min_close == 188.25
    assert result.max_close == 1609.7


def test_health_check_symbol_rejects_empty_symbol_results():
    with pytest.raises(ValueError, match="No OHLCV rows found for symbol MISSING"):
        health_check_symbol("MISSING", query_runner=lambda symbol: {
            "row_count": "0",
            "min_ts": "",
            "max_ts": "",
            "min_close": "",
            "max_close": "",
        })


def test_run_psql_health_query_is_bounded_and_noninteractive(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="1\t2024-01-01 00:00:00+00\t2024-01-01 00:00:00+00\t10.0\t10.0\n")

    monkeypatch.setattr(backend.subprocess, "run", fake_run)

    row = backend._run_psql_health_query("RELIANCE")

    assert row["row_count"] == "1"
    assert calls[0][1]["timeout"] == 30
    assert calls[0][1]["stdin"] is subprocess.DEVNULL
