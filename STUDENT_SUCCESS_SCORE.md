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

## 3. Tier classification, safety floors, and configurable thresholds

CampusPulse implements a two-tier safety architecture distinguishing between routine institutional policy alerts and emergency hard-floor circuit breakers.

### 3.1 Two-Tier Alert & Safety Floor Framework

| Threshold Level | Metric Target | Institutional Role & Policy Mapping | Operational Trigger |
| :--- | :---: | :--- | :--- |
| **Institutional Standard Alert** | $\text{Attendance} < 75.0\%$ | Statutory UGC/AICTE exam eligibility threshold. Configurable per institutional regulation. | Alerts advisor for early check-in, mentoring contact, and attendance recovery plan. |
| **Academic Warning Alert** | $\text{CGPA} < 6.0$ | Academic probation boundary (standard grade scale threshold). | Schedules academic tutoring clinic and subject review. |
| **Backlog Warning Alert** | $\text{Backlogs} \ge 2$ | Credit accumulation risk threshold. | Reviews course load and exam registration plan. |
| **Emergency Hard-Floor** | $\text{Attendance} < 57.0\%$ | Mathematical point of exam ineligibility impossibility. Safety circuit breaker. | Immediately overrides tier to **Priority Support [PINNED]**; pins student to top of advisor queue. |
| **CGPA Emergency Hard-Floor** | $\text{CGPA} < 4.7$ | Severe semester credit progression stall limit. | Overrides tier to **Priority Support [PINNED]**. |
| **Backlog Emergency Hard-Floor**| $\text{Backlogs} \ge 3$ | Imminent academic disqualification/curriculum stall. | Overrides tier to **Priority Support [PINNED]**. |

### 3.2 Mathematical Derivation of the 57% Emergency Hard Floor

A central question in academic policy design is: *Why 57% attendance rather than a routine warning at 75%?*

The 57.0% attendance cutoff is not an arbitrary heuristic—it represents the **mathematical point-of-no-return** in a standard collegiate semester.

#### Formal Derivation:
1. **Academic Calendar Baseline**: In a standard university term of 15 instructional weeks (approx. 75 teaching days), midterm performance reviews and advisor intervention cycles take place around **Week 9**.
2. **Term Elapsed Proportion**: Week 9 represents exactly 60% of the instructional semester completed ($t_{\text{elapsed}} = \frac{9}{15} = 0.60$). The remaining period comprises 6 weeks or 40% of the term ($t_{\text{remaining}} = \frac{6}{15} = 0.40$).
3. **Cumulative Attendance at Week 9**: A student possessing a 57.0% cumulative attendance rate at the Week 9 assessment point has accrued:
   $$\text{Attended Share} = 0.60 \times 57.0\% = 34.2\% \text{ of the total semester instruction}$$
4. **Best-Case Forward Trajectory**: Even if the student exhibits **flawless, 100.0% perfect attendance** for every single class across the remaining 6 weeks ($t_{\text{remaining}} = 0.40$):
   $$\text{Max Attainable Final Attendance} = 34.2\% + (0.40 \times 100.0\%) = 34.2\% + 40.0\% = 74.2\%$$
5. **The Impossibility Condition**:
   $$74.2\% < 75.0\% \quad \text{(Statutory Minimum)}$$
   Because 74.2% falls strictly below the statutory 75.0% threshold mandated by UGC and AICTE regulations, it is **mathematically impossible** for the student to achieve exam eligibility through regular class attendance alone.
6. **Pedagogical Conclusion**: 
   - A student between 57% and 75% attendance can still be mathematically rescued through faculty mentoring and attendance recovery agreements.
   - Below 57%, routine coaching cannot mathematically salvage exam eligibility. The student must be **pinned to Priority Support** for formal administrative intervention: statutory condonation petitions, medical/hardship documentation reviews, or remedial supplementary schedules.

### 3.3 Configurable Thresholds API & In-Memory Overlay

Institutions operate under varying statutory regulations (e.g., medical condonation allowances, autonomous college rules). CampusPulse provides dynamic threshold management:
- `GET /api/v1/config/thresholds`: Returns active alert thresholds, default institutional policy references, and the mathematical derivation.
- `PUT /api/v1/config/thresholds`: Allows authorized administrators to customize alert boundaries (e.g., standard attendance $\in [60, 90]\%$, emergency floor $\in [40, 70]\%$) with strict validation guaranteeing that $\text{attendance\_emergency\_min} < \text{attendance\_standard\_min}$ and $\text{cgpa\_emergency\_min} < \text{cgpa\_warning\_min}$.
- `POST /api/v1/config/thresholds/reset`: Restores canonical UGC/AICTE defaults.

### 3.4 Tier Classification Precedence

To guarantee zero false negatives for high-risk students, tier classification evaluates safety floors before score bands:

1. Hard floor trigger:
   $$\text{Attendance} < 57.0\% \quad \lor \quad \text{CGPA} < 4.7 \quad \lor \quad \text{Backlogs} \ge 3 \implies \mathbf{Priority\ Support\ [PINNED]}$$
2. Review band:
   $$57.0\% \le \text{Attendance} \le 63.0\% \quad \lor \quad 4.7 \le \text{CGPA} \le 5.3 \implies \mathbf{Review}$$
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
