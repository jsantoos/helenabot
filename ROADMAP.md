# HelenaBot — Development Roadmap

> **Status:** Planned work | **Maintainer:** Project owner | **Last updated:** November 2026
>
> This roadmap describes proposed engineering work, not completed functionality or guaranteed delivery dates. Estimates are approximate and may change after implementation and review.

## Product direction

HelenaBot is a Python-based AI assistant for working with uploaded documents across different knowledge domains. Its existing project structure includes document-processing and retrieval-augmented generation (RAG) components, with integrations such as Telegram. The product direction is to make document ingestion, management, retrieval, and user interaction reliable, secure, and easy to operate.

The next phase emphasizes **conventional software engineering**: upload workflows, validation, API contracts, persistence, access controls, automated tests, documentation, and operational reliability. **The tasks in this roadmap do not include training, fine-tuning, evaluating, or benchmarking ML models.** Support for a file type is considered complete only after its parser and safety behavior have been verified; the roadmap does not claim that every file type is already supported.

> **BYOP eligibility note:** HelenaBot includes AI/LLM-related functionality. Its eligibility for any program restricting ML work must be confirmed with the organizers; selecting only the tasks below does not establish eligibility. Public samples must be synthetic or properly licensed and free of confidential information.

## Planned work at a glance

| ID | Priority | Workstream | Estimated effort | Status |
|---|---|---|---:|---|
| HB-01 | P0 | Upload validation and file safety | 22 h | Planned |
| HB-02 | P0 | Document ingestion lifecycle and error handling | 22 h | Planned |
| HB-03 | P0 | Backend service and API contracts | 20 h | Planned |
| HB-04 | P0 | Automated unit and integration tests | 26 h | Planned |
| HB-05 | P1 | Document management and metadata | 20 h | Planned |
| HB-06 | P1 | Telegram interaction reliability | 16 h | Planned |
| HB-07 | P1 | Secrets, authorization, and safe logging | 24 h | Planned |
| HB-08 | P1 | CI and reproducible local setup | 18 h | Planned |
| HB-09 | P2 | Observability and troubleshooting | 16 h | Planned |
| HB-10 | P2 | Documentation and demonstration assets | 16 h | Planned |
| | | **Total planned independent development** | **200 h** | |

These are planning estimates, not logged hours or delivery commitments.

## Phase 1 — Ingestion and backend reliability (90 h)

### HB-01 — Upload validation and file safety (22 h)
**Goal:** Accept supported uploads predictably and reject unsafe or invalid inputs.

- [ ] Document an explicit allowlist of supported file formats and size limits.
- [ ] Validate file signatures, extensions, content types, and empty files.
- [ ] Reject path traversal, unsafe filenames, and oversized payloads.
- [ ] Provide actionable, non-sensitive validation errors.
- [ ] Add test fixtures for valid, malformed, and unsupported files.

**Done when:** Upload rules are documented and tested, and invalid files fail safely.

### HB-02 — Document ingestion lifecycle and error handling (22 h)
**Goal:** Make document processing repeatable and recoverable.

- [ ] Define document states such as received, processing, ready, and failed.
- [ ] Handle parser failures and partial ingestion without inconsistent records.
- [ ] Prevent unintended duplicate processing of the same document.
- [ ] Ensure temporary files are cleaned up after success or failure.
- [ ] Add tests for retries, failures, and interrupted processing.

**Done when:** Each ingestion attempt has a clear status and predictable failure behavior.

### HB-03 — Backend service and API contracts (20 h)
**Goal:** Establish consistent interfaces for uploads and document operations.

- [ ] Inventory existing Flask endpoints and service boundaries.
- [ ] Define stable request, response, and error schemas.
- [ ] Validate document identifiers and pagination inputs where applicable.
- [ ] Separate transport-layer handling from ingestion and storage logic.
- [ ] Document endpoint behavior with examples and negative-case tests.

**Done when:** Core application contracts are consistent, documented, and tested.

### HB-04 — Automated unit and integration tests (26 h)
**Goal:** Reduce regressions across file processing, persistence, and integrations.

- [ ] Expand pytest coverage for validation and ingestion services.
- [ ] Add isolated fixtures for document storage and metadata.
- [ ] Mock external LLM, messaging, and storage dependencies in routine tests.
- [ ] Cover timeout, malformed-response, and unavailable-service scenarios.
- [ ] Document deterministic test commands and cleanup steps.

**Done when:** Core non-ML application workflows run reliably in automated tests.

## Phase 2 — User workflows and safeguards (78 h)

### HB-05 — Document management and metadata (20 h)
**Goal:** Let users understand and control their uploaded content.

- [ ] Define metadata fields such as filename, type, upload time, and processing status.
- [ ] Implement consistent document listing and detail operations.
- [ ] Define deletion behavior for source files and associated stored artifacts.
- [ ] Add filters and pagination where useful.
- [ ] Test missing documents, duplicate names, and deletion failures.

**Done when:** Document records can be listed, inspected, and removed consistently.

### HB-06 — Telegram interaction reliability (16 h)
**Goal:** Improve the stability and clarity of the messaging experience.

- [ ] Standardize user-facing messages for upload, processing, and failure states.
- [ ] Handle invalid commands and unsupported attachments gracefully.
- [ ] Add timeout and retry handling for external integrations.
- [ ] Avoid duplicate responses to repeated incoming events.
- [ ] Add tests with mocked Telegram events and API responses.

**Done when:** Common user interactions have predictable outcomes and clear feedback.

### HB-07 — Secrets, authorization, and safe logging (24 h)
**Goal:** Reduce risks from uploaded content and external-service integrations.

- [ ] Audit environment variables and replace example secrets with placeholders.
- [ ] Document which files must never be committed to Git.
- [ ] Review user/document access boundaries and add denial tests.
- [ ] Prevent document contents, credentials, and personal data from leaking into logs.
- [ ] Define retention and deletion expectations for stored files and metadata.

**Done when:** Sensitive configuration and document access are protected by documented controls and tests.

### HB-08 — CI and reproducible local setup (18 h)
**Goal:** Make a clean checkout straightforward to build and validate.

- [ ] Add GitHub Actions for linting and automated tests.
- [ ] Verify Poetry dependency installation from a clean environment.
- [ ] Validate Docker and Docker Compose setup instructions.
- [ ] Provide a safe `.env.example` with clearly documented variables.
- [ ] Add checks for missing configuration and startup failures.

**Done when:** A contributor can set up and test the project from a fresh clone using documented steps.

## Phase 3 — Operations and onboarding (32 h)

### HB-09 — Observability and troubleshooting (16 h)
**Goal:** Diagnose common failures without exposing uploaded content.

- [ ] Introduce consistent structured application logging.
- [ ] Add request or job correlation identifiers where useful.
- [ ] Distinguish input-validation, integration, and infrastructure failures.
- [ ] Document health checks and common recovery procedures.
- [ ] Test stable error messages for representative failure cases.

**Done when:** Common operational issues can be diagnosed using non-sensitive signals.

### HB-10 — Documentation and demonstration assets (16 h)
**Goal:** Help external reviewers understand and reproduce the project.

- [ ] Align the README with verified current capabilities and repository structure.
- [ ] Document local startup, configuration, tests, and supported file formats.
- [ ] Add a concise architecture diagram and example user flows.
- [ ] Prepare a small demonstration using synthetic or redistributable documents.
- [ ] Add contribution guidance and issue templates.

**Done when:** An external reviewer can install, run, and understand the application without private documents or credentials.

## Suggested GitHub Issues

Create one issue for each roadmap item (`HB-01` through `HB-10`). Each issue should link to this roadmap, specify scope and acceptance criteria, and retain its estimate as a planning assumption. Suggested labels: `backend`, `ingestion`, `telegram`, `testing`, `security`, `devops`, `documentation`, `priority:P0`.

## Delivery and tracking

- Keep checkboxes unchecked until work is implemented and verified.
- Link completed work to actual issues, pull requests, and commits.
- Revise estimates and priorities openly as requirements become clearer.
- Do not fabricate commit history or imply planned features are already available.
- Use only synthetic, public-domain, or appropriately licensed demo documents; never publish confidential uploads or credentials.
- Obtain explicit program approval before using this AI-enabled repository in a restricted BYOP evaluation.

## License

Refer to the repository's license information. If no `LICENSE` file exists, do not assume the project is open source.
