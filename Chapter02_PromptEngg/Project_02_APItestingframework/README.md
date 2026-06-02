# AI Tester Blueprint — Request-based Python API Testing Framework

Opinionated scaffold for API testing using requests + pytest.

Quick start

1. Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Unix / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Create a `.env` from the example and customize if needed

Windows:

```powershell
copy .env.example .env
```

Unix/macOS:

```bash
cp .env.example .env
```

Default `BASE_URL` in `.env.example` points to the public Petstore API (https://petstore.swagger.io/v2).

4. Run tests

Run full suite:

```bash
python -m pytest -q
```

Run a single test:

```bash
python -m pytest test_pet_workflow.py::test_create_and_get_pet -q
```

Notes

- Configuration lives in `settings.py` via Pydantic `BaseSettings` and reads `.env`.
- `BaseClient` implements retry/backoff and a simple circuit breaker.
- CI: see `.github/workflows/ci.yml` for a sample GitHub Actions workflow.

License: None — this is scaffold code for internal use.
