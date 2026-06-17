# London Housing — dbt project

This repository contains a starter dbt project for transforming and analyzing London housing data. It is scaffolded for use with a local DuckDB file and includes a Python virtual environment for development.

**Status:** Project scaffolded — models, seeds, macros, and tests are placeholders and need to be implemented.

**Contents:**
- `london_housing.duckdb` — local DuckDB database file (project data store)
- `env/` — Python virtual environment used for development
- `london_housing/` — the dbt project (models, macros, seeds, snapshots, tests)

## Quickstart

1. Activate the Python virtual environment (provided):

	```bash
	source env/bin/activate
	```

2. Install dbt and dependencies (if not already installed):

	```bash
	pip install dbt-core dbt-duckdb duckdb
	```

3. Configure your dbt `profiles.yml` to use DuckDB. A minimal example:

	```yaml
	london_housing:
	  target: dev
	  outputs:
		 dev:
			type: duckdb
			path: ../london_housing.duckdb
			threads: 1
	```

	Place this under your `~/.dbt/profiles.yml` or the location dbt expects.

4. Run dbt commands from the `london_housing` project directory:

	```bash
	cd london_housing
	dbt debug
	dbt seed     # if you add seed CSVs in seeds/
	dbt run
	dbt test
	dbt docs generate
	dbt docs serve
	```

## Project structure

- `models/staging/` — raw staging models (currently empty)
- `models/intermediate/` — intermediate transformations (currently empty)
- `models/marts/` — business-facing marts (currently empty)
- `seeds/`, `macros/`, `snapshots/`, `tests/` — placeholders (.gitkeep)

## Development notes

- The project is a starter scaffold. Add source data (or seeds) and implement models under `models/`.
- Use `london_housing.duckdb` for local testing and lightweight analytics.
- Keep `dbt_project.yml` and model configs up to date to control materializations and environment-specific behavior.

## Next steps (suggested)

1. Add `profiles.yml` and verify `dbt debug` passes.
2. Add source definitions and staging models under `models/staging/`.
3. Implement intermediate models and data quality tests.
4. Build marts and document with `dbt docs`.

## Help and resources

- dbt docs: https://docs.getdbt.com
- dbt community: https://community.getdbt.com

---
_This README was generated from the current project scaffold. If you want, I can add a sample `profiles.yml`, a basic staging model, or CI instructions next._
