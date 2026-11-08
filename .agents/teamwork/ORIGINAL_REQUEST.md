# Original User Request

## Initial Request — 2026-11-03T04:42:49Z

Address the stress-test audit findings and verdict from Claude Court Case #002 for CampusPulse by implementing the recommended fixes across the platform locally, keeping changes focused and minimal (/ponytail) with zero regressions and no git push.

Working directory: c:\Users\priya\Desktop\Final_Hack
Integrity mode: development

Reference: c:\Users\priya\Desktop\Final_Hack\Claude Court Case #002, CampusPulse.pdf

## Requirements

### R1. Core Focus & Navigation Hierarchy
Narrow the core platform focus to explainable early-warning and advisor intervention tracking, outputting accreditation-ready evidence. In the primary navigation and user hierarchy, de-emphasize peripheral student tools (coding lab, mock interviewer) by moving them to secondary/lab navigation so the core advisor workflow takes center stage while keeping those tools accessible.

### R2. Scoring & Machine Learning Positioning
Maintain the core student success scoring as 100% deterministic and explainable. Position machine learning strictly as an optional, audited fairness proxy add-on rather than presenting both as the core engine.

### R3. Configurable & Justified Thresholds
Support configurable alert thresholds in the UI and API, defaulting to standard institutional policies (e.g., 75% attendance rule). Provide explicit documentation and rationale for the 57% emergency hard-floor threshold.

### R4. Data Ingestion & Accreditation Claims
Ensure CSV and Excel upload is surfaced as the primary data ingestion path across the interface and documentation. Soften institutional marketing and accreditation claims from "NAAC A++ forecasting" to "NAAC SSR Readiness & Evidence Dossier" with clear metric validation.

### R5. Local Execution & Git Push Constraint
All modifications must remain strictly local. The team must NOT execute git push or push any code, commits, or branches to remote repositories.

## Acceptance Criteria

### Primary Workflows & Hierarchy
- [ ] Primary navigation hierarchy places advisor early-warning, triage lists, and intervention tracking front and center.
- [ ] Peripheral student tools (coding lab, mock interviewer) are moved to secondary navigation sections.
- [ ] CSV/Excel data upload is accessible and surfaced as the primary ingestion method in the user flow.

### Deterministic Core & ML Decoupling
- [ ] Core early-warning calculations remain 100% deterministic and explainable.
- [ ] ML features operate as an optional, audited fairness proxy add-on without replacing or obscuring deterministic scoring.

### Thresholds & Positioning
- [ ] Attendance and alert thresholds can be configured in UI/API, with default standard attendance at 75%.
- [ ] Codebase or documentation explicitly justifies the 57% emergency hard-floor.
- [ ] Accreditation references use "NAAC SSR Readiness & Evidence Dossier" with metric validation rather than "NAAC A++ forecasting".

### Local Integrity & Zero Regressions
- [ ] No git push command is executed; repository remotes are untouched.
- [ ] All 80 existing pytest tests pass with zero regressions.
- [ ] New unit tests cover modified functionality (threshold configuration, ingestion path, and score explainability).


## Follow-up — 2026-11-03T04:57:20Z

The server restarted. Please resume and continue right where you stopped on the approved task prompt for the Claude Court Case #002 fixes:

- Phase 0 survey synthesis into PROJECT.md and execution of the implementation milestones.
- Keep the changes focused, minimal (/ponytail), zero regressions across all 80 tests.
- STRICT CONSTRAINT: DO NOT GIT PUSH. All changes remain strictly local.
