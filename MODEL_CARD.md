# Model card: CampusPulse disagreement detector (`ml_layer`)

## Model details

- Model name: CampusPulse Disagreement Detector
- Version: 1.0.0-disabled
- Type: Supervised linear proxy and disagreement classifier
- Default status: Disabled. Deterministic rules in the domain layer hold primary authority.
- Scoring path separation: The model does not write to `tier`, `priority`, `segment`, or `score`. It only records `confidence_note` and `ml_agreement_boolean`.

## Governance guardrails (G1-G8)

| Guardrail ID | Description | CI enforcement |
| :--- | :--- | :--- |
| G1 | Model output does not write to tier, priority, segment, or score | Verified by unit tests and domain purity rules |
| G2 | Model output only writes `confidence_note` and `ml_agreement` | Enforced at layer return interface |
| G3 | On disagreement: lower confidence by one level and add a review note | Automated in `ml_layer.py` |
| G4 | Holdout AUC threshold $\ge 0.65$ | If $\text{AUC} < 0.65$, CI disables the feature flag |
| G5 | Proxy bias check: tier distribution shift $\le 5\%$ across departments | CI validation on department and section proxies |
| G6 | Temporal split enforcement ($t_{\text{train}} \le t_{\text{eval}}$) | Property testing via hypothesis |
| G7 | Transparent coefficient disclosure | Published below when enabled |
| G8 | Automatic failure fallback | Any G1-G7 violation reverts the flag to disabled |

## Feature weights and coefficients

When `ml_layer` is enabled:
- Academic Index: `0.30`
- Attendance Index: `0.25`
- Placement Index: `0.25`
- LMS Index: `0.20`

## Data boundaries and privacy

- Protected attributes (gender, caste, religion, socio-economic status) are not collected or ingested.
- Department and section are used only to detect differences in grading patterns across cohorts.
