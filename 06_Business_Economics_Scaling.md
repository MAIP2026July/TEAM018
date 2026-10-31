# 06 Business, Economics and Scaling

All numbers below are **assumptions** for a mid-sized product company, used to check whether the idea can make sense. None of them are measured. The pilot is where they get replaced with real numbers.

## Monetization model

**Primary: internal value case.** This is built for an internal engineering org. Nobody pays per MR. The question is whether it saves more engineering and incident cost than it costs to run.

**Later option: SaaS.** If it works well across several teams, it could be sold as a per-active-developer subscription (like most dev tools), with a self-hosted option for companies that cannot send code outside. I would not plan for this now. It is a different business with competitors already in the AI code review space.

## Value logic

The product creates value in three ways:
1. **Fewer escaped problems.** Risky MRs get the right reviewer before merge, so fewer reverts, hotfixes and incidents.
2. **Faster flow for low-risk MRs.** They can be reviewed faster or by a wider set of reviewers, so lead time drops.
3. **Better use of senior and security people.** Their time moves from "look at everything" to "look at what is flagged".

## Assumed org for the numbers

| Assumption | Value |
|---|---|
| Engineers | 60 |
| MRs per month | ~600 |
| Average review time per MR | ~30 min |
| Loaded cost of a senior engineer hour | ~₹2,000 |
| Problem MRs that cause a real incident per month | ~3 |
| Average cost of one incident (engineer time, firefighting, customer impact) | ~₹1.5 lakh |

## Cost drivers

| Cost | Estimate per month | Notes |
|---|---|---|
| LLM API | ~₹3,000-₹10,000 | ~600 MRs x one call each, a few thousand tokens per call. Depends heavily on model and diff size. Cap diff size sent |
| Compute for scoring + scanners | Small, runs in existing CI | Mostly already paid for |
| Build effort (one-off) | ~8-10 person-weeks | Integration, scoring, UI in MR, logging |
| Maintenance | ~1-2 days per month | Rule tuning from overrides, retraining |
| Review cost (human) | Goes *up* for High MRs, *down* for Low | This is intended. It is a shift, not just a saving |
| Privacy / security review of the tool itself | One-off | Especially if code goes to an external API |

## Unit economics view

Rough monthly view with the assumptions above:

- **Saving on low-risk reviews:** if 50% of MRs are Low and their review time drops from 30 to 20 min, that is 300 x 10 min = 50 hours, about ₹1 lakh.
- **Extra cost on high-risk reviews:** if 20% are High and get +20 min of senior/security time, that is 120 x 20 min = 40 hours, about ₹80,000.
- So the review time roughly evens out. **The real case is incidents:** if the tool helps prevent even 1 of the ~3 monthly incidents, that's about ₹1.5 lakh saved, against a running cost of maybe ₹10,000-₹20,000 a month.

The honest conclusion is that this is **not a "save reviewer time" product.** It is a risk-reduction product that is roughly neutral on review time. The pitch to management should be "fewer incidents for about the same review effort", not "faster reviews". If the pilot shows it doesn't reduce escaped problems, the business case is weak even if reviewers like it.

## Scaling risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| Latency | If the score appears 10 minutes after the MR, reviewers have already started | Run rules first (seconds), add LLM text when ready |
| Cost growth | LLM cost grows with MR count and diff size | Only call the LLM for Medium/High, cap tokens, cache by commit |
| Workflow complexity | Each team has different folders, conventions, risk areas | Per-repo config for sensitive paths, team-level calibration |
| Governance burden | Logs contain code snippets and possibly secrets | Mask secrets, retention limits, access control on logs |
| Model drift | New frameworks, folder moves, new team habits | Monitor override rate, retrain quarterly, rules as fallback |
| Alert fatigue at scale | More teams = more noise if not calibrated | Keep the High share target per team, not global |

## Operations implications

- Someone has to own the rules and the model. During the pilot that's me. At scale it would sit with a platform / developer experience team.
- Security team needs a clear channel for hard-rule hits like leaked secrets.
- Engineering managers need to agree that the tool is advisory, and that "the tool said Low" is never an excuse in a post-mortem.
