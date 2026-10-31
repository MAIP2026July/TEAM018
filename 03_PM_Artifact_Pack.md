# 03 PM Artifact Pack

## Problem statement

Engineering teams review every merge request with roughly the same effort, while the risk of MRs varies a lot. Reviewers have no quick, consistent way to see which MRs carry real risk (security, data, payments, infra, untested logic) and what to check. As a result, small high-risk changes get a light review and incidents follow, while senior time goes into large low-risk MRs.

**The decision being improved:** for each open MR, *how much review does this need, and from whom?*

## Product vision

The reviewer opens the queue and sees it sorted by risk, with a one-line reason for each MR. Risky MRs get the right people automatically suggested. Low-risk MRs move faster. The reviewer is still the one who decides.

## PRD-lite

**User problem.** Reviewers cannot tell which MRs are risky without opening each one, so they triage by age or size.

**Core workflow**
1. Developer opens or updates an MR.
2. The assistant extracts features from the diff: paths touched, size, test changes, risky patterns, dependency and config changes.
3. Deterministic checks run first (secrets, privileged containers, open firewall, injection patterns). These cannot be "outvoted" by the model.
4. The risk model gives a score 0-100 and a band.
5. The LLM writes a 2-4 sentence explanation from the signals and the diff.
6. The result appears in the MR and in the reviewer's queue, sorted by risk.
7. The reviewer accepts the band or overrides it with a reason.
8. After merge, outcome signals (revert, hotfix within 14 days, linked incident) are collected for evaluation and retraining.

**AI role**
- *ML model:* risk scoring, learned from the team's own MR history.
- *LLM:* explanation and review suggestions in plain language.
- *Not AI:* secret/unsafe-config detection and routing rules. These are deterministic on purpose.

**Requirements (MVP)**

| # | Requirement | Notes |
|---|---|---|
| R1 | Score every MR within 2 minutes of opening / update | Must not slow down the developer |
| R2 | Show band + top 3 reasons + suggested review path | Reasons must point to files / lines |
| R3 | Secret or unsafe-config hit always forces High | No model can lower it |
| R4 | Reviewer can override with a mandatory reason | Stored for learning and audit |
| R5 | Mark scores close to a band threshold as "uncertain" | Avoid false precision |
| R6 | Never block or auto-approve a merge | Advisory only |
| R7 | Do not use author identity / seniority as a feature | Fairness and trust |
| R8 | Log score, signals, decision and outcome per MR | For evaluation and audit |

**Data assumptions**
- We can get at least 6-12 months of MR history from the Git platform API.
- We can label "problem MRs" from reverts, hotfix MRs that reference them, and incident tickets linked to a commit. This labelling is noisy and incomplete (many problems are never linked back).
- Diff content may be sent to an LLM only if the company's data policy allows it.

**Risks** (detail in 07)
- False alarms cause alert fatigue and people stop looking.
- Misses create false confidence ("the tool said Low").
- Code confidentiality with an external LLM.
- Gaming: splitting changes to stay under the radar.

**Fallback logic**

| Situation | Behaviour |
|---|---|
| Model or LLM unavailable | Show rule-based score only, clearly labelled "rules only" |
| Score near a threshold | Show band as uncertain, suggest the reviewer decide |
| Diff too large to analyse | Mark as "not analysed, needs manual triage", never silently Low |
| Unknown file types / new folders | Fall back to rules, flag "low confidence" |

## Feature prioritisation (RICE)

Reach = MRs per month affected (pilot team ~150). Impact on a 0.5-3 scale. Confidence %. Effort in person-weeks.

| Feature | Reach | Impact | Confidence | Effort | RICE | Priority |
|---|---|---|---|---|---|---|
| Rule-based risk score + reasons | 150 | 2 | 80% | 2 | 120 | MVP |
| Secret / unsafe-config detection (reuse scanners) | 150 | 3 | 90% | 1 | 405 | MVP |
| Override with reason + decision log | 150 | 1.5 | 80% | 1 | 180 | MVP |
| Risk-sorted queue view | 150 | 2 | 70% | 1.5 | 140 | MVP |
| LLM explanation | 150 | 1 | 60% | 2 | 45 | Pilot |
| Learned ML score | 150 | 2 | 50% | 4 | 37.5 | Pilot |
| Manager dashboard | 20 | 1 | 70% | 2 | 7 | Later |
| Auto reviewer assignment | 150 | 1 | 40% | 3 | 20 | Later |

The secret detection scores highest because it is cheap (reuse) and the impact of a miss is severe. The learned model scores lower than I expected. That is mostly the low confidence: we don't yet know if the labels from MR history are good enough. That is exactly what the pilot needs to find out.

## MVP definition

**The MVP proves one thing: risk-sorted triage with reasons helps reviewers put attention on the right MRs, and they trust it enough to use it.**

In scope: rule-based score, deterministic security checks, reasons, suggested review path, override with reason, decision log, risk-sorted queue.
Out of scope: learned model, LLM text, auto-assignment, dashboards, blocking.

The prototype in this repo is this MVP, running on synthetic MRs.

## Roadmap with proof gates

| Phase | Duration | What happens | Gate to move on |
|---|---|---|---|
| 0. Prototype | done | Clickable prototype, synthetic MRs, rules engine | Workflow makes sense to 3-5 reviewers I show it to |
| 1. Shadow pilot | 2 weeks | Score real MRs in 2-3 repos, log only, not shown to reviewers | On past problem MRs, recall clearly better than the size rule; flags under ~30% of queue |
| 2. Advisory pilot | 6 weeks | Show score + reasons in MR, collect overrides | Override rate < 25%; reviewers say it's useful (survey); no "missed High" incident |
| 3. Add ML + LLM | 4-6 weeks | Train model on labelled history, add LLM explanation | Model beats rules on held-out data; explanation rated accurate in > 80% of spot checks |
| 4. Scale to more teams | later | Per-team calibration, dashboard | Same gates hold for a second team |

The difference from a normal software roadmap is that each phase has a *learning* gate, not just a delivery date. If a gate fails, we stop or fix, we don't push ahead.

## Success metrics

| Type | Metric | Target for pilot |
|---|---|---|
| Product | % of MRs where the reviewer opened the risk panel | > 60% |
| Product | Reviewer usefulness rating (1-5) | ≥ 3.5 |
| Business | Recall of problem MRs in High band (vs size rule) | Clearly higher than baseline, aim > 60% |
| Business | Median time to first review for Low-risk MRs | Goes down |
| Business | Problem MRs that reached production without senior/security review | Goes down |
| Trust / guardrail | Override rate | < 25% |
| Trust / guardrail | Share of queue flagged High | < 30% (alert fatigue guard) |
| Trust / guardrail | High-severity incident from an MR the tool rated Low | 0 in pilot, every case reviewed |

## How these artifacts change because it is an AI product

| Artifact | Normal version | What changed here |
|---|---|---|
| Problem statement | "Reviews are slow" | Framed around a *decision*: how much review an MR needs, and from whom |
| User story | "As a reviewer I want a list" | Includes error cost: what happens when the score is wrong and how the user notices |
| PRD | Features and acceptance criteria | Added data assumptions, labelling source, fallback behaviour, things the model must never decide |
| Prioritisation | Value vs effort | Confidence in the data is a real factor. The learned model drops in priority because the labels are uncertain |
| Roadmap | Dates and releases | Proof gates. Shadow mode before showing anything to users |
| Metrics | Usage, time saved | Model metric (recall) tied to business metric (problem MRs caught) and a guardrail (queue share, override rate) |
| Launch checklist | QA sign-off | Plus: rollback to rules-only, override path, audit log, no blocking |
