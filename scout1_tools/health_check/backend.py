from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
import subprocess
from typing import Callable, Mapping


@dataclass(frozen=True)
class SymbolHealthCheck:
    row_count: int
    min_ts: datetime
    max_ts: datetime
    min_close: float
    max_close: float


QueryRunner = Callable[[str], Mapping[str, str]]


def health_check_symbol(symbol: str, query_runner: QueryRunner | None = None) -> SymbolHealthCheck:
    row = (query_runner or _run_psql_health_query)(symbol)
    row_count = int(row["row_count"])
    if row_count == 0:
        raise ValueError(f"No OHLCV rows found for symbol {symbol}")

    return SymbolHealthCheck(
        row_count=row_count,
        min_ts=_parse_timestamp(row["min_ts"]),
        max_ts=_parse_timestamp(row["max_ts"]),
        min_close=float(row["min_close"]),
        max_close=float(row["max_close"]),
    )


def _run_psql_health_query(symbol: str) -> Mapping[str, str]:
    sql = """
select
  count(*) as row_count,
  min(o.ts) as min_ts,
  max(o.ts) as max_ts,
  min(o.c) as min_close,
  max(o.c) as max_close
from c1.ohlcv o
join c1.symbols s on s.symbol_id = o.symbol_id
where s.symbol = :'symbol';
"""
    command = [
        os.environ.get("SCOUT1_PSQL", "psql"),
        "-X",
        "-v",
        "ON_ERROR_STOP=1",
        "-d",
        os.environ.get("SCOUT1_DBNAME", "scout1"),
        "-U",
        os.environ.get("SCOUT1_DBUSER", "postgres"),
        "-t",
        "-A",
        "-F",
        "\t",
        "-v",
        f"symbol={symbol}",
        "-c",
        sql,
    ]

    host = os.environ.get("SCOUT1_DBHOST")
    if host:
        command[1:1] = ["-h", host]

    port = os.environ.get("SCOUT1_DBPORT")
    if port:
        command[1:1] = ["-p", port]

    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        stdin=subprocess.DEVNULL,
        text=True,
        timeout=30,
    )
    values = completed.stdout.rstrip("\n").split("\t")
    if len(values) != 5:
        raise ValueError(f"Expected 5 aggregate columns from psql, got {len(values)}")

    return dict(zip(("row_count", "min_ts", "max_ts", "min_close", "max_close"), values))


def _parse_timestamp(value: str) -> datetime:
    normalized = value.strip().replace(" ", "T", 1)
    if normalized.endswith("+00"):
        normalized = f"{normalized}:00"
    return datetime.fromisoformat(normalized)
