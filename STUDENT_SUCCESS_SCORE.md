# Student success score and risk identification framework
> Technical and methodology documentation: CampusPulse v5.0

## 1. Summary and design principles

The student success score combines academic, attendance, placement, and engagement indicators to help faculty advisors identify students who need support early in the semester.

### Core principles

1. Focus on early support: The scoring model isolates specific friction points, such as low LMS activity or coding test gaps, so advisors can offer targeted coaching.
2. Deterministic calculation: Scores use fixed arithmetic formulas rather than language models or probabilistic routines. Each point links to a verified metric.
3. Parameter governance: Target baselines and weights live in `TARGETS.yaml`, validated at startup with a SHA-256 hash.

## 2. Key indicators and sub-index calculations

The overall success score integrates six dimensions:

$$\text{Success Score} = 0.25 \cdot I_{\text{academic}} + 0.20 \cdot I_{\text{attendance}} + 0.20 \cdot I_{\text{placement}} + 0.15 \cdot I_{\text{lms}} + 0.10 \cdot I_{\text{engagement}} + 0.10 \cdot I_{\text{skills}}$$

### Sub-index formulas

| Indicator | Weight | Formulation | Rationale |
| :--- | :---: | :--- | :--- |
| Academic ($I_{\text{acad}}$) | 25% | $\text{clamp}(\text{CGPA} \times 10 - 3 \times \min(\text{backlogs}, 5), 0, 100)$ | Academic baseline penalized for active backlogs. |
| Attendance ($I_{\text{att}}$) | 20% | $\text{clamp}(\mu_{\text{att}} - 5 \times N_{\text{sub} < 60\%}, 0, 100)$ | Penalizes subject-level absenteeism even if average attendance is acceptable. |
| Placement ($I_{\text{place}}$) | 20% | $0.35 \cdot \text{Aptitude} + 0.40 \cdot \text{Coding} + 0.25 \cdot \text{MockInterview}$ | Placement readiness indicator. Uses general assessment sub-score when coding logs are absent. |
| LMS Engagement ($I_{\text{lms}}$) | 15% | $0.50 \cdot \text{CompletionPct} + 0.50 \cdot \text{ScaledLogins}$ | Measures regular participation in course portal tasks. |
| Campus Engagement ($I_{\text{eng}}$) | 10% | $\text{clamp}\left(\frac{\text{WinsorizedSum}(\text{events}, \text{clubs}, \text{hackathons}, \text{certs})}{20} \times 100, 0, 100\right)$ | Extracurricular activities, winsorized at the 95th percentile to limit extreme outlier skew. |
| Skills Profile ($I_{\text{skills}}$) | 10% | $0.60 \cdot \text{TechnicalAssessment} + 0.40 \cdot \text{SoftSkills}$ | Technical competency and interpersonal evaluation. |

## 3. Tier classification and safety rules

To keep high-risk students visible even when they score well on other dimensions, tier classification evaluates safety floors before score bands:

1. Hard floor trigger:
   $$\text{Attendance} < 57\% \quad \lor \quad \text{CGPA} < 4.7 \quad \lor \quad \text{Backlogs} \ge 3 \implies \mathbf{Priority\ Support\ [PINNED]}$$
2. Review band:
   $$57\% \le \text{Attendance} \le 63\% \quad \lor \quad 4.7 \le \text{CGPA} \le 5.3 \implies \mathbf{Review}$$
3. Score bands:
   $$\begin{cases} 
   \text{Score} \ge 60 \implies \mathbf{On\ Track} \\
   40 \le \text{Score} < 60 \implies \mathbf{Watchlist} \\
   \text{Score} < 40 \implies \mathbf{Priority\ Support}
   \end{cases}$$

## 4. Student segmentation rules

Students are assigned to one mutually exclusive segment each week in this order of priority:

1. Struggling on All Fronts: Tier is `priority_support` with 4 or more sub-indices below cohort 25th percentile ($p_{25}$).
2. Academic Stars with Placement Gap: Strong academic score ($I_{\text{acad}} \ge 75$) alongside lower placement readiness ($I_{\text{place}} \le p_{25}$).
3. Hustlers at Academic Risk: High campus engagement ($I_{\text{eng}} \ge 75$) but academic index falling below the cohort quartile ($I_{\text{acad}} < p_{25}$).
4. Quietly Disengaged: Acceptable attendance ($I_{\text{att}} \ge 60\%$) paired with low LMS and campus activity ($I_{\text{lms}}, I_{\text{eng}} < p_{25}$).
5. Balanced: Standard progression meeting department targets across all six dimensions.

## 5. Priority ranking for advisors

The advisor action list ranks students using this urgency index:

$$\text{Priority Score} = (0.50 \cdot \text{Severity} + 0.25 \cdot \text{Actionability} + 0.25 \cdot \text{Urgency}) \times \text{MomentumBoost}$$

- Pinned hard-floor students: Stay at the top of the advisor queue regardless of aggregate points.
- Actionability weighting: Prioritizes students whose primary risk factor corresponds to a standard intervention template (such as an attendance review or coding practice clinic).
- Queue presentation: Displays the student tier, the primary risk driver, and direct intervention logging options in one view.
