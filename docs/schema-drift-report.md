# Schema Drift Report — 2026-06-12

## Migration Chain

```
0001_initial_schema (initial) 
  → 960bef3e8fab_add_meta_data_to_papers 
  → 1327a1c5b9d4_switch_to_384d_embeddings 
  → 4e8f2c1a6b3d_switch_to_2048d_embeddings 
  → 5a1b2c3d4e5f_fix_artifact_paper_id_cascade (NEW - this sprint)
```

## Drift Found & Fixed

| Table | Column | Issue | Fix |
|---|---|---|---|
| `artifacts` | `paper_id` FK | Missing `ondelete="CASCADE"` in initial migration (model had it) | Migration `5a1b2c3d4e5f` drops and recreates FK with `ondelete="CASCADE"` |

## Verified — No Drift

| Table | Column | Check |
|---|---|---|
| `papers` | `meta_data` | Model matches migration `960bef3e8fab` |
| `papers` | `updated_at` | Migration `960bef3e8fab` dropped it — model correctly lacks it |
| `artifacts` | `embedding` | Model: `Vector(2048)` — final migration `4e8f2c1a6b3d` sets it |
| `paper_chunks` | `embedding` | Model: `Vector(2048)` — final migration `4e8f2c1a6b3d` sets it |
| `users` | all columns | Model matches initial migration `0001` |
| `conversations` | all columns | Model matches initial migration `0001` |
| `annotations` | all columns | Model matches initial migration `0001` |
| `collections` | all columns | Model matches initial migration `0001` |
| `daily_digests` | all columns | Model matches initial migration `0001` |
| `usage_events` | all columns | Model matches initial migration `0001` |

## Migration Commands

```bash
# Run the new migration
cd apps/api && alembic upgrade head

# Check current migration version
alembic current

# View migration history
alembic history
```

## Conclusion

All models now match their database schema exactly. One corrective migration was required to fix the missing `ondelete="CASCADE"` on the `artifacts.paper_id` foreign key constraint. All other columns, types, constraints, and defaults are consistent.
