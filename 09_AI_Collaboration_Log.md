# 09 AI Collaboration Log

## Tools used

- **Claude (through Claude Code in VS Code)**: drafting the PM documents from my Phase 1 write-up, writing the prototype code, and checking the prototype's scoring on the sample data.
- No other generative AI tools were used for the final package.

## Where AI helped

| Area | How AI helped |
|---|---|
| Structure | Mapped the assignment packet's 10 deliverables onto my Phase 1 content, so I could see what was already covered (problem, decision, stakeholders, constraints) and what was missing (economics, evaluation, prototype, roadmap gates) |
| Drafting | First drafts of the strategy, PRD-lite, UX, evaluation, economics and risk sections |
| Prototype coding | Wrote the single-page prototype: rule engine, queue, detail panel, override flow, diff parser and evaluation tab |
| Synthetic data | Drafted 24 sample MRs covering the typical cases, including ones the rules would miss |
| Checking | Ran the scoring logic outside the browser to get the real evaluation numbers, so the documents quote computed results and not guesses |
| Pilot data script | Wrote `scripts/collect_mr_history.py` to pull MR history and label problem MRs from reverts / hotfix references |
| PDFs | Generated the PDF versions in `Submission/` from the Markdown documents |
| Benchmarking | Looked at how other teams in the course structured their repositories, to match the expected format |

## Example prompts and workflow

- *"Check the assignment briefing and other teams' projects and tell me what TEAM018 needs to do."* Gave me the gap: only a Phase 1 PDF against a 10-part package.
- *"Do the entire thing, building on my Phase 1 document, and keep it plain and readable."* Produced the drafts and prototype, which I then reviewed.
- Asked for the evaluation to be computed by actually running the scoring code, so the numbers in 05 come from the prototype and not from the text.

## Where AI was weak or needed correction

- **Too-good evaluation.** Because the same tool wrote both the rules and the sample data, the first results looked better than they should. The fix was to write sample MRs the rules genuinely can't catch (blast radius, business-config changes, dependency semantics) and a false alarm, and to put a clear caveat in the prototype and in 05. Even then, the numbers are only a demonstration.
- **Author experience as a risk factor.** My own Phase 1 listed developer experience as one of the possible causes and factors. Using it as a model feature would turn the tool into a people-scoring system. It was removed and the decision is explained in 07.
- **Economics framing.** The natural pitch was "saves reviewer time". When the assumed numbers were worked through, review time roughly evens out (less on Low MRs, more on High). The business case had to be reframed as risk reduction. This is the kind of thing that sounds right in a generated draft and falls apart with a simple calculation.
- **Generic course-case links.** Case references tend to be vague. I kept them to the specific lens from the course packet (metrics, bias, drift) and how each changed a decision in this project.
- **Over-claiming the AI part.** The prototype doesn't use a trained model or a live LLM. The docs say this clearly instead of calling it "AI-powered" without qualification.

## Human corrections and decisions

These were my calls, not the AI's:
- The topic, the problem framing and the decision being supported (from my Phase 1 document).
- **Advisory only, never block or auto-approve merges.** This was already in my Phase 1 ("not to automatically approve or reject code") and I kept it as a hard requirement.
- Leaving author identity out of the model.
- The recommendation: narrow pilot, shadow mode first, with gates, not a rollout.
- Accepting a weaker but honest evaluation instead of a perfect-looking one.
- Not calling a real LLM from the prototype, because of API keys in a public repo and the code privacy question.

## Final reflection

**Where AI sped up the PM work:** turning a framing document into a full set of artifacts, and especially the prototype. Building a working, clickable demo would have taken me much longer alone.

**Where it could not replace PM reasoning:** deciding what *not* to build (blocking, author scoring), noticing that the economics didn't support the obvious pitch, and deciding how much to trust an evaluation built on my own data. These came from going back to the problem and the course ideas (error cost, human-in-the-loop, metric vs business outcome), not from the drafts.
