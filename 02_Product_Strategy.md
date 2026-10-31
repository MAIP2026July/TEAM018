# 02 Product Strategy and Opportunity Framing

## Product vision

Every reviewer should know, within a few seconds of opening the queue, which changes deserve their full attention and why, so that review time goes where the risk actually is.

## JTBD

**Reviewer / tech lead**
> When I have a long list of open MRs and limited time,
> I want to quickly see which ones are risky and what exactly to look at,
> so that I can spend my review time where a mistake would hurt the most, and not miss something serious because it looked small.

**Engineering manager**
> When I am planning review capacity and who reviews what,
> I want to see where risky changes are coming in,
> so that I can pull in security or senior reviewers before an incident rather than after.

## Opportunity framing

**Why this problem matters**
- Code review is one of the most expensive recurring activities in an engineering team, and it mostly uses senior people's time.
- The most costly problems (leaked credentials, insecure config, broken migrations, payment bugs) often come from *small* changes. They do not look scary, so they get a light review.
- After an incident, the post-mortem usually finds that "the MR was approved, nobody noticed". That is a triage failure, not a skills failure.

**Why current alternatives are weak**

| Current approach | What it does well | Where it falls short |
|---|---|---|
| Review everything equally | Simple, fair | Wastes senior time on trivial MRs and spreads attention thin on risky ones |
| "Big MR = careful review" | Easy to apply | Size is a weak signal; small risky changes slip through |
| CODEOWNERS / required approvers | Routes by folder | Static. Says who must approve, not how risky the change is |
| SAST / secret scanners in CI | Very good at known patterns | Output is a long list of findings, not a review priority. Many teams ignore the noise |
| AI code review bots | Comment on code style and bugs line by line | Add more comments to every MR. They don't answer "which MRs need my attention first" |

**Why AI may help**
- The risk of an MR depends on a mix of signals, and the right weights are specific to each codebase. A model trained on our own MR history (which MRs led to reverts, hotfixes, incidents) can learn this better than hand-written rules.
- An LLM can turn the signals plus the diff into a short explanation that a reviewer can check in 20 seconds. That is what makes the score usable.

## Opportunity matrix

I considered several possible features and scored them on business value and feasibility for a first version.

| Idea | Business value | Feasibility | Priority |
|---|---|---|---|
| Risk score + band per MR with reasons | High | High | **MVP** |
| Suggested review path (security / infra / senior / tests) | High | High | **MVP** |
| Reviewer override with reason capture | High (trust + learning data) | High | **MVP** |
| Secret / unsafe-config detection (reuse existing scanners) | High | High | **MVP** |
| LLM explanation of the diff | Medium-High | Medium | **Pilot** |
| Learned ML model on historical MRs | High | Medium (needs labelled history) | **Pilot** |
| Manager dashboard: risk by repo / service | Medium | High | Later |
| Auto-assign the right reviewer | Medium | Medium | Later |
| Blast-radius analysis (who imports this code) | High | Low | Later |
| Automatically block high-risk merges | Low (hurts trust) | High | **Rejected** |

The last row matters. Blocking merges on a model score would be easy to build, but it moves accountability from the reviewer to the tool, and the first false block would kill trust. So I rejected it on purpose.

## Build vs buy vs partner/API

**Recommended path: reuse existing scanners + LLM via API + build the risk and routing layer ourselves.**

| Layer | Decision | Why |
|---|---|---|
| Secret and SAST detection | **Reuse** open-source scanners (gitleaks / semgrep type tools) already common in CI | Mature, cheap, well understood. No reason to rebuild |
| Explanation text | **API** to a hosted LLM (or a self-hosted model if code cannot leave the company) | Learning speed matters more than owning a model at this stage |
| Risk score, routing, override capture | **Build** | This is the part that is specific to our codebase and our process. It is the "judgment layer" and is the actual product |
| Git platform integration | **Use platform APIs / webhooks** (GitLab / GitHub) | Show the result inside the MR where reviewers already work |

**Main trade-offs**
- An LLM API means code leaves our network. For many companies that is not acceptable. Fallback: self-hosted model, or only send the signal summary and file names, not the full diff.
- Building the scoring layer ourselves means we need labelled history. If we don't have it, the rules version (what the prototype runs) is still useful as a v1.

## First wedge

Start narrow:
- **one team, 2-3 backend repositories** that have a mix of auth, payments, data and infra code,
- **only triage**, no auto-comments, no blocking,
- **shadow mode first** (score is logged, not shown) for 2 weeks, so we can compare it with what actually happened without influencing reviewers.

This is small enough to run without a big rollout, and it hits the MRs where the cost of a miss is high.

## Course case connection

- **Netflix (metrics and evaluation lens):** the lesson I took is that a model metric is only useful if it is tied to a business outcome. Here, "AUC of the risk model" means nothing on its own. What matters is whether problem MRs get the right review and whether reviewer time goes down on low-risk ones. That is why my evaluation tracks recall of problem MRs *and* share of queue flagged.
- **Bias in lending / Apple Card (ethics lens):** if the model uses author history, it starts scoring people instead of changes. Junior developers would be flagged more, which is exactly the kind of proxy unfairness discussed in class. I left author features out deliberately (see 07).
- **Instacart / Tesla (lifecycle and drift lens):** codebases change all the time. New folders, new frameworks, new team habits. A model trained on last year's MRs will drift, so the roadmap includes retraining and monitoring the override rate as an early drift signal.
