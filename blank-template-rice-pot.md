**Title**: Enterprise Request-Python API Testing Framework Instructions

**Overview**:
- **Purpose**: Define a production-grade Request-based Python API testing framework specification suitable for CI/CD, service virtualization, contract testing, and large-scale automation teams.
- **Scope**: RESTful API functional and contract testing, smoke/regression workflows, resilient network handling, secrets-safe configuration, and developer-friendly SDK-style API object model.

**Objective**:
- Generate an enterprise-ready, maintainable, and scalable API test framework using the `requests` ecosystem and pytest, implementing an API Object Model and production patterns used in UI automation but optimized for API layer testing.

**Role**: Principal API Test Automation Architect with 15+ years of experience delivering enterprise API testing platforms.

**Authoritative Requirements**:

**Critical**:
- Implement pytest with comprehensive fixture scope management (`function`, `class`, `module`, `session`) and fixture teardown using `yield`.
- Centralize configuration via pydantic settings (`BaseSettings`) and load runtime secrets via python-dotenv; never hardcode secrets or base URLs.
- Use a single `requests.Session()` instance per test session for connection pooling and performance.
- Implement retry and backoff via `tenacity` for all service-layer network calls.
- Handle network/HTTP errors, `requests` exceptions, and JSON decoding errors in the service layer only; tests must receive deterministic failures (no try/except swallowing in tests).

**Mandatory**:
- Implement an API Object Model: `BaseClient` with typed request/response helpers, separate service classes (e.g., `PetService`, `StoreService`, `UserService`) that expose business-level methods.
- Use Python `typing` and `dataclasses` (or pydantic models where stricter validation is required) for request and response DTOs.
- Strictly use `requests` and `requests.Session()`; do not introduce alternate HTTP clients.
- Provide reusable request methods for `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, supporting query params, headers, timeouts, streaming, and file uploads.
- Implement structured logging with `loguru` (no `print()` statements). Configure log levels and structured outputs for CI ingestion.

**Quality & Reliability**:
- Adopt circuit-breaker or bulkhead patterns for external dependency protection (can be a simple in-process circuit with thresholds and time windows).
- Aim for high stability: retries + idempotent test design + environment isolation to reduce flakiness.

**Security**:
- Use `.env` and environment variables for secrets; support optional Vault integration via pluggable provider (configuration only, no secret storage in repo).
- Never log secrets; redact sensitive headers and bodies before persisting logs.

**Don't**:
- Do not hardcode base URLs, credentials, or tokens in code or tests; use pydantic settings and `.env` files.
- Do not use `time.sleep()` anywhere; implement retry/backoff with `tenacity` and pytest-timeout for tests.
- Do not catch and swallow exceptions in test code; let assertions and service-layer exceptions surface to pytest.
- Do not use `print()` or `sys.stdout` for validations; use asserts and structured logging.
- Do not use alternate HTTP libraries (`httpx`, `urllib3` direct, `aiohttp`)—use `requests` exclusively.

**Output**:
- Output only runnable Python code when implementing scaffolding.
- Provide a minimal, reviewable set of files to start: `conftest.py`, `settings.py`, `base_client.py`, `pet_service.py`, `test_pet_workflow.py`.

**Generate**:
- Generate the following files as the initial scaffold and maintain separation of concerns:
	- `conftest.py` - pytest fixtures, session-scoped `requests.Session`, settings fixture, and test data fixtures.
	- `settings.py` - pydantic `BaseSettings` for configuration (base_url, timeouts, retries, credentials loader from `.env`).
	- `base_client.py` - `BaseClient` implementing session management, typed request helpers, tenacity-based retry decorators, JSON parsing, error mapping, and circuit-breaker hooks.
	- `pet_service.py` - example service class implementing API Object Model for the Pet endpoints (business methods using DTOs).
	- `test_pet_workflow.py` - pytest tests demonstrating valid and invalid testcases driven by fixtures and `@pytest.mark.parametrize`.

**Folder Layout**:
- `config/` - `config.example.env`, `logging.yml` (or python logging config), and optional `ci/` pipeline snippets.
- `services/` - service classes (`pet_service.py`, `user_service.py`, etc.).
- `clients/` - `base_client.py` and helpers.
- `models/` - dataclasses or pydantic models for DTOs.
- `tests/` - test modules organized by feature; `test_*.py` naming conventions.
- `reports/` - allure results, junit xml output, and artifacts.

**Test Design Guidance**:
- Favor end-to-end happy-path and negative-path tests with parametrized datasets. Use idempotent interactions or cleanup steps in fixtures.
- Keep assertions at the test level; service methods should return typed responses or raise well-defined exceptions.
- Use schema/contract assertions for responses (e.g., pydantic model validation) where contract stability is required.

**CI/CD Integration**:
- Provide a `ci/` job template for GitHub Actions or GitLab CI that installs test deps, runs pytest with `--junitxml` and `--alluredir` flags, and uploads artifacts on failure.
- Fail fast on critical contract violations; generate flakiness metrics using retry counts and attach them to reports.

**Service Virtualization & Contract Testing**:
- Recommend WireMock or MockServer for isolating external dependencies in CI. Provide guidance on toggling virtualization via settings flags.
- For contract testing, integrate with pact-like tools or implement schema checks via pydantic models.

**Reporting**:
- Support Allure for detailed step-level reporting and attachments (request/response payloads redacted), and produce JUnit XML for CI.

**Logging & Observability**:
- Log request/response metadata (method, path, status, duration) and redact sensitive fields; emit structured JSON logs compatible with ELK/Datadog.

**Acceptance Criteria for Initial Deliverable**:
- A reviewed instruction document (this file) approved by the automation architect.
- The scaffolding files (`conftest.py`, `settings.py`, `base_client.py`, `pet_service.py`, `test_pet_workflow.py`) generated and runnable in a virtualenv with pinned dependencies.

**Next Steps**:
- Upon approval, generate the scaffold files adhering exactly to these rules (no print statements, no sleeps, requests + tenacity + pydantic + loguru, pytest fixtures), then run a smoke test in CI.

**Conformance Notes**:
- No features beyond the stated toolset will be invented. All requirements map to mainstream, production-safe libraries and patterns.

# Blank RICE-POT Template

Copy this, fill each section, and hand it to your AI tool.

```
### R — Role
[Who should the AI act as? e.g., "expert QA tester with 15 years' experience"]

### I — Instructions
1. [First step]
2. [Second step]
...
Do NOT:
- [What the AI must never do]
- [Another hard rule]

### C — Context
- [Product / system / background the AI needs]
- [What inputs or files you are attaching]

### E — Example
[One sample row or snippet showing the ideal output]

### P — Parameters
- [Quality / accuracy / style constraints]
- [Determinism, traceability, length limits, no hallucination, etc.]

### O — Output
- Format: [CSV / JSON / Markdown table / code]
- Columns / structure: [exact spec, in order]

### T — Tone
[Technical / plain / formal / output-only]
```

## Recommended Parameters block (for factual or technical output)
```
- Output must be deterministic (same input → same output).
- Every assertion must be traceable to a provided input.
- If information is missing or unclear, respond exactly: "Insufficient information to determine."
- If a detail is inferred, label it exactly: "Inference (low confidence)".
- Do not invent features, IDs, APIs, error codes, UI elements, or behavior.
- Do not assume default or "typical" system behavior.
```
