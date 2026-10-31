# 07 Ethics, Governance and Risk Note

## Main risks

1. **False sense of safety.** A "Low" label makes reviewers relax, and a risky MR goes through *because* the tool rated it low. This is the most serious risk. It's worse than not having the tool.
2. **Alert fatigue.** Too many High flags, and people stop reading them. Then the tool adds noise and nothing else.
3. **Scoring people instead of changes.** If author history is used, or if scores are visible in a way managers start using in performance reviews, it becomes a surveillance tool.
4. **Code confidentiality.** Sending diffs to an external LLM may break company policy or customer contracts. Diffs sometimes contain secrets or customer data.
5. **Hallucinated explanations.** The LLM states a reason that isn't in the diff ("this changes the password hashing") and the reviewer trusts it.
6. **Gaming.** Developers learn the rules and split or rename things to avoid being flagged.

## Bias

- **Author-based bias.** Junior or new developers statistically have more reverted MRs, partly because they get the harder onboarding tasks or less context. A model that learns from author history would flag them more, regardless of the actual change. I removed author identity, seniority and team from the features entirely. The score is about the change, not the person.
- **Folder / team bias.** Teams working on legacy or critical systems will always score higher. That is correct for review routing, but it must not be read as "this team writes worse code". Dashboards (later) should show risk by *area*, not rank teams.
- **Label bias.** Problems are linked back to MRs more often in some teams than others (better incident discipline). The model may learn "team X causes incidents" when actually team X just records them better. Check label coverage per team before training.

## Privacy

- Default: the scoring and the scanners run inside our own CI. No code leaves.
- LLM explanation: only if approved by security. Otherwise use a self-hosted model, or send only the signal summary (file names, signal labels), not the diff.
- Secrets found are **masked** in all logs and UI. Only the file and line are shown.
- Decision logs have a retention limit and access is restricted to the pilot team and security.

## Hallucination / unsafe output

- The LLM never produces the score. It only explains signals that the rules / model already found.
- The prompt passes those signals in and says to explain only them, and to quote file paths exactly.
- Spot check 30 explanations a week in the pilot. If more than 20% have an unsupported claim, turn the LLM text off and fall back to template text (what the prototype does today).

## Misuse risk

| Misuse | Control |
|---|---|
| Managers use scores to judge developers | Scores are per MR only. No per-person aggregation is built. Written policy that scores are not for performance reviews |
| "The tool said Low" used as an excuse after an incident | Advisory only. Reviewer remains accountable, stated in the team's review guidelines |
| Gaming the rules | Rules are not secret, but the learned model and hard rules (secrets etc.) are hard to dodge. Watch for unusual MR splitting patterns |
| Using it to auto-merge Low MRs | Explicitly out of scope. Would need a separate decision with much stronger evidence |

## Controls

- **Guardrails:** hard rules (secrets, privileged containers, open firewall, injection patterns) always force High; the model cannot lower them. Diffs that can't be analysed are shown as "not analysed", never Low.
- **Review process:** every band can be overridden with a reason. Overrides reviewed every two weeks.
- **Escalation path:** secret hits go to the security channel automatically. A Low-rated MR linked to an incident triggers a review of the rules.
- **Logging / auditability:** for every MR, store score, signals, rule/model version, reviewer decision and reason, and later the outcome. That way we can always answer "why did the tool say this, and who decided what".
- **Rollback:** one switch to go back to rules-only, and one to turn the whole thing off without affecting the merge process.

## Launch blockers

I would pause or not launch if any of these happen:
- A hard-rule case (e.g. a real secret) is missed in shadow mode.
- The High band flags more than ~30% of the queue and can't be tuned down without losing most of the recall.
- Security does not approve the data flow for the LLM and there is no acceptable self-hosted option. In that case: launch without LLM text, rules + model only.
- Any sign that scores are being used to evaluate individual developers.
- In the advisory pilot, a serious incident comes from an MR the tool rated Low and the reviewer relied on that rating. That needs a full review before continuing.
