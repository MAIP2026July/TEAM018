# 05 Data, Model and Evaluation Strategy

## Problem as AI task

There are three different tasks here, and treating them separately keeps things honest:

| Task | Type | Approach |
|---|---|---|
| Is there a secret / unsafe setting / injection pattern? | Detection | **Deterministic rules and existing scanners.** Not ML. These must be predictable |
| How risky is this MR overall? | **Classification / ranking** (Low / Medium / High, or a 0-100 score used to rank the queue) | Rules in MVP, then a learned model (logistic regression or gradient boosting) on MR history |
| What should the reviewer know? | **Generation** | LLM, given the diff and the signals, writes a short explanation |

## Data sources

**Internal (main source)**
- MR metadata from the Git platform API: files changed, lines added/removed, labels, approvals, review comments, time to merge.
- Diffs (file paths and added lines).
- Revert commits and hotfix MRs that reference an earlier MR.
- Incident / bug tickets linked to commits or MRs.
- CI results: test pass/fail, scanner findings.

**External**
- Rule packs from open-source secret and SAST scanners.

**User-generated (from the product itself)**
- Reviewer overrides and reasons. These become the most useful data over time, because they are direct human labels.

**Not used:** author identity, seniority, team, past "bad MR" counts. See 07.

## Labelling / ground truth

The label is "did this MR cause a problem after merge?", defined as any of:
- reverted within 30 days,
- a hotfix MR within 14 days that references it or touches the same lines,
- linked to an incident ticket,
- a security finding traced back to it.

**Honest problems with this label**
- It under-counts. Many problems are fixed quietly without linking back to the original MR.
- It mixes severities. A typo revert and a production outage both count as 1. In the pilot I would weight by severity where incident data exists.
- Rare positives. Maybe 3-8% of MRs, so accuracy is a useless metric. A model that always says "fine" would be 95% accurate.

Reviewer overrides during the pilot give a second, cleaner source of labels.

## Baseline

The baseline is what teams already do informally: **look harder at big MRs (more than 300 changed lines).** Any model has to clearly beat this, otherwise it is not worth the complexity.

A second baseline for the pilot: the rules-only version (what the prototype runs). The learned model must beat the rules, not just the size rule.

## Model / API choice

- **MVP:** weighted rules. Transparent, no training data needed, easy to explain. Every signal and its points are shown.
- **Pilot:** logistic regression or gradient boosted trees on the same features plus a few more (file churn history, how many services import the changed file). I prefer something simple and explainable over a deep model. Per-feature contributions (or SHAP values for trees) map directly to the "Why" list in the UI.
- **LLM:** hosted API for the explanation, *or* a self-hosted model if code cannot leave the network. The LLM gets the signals as input and is told to explain only those. It does not produce the score. This limits hallucinated reasons.

## Prototype evaluation (synthetic data)

I wrote 24 synthetic MRs covering typical cases: docs, UI refactors, auth, payments, migrations, k8s, terraform, CI, dependency bumps, and a few traps. Each has an "after merge" outcome I assigned based on what typically happens with that kind of change. 11 of 24 are problem MRs (much higher than real life, on purpose, to have enough cases).

Results, computed live in the prototype's Evaluation tab:

| | Size baseline (> 300 lines) | Prototype (High band) |
|---|---|---|
| MRs flagged | 5 of 24 (21%) | 9 of 24 (38%) |
| Problem MRs caught (recall) | 1 of 11 (9%) | 8 of 11 (73%) |
| Flags that were real (precision) | 1 of 5 (20%) | 8 of 9 (89%) |
| False alarms | 4 (UI refactor, translations, export endpoint, lockfile bump) | 1 (MR-122, payment icons) |
| Missed problem MRs | 10 | 3 (MR-121, MR-123, MR-124) |

**What the misses teach**
- **MR-121, date utils refactor.** Small and tested, but used by 6 services. The tool has no idea about blast radius. This is the biggest gap, and it's why "how many places import this file" is on the pilot feature list.
- **MR-123, cache TTL change.** A 2-line config change with a business impact (stale prices). No rule can know that. Probably only reviewer judgement or incident history can.
- **MR-124, auth library upgrade.** Dependency bumps get a small score. A dependency used for auth should probably count as auth. That is an easy rule fix.

**What the false alarm teaches**
- **MR-122, payment icons.** The path contains `payments`, so it looks like payment logic. Path keywords over-trigger. A reviewer would override this, and that override is exactly the signal to fix the rule (e.g. ignore UI-only files for the payments rule).

**The big caveat:** I designed both the rules and the data, so the prototype is bound to do well. These numbers show the mechanism works. They are not evidence it will work on a real codebase. The shadow pilot is where that gets tested.

## Evaluation framework for the pilot

| Metric type | Metric | Why it matters |
|---|---|---|
| Technical | Recall of problem MRs in the High band | The whole point is not missing risky MRs |
| Technical | Precision of the High band | Too many false alarms = people ignore it |
| Technical | Recall at a fixed queue share (e.g. top 20% of MRs by score) | Fair way to compare with baseline at equal reviewer effort |
| Technical | LLM explanation accuracy (spot check 30 per week: is every stated reason actually in the diff?) | Catch hallucinated reasons early |
| Business | Problem MRs that reached production without senior/security review | The outcome we actually care about |
| Business | Median time-to-first-review for Low MRs | Low-risk work should move faster |
| Business | Senior reviewer hours spent on Low MRs | Is effort shifting to where it matters? |
| Trust / guardrail | Override rate (and direction: up vs down) | Rising override rate = model drifting or not trusted |
| Trust / guardrail | Share of queue flagged High | Alert fatigue guard |
| Trust / guardrail | Any High-severity incident from an MR rated Low | Every case reviewed |

## Launch / go-no-go thresholds

**Move from shadow to advisory pilot if:**
- recall of past problem MRs in High is clearly above the size baseline (aim > 60%), and
- High covers under ~30% of the queue, and
- no hard-rule (secret/unsafe) case was missed.

**Move from advisory pilot to wider rollout if:**
- override rate stays under 25% over 6 weeks,
- reviewer usefulness rating is 3.5 or more out of 5,
- explanation spot checks are accurate in more than 80% of cases,
- no serious incident came from an MR the tool rated Low without a reviewer override.

**Stop if:** reviewers stop opening the panel, override rate keeps rising, or the label data turns out too sparse to evaluate anything.
