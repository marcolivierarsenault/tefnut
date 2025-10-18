# Repository Guidelines

## Project Structure & Module Organization
This repository ships a uv-managed Python 3.13 service. Entry point `main.py` starts the scheduler and background jobs. Package code in `tefnut/` splits into `control/` (device orchestration, Ecobee clients), `utils/` (shared helpers), and `webui/` (Flask views/assets). Configuration templates sit in `_template.settings.toml` and `misc/`. Tests replicate the layout under `tests/`. Operational scripts (`deploy.sh`, `setup.sh`) and CI settings (`.github/`, `sonar-project.properties`, `codecov.yml`) reside at the root. uv pins Python 3.13 via `pyproject.toml`, so `uv sync` ensures the interpreter is installed automatically.

## Build, Test, and Development Commands
Initial setup: run `uv sync --extra dev` or `./setup.sh` to install uv, dependencies, and the pre-commit hooks. Launch locally with `uv run python main.py` after configuring Dynaconf settings. Execute `uv run pytest` for the suite; append `--cov=tefnut --cov-report=term-missing` to audit coverage like CI. Lint/format via `uv run ruff check .` (auto-fix enabled) and `uv run ruff format .`. Run `uv run pre-commit run --all-files` before each push to mirror CI.

## Coding Style & Naming Conventions
Use 4-space indentation, UTF-8 source encoding, and `snake_case` module/function names. Classes stay `PascalCase`; constants go in `UPPER_CASE`. Prefer type hints for new surfaces, especially public APIs in `tefnut/control`. Shared helpers belong in `tefnut/utils`; keep web assets paired with `webui/`. Run Ruff prior to committing—CI treats violations as failures—and let pyupgrade modernize syntax to Python 3.9+.

## Testing Guidelines
Tests sit in a mirrored module path (`tests/control/test_<module>.py`, etc.). Follow pytest naming (`test_*`) and lean on fixtures from `tests/common.py` and `tests/conftest.py` before adding new ones. `pytest.ini` promotes warnings to errors; fix deprecations rather than muting them. Use `uv run pytest -k <keyword>` for targeted runs, but finish with the full suite plus coverage to maintain codecov quality gates.

## Commit & Pull Request Guidelines
Write concise, present-tense commit titles in the style of `update to Python 13` or `Bump ruff to 0.12.12`. Keep version bumps isolated from feature work. Every PR should describe intent, list validation commands executed, and link tracking issues. Attach screenshots or logs when touching `webui/` or deployment scripts. Confirm GitHub Actions jobs are green before requesting review.

## Configuration & Deployment Tips
Seed new environments from `_template.settings.toml`, exporting secrets via Dynaconf instead of committing them. `deploy.sh` expects uv on the host, sudo access to `tefnut.service`, and installs the Raspberry Pi GPIO shim. Document any additional system dependencies in the README or project wiki so operators can reproduce the installation.
