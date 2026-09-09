# Tool 1A Interface Confirmation

## Scope

This document records the read-only investigation for Task 002. The PRD assumption to verify was:

```text
get_segment_ohlcv(dataset_version, segment, symbol_id, tf)
```

and the existence of derived OHLCV views named:

```text
v_ohlcv_4h_derived
v_ohlcv_1d_derived
v_ohlcv_1w_derived
```

## Result

Mismatch / not confirmed in this checkout.

The actual `scout1` / Tool 1A implementation containing `get_segment_ohlcv` and the derived view DDL is not present on `main` or on the local branches available during this investigation. Therefore the PRD interface cannot be confirmed from the available codebase.

Group B should remain blocked until the CTO Mentor confirms the correct Tool 1A source location or provides the actual interface contract.

## Evidence

The checked-out `main` tree contains only:

```text
.github/workflows/ci.yml
README.md
```

The exact function and view names were searched across all local Git refs:

```text
get_segment_ohlcv
v_ohlcv_4h_derived
v_ohlcv_1d_derived
v_ohlcv_1w_derived
```

No matches were found.

The only OHLCV-related source found across all refs was on branch `feat/task-001-health-check-backend`, in `scout1_tools/health_check/backend.py`. That code queries the base table `c1.ohlcv` directly:

```sql
select
  count(*) as row_count,
  min(o.ts) as min_ts,
  max(o.ts) as max_ts,
  min(o.c) as min_close,
  max(o.c) as max_close
from c1.ohlcv o
join c1.symbols s on s.symbol_id = o.symbol_id
where s.symbol = :'symbol';
```

The repository's existing `graphify-out/graph.json` was also checked for nodes matching the function name, the three view names, and `ohlcv`. It contained no matching Tool 1A interface nodes; its source metadata was dominated by local `.agents` skill files and CI metadata, not Tool 1A implementation files.

## Confirmed Interface

No actual `get_segment_ohlcv` signature was found.

No `v_ohlcv_4h_derived`, `v_ohlcv_1d_derived`, or `v_ohlcv_1w_derived` view DDL was found.

## Escalation

This is a blocking mismatch against the PRD assumption. Do not proceed with Group B tasks that depend on `get_segment_ohlcv(dataset_version, segment, symbol_id, tf)` or the three derived view names until the CTO Mentor supplies or confirms the Tool 1A interface.
