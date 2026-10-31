# 04 UX, Workflow and Trust Design

## Design principle

It should feel like a colleague who glanced at the MR and said "careful, this touches auth and there are no tests". It should not feel like a gatekeeper. If developers feel judged or blocked, they will route around it.

## Main workflow

```
Developer opens MR
      |
      v
Assistant analyses diff (rules + scanners, later ML + LLM)
      |
      v
Risk band + reasons + suggested review path
      |                         |
      v                         v
Shown in MR (comment/panel)   Reviewer queue sorted by risk
      |
      v
Reviewer: Accept  or  Override (reason required)
      |
      v
Decision logged  ->  after merge, outcome collected (revert / hotfix / incident)
      |
      v
Used for evaluation and retraining
```

## Key user journey (reviewer)

1. Priya, a tech lead, has 18 open MRs on Monday morning.
2. She opens the review queue. It is sorted by risk instead of age. The top 3 are High: a Terraform change opening a firewall, an MR with what looks like an AWS key, and a payment rounding fix with no tests.
3. She opens the Terraform one. The panel says *"Unsafe infra setting: `source_ranges = ["0.0.0.0/0"]` in infra/terraform/db.tf. Suggested: platform review."* She tags the platform team.
4. The payment fix is marked High but "uncertain" (score close to the threshold). She looks, agrees it needs tests, and accepts.
5. A UI MR under a `payments/` folder is also High. She sees it only adds icons, overrides to Low with the reason "UI only, no logic". That override is logged.
6. The remaining Low MRs (README, translations, test-only) she approves quickly or leaves to a junior reviewer.

## Screens (prototype)

The prototype has these screens. Open `prototype/index.html` to see them.

| Screen | Purpose |
|---|---|
| Review queue | All open MRs sorted by score. Shows band, size and status |
| MR detail panel | Score bar, uncertainty warning, summary, signals with points, suggested review path, files |
| Reviewer decision | Accept, or override to another band with a mandatory reason |
| Decision log | All decisions with override rate. Export as JSON |
| Analyse a diff | Paste any `git diff` and see the analysis. Useful for demo and for developers to self-check before opening an MR |
| Evaluation | Baseline vs prototype on the synthetic set, with per-MR outcomes |

Text wireframe of the detail panel:

```
+--------------------------------------------------------------+
| MR-114 | Fix rounding in invoice total                       |
| [High risk] score 45/100   [=========-----------]            |
| ! Close to a band threshold. Treat the band as uncertain.    |
|                                                              |
| SUMMARY                                                      |
| Rated high mainly because of: payments / billing code;       |
| code changed, no tests changed; sensitive area without tests.|
|                                                              |
| WHY                                                          |
|  - Payments / billing code            +20  src/payments/...  |
|  - Code changed, no tests changed     +15                    |
|  - Sensitive area changed w/o tests   +10                    |
|                                                              |
| SUGGESTED REVIEW PATH                                        |
|  - Senior developer review                                   |
|  - Add or update tests                                       |
|  - Do not merge until the above reviews are done             |
|                                                              |
| [Accept High]   [Low/Med/High v] [reason........] [Override] |
+--------------------------------------------------------------+
```

## Trust and explainability

**What the user needs to know**
- The band, and the 2-3 main reasons, each pointing to a file or line.
- What to do about it (review path), not just a number.
- That it is advisory. The reviewer decides.

**What must be visible**
- Every signal with its points, so the score is never a black box.
- When the score is uncertain (near a threshold).
- When the analysis is degraded (rules only, diff too big, unknown files).

**What should be hidden**
- Raw model probabilities with many decimals. They suggest precision we don't have.
- Any per-developer "risk history". It is not used, and it should not appear anywhere.
- Secret values themselves. Show the file and line, mask the value.

## Uncertainty handling

| Case | Behaviour |
|---|---|
| High confidence (score clearly in a band) | Show band and reasons normally |
| Low confidence (within 4 points of a threshold) | Show band with "uncertain" warning, ask reviewer to decide |
| Hard rule hit (secret, privileged container, open firewall) | Always High, regardless of model. Explain the exact line |
| Failure / fallback | Model down: rules-only score, labelled. Diff too large or unparseable: "Not analysed, manual triage", never shown as Low |

## Human-in-the-loop

- **Every** band can be overridden, up or down, by the reviewer.
- Overrides need a short reason. This is a bit of friction on purpose: it stops blind clicking and gives us learning data.
- The tool never approves, merges or blocks.
- Security-relevant hard-rule hits (secrets) also notify the security channel, because those need action even if the MR is closed.
- Override reasons are reviewed every two weeks during the pilot. If the same override keeps appearing (like "UI only under payments folder"), the rule is fixed.
