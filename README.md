# TEAM018 | MR Risk Assistant

**AI-assisted merge request risk triage, so that review effort goes where the risk is.**

| | |
|---|---|
| Course | MBA ZG583 Management of AI Products |
| Team | TEAM018 (single member) |
| Member | M Mahadev, 2025mb26043 |
| Option | C, improve a real workflow (code review) |
| Recommendation | **Pilot** with one team in shadow mode, then advisory. Do not scale until the proof gates in [03](03_PM_Artifact_Pack.md#roadmap-with-proof-gates) are met |

## The idea in short

Every MR gets roughly the same review today, but the risk varies a lot. A leaked key or an unsafe firewall rule can be a 3-line change that gets a quick approval, while a big UI refactor eats senior time. This tool reads each MR, gives a Low / Medium / High risk band with reasons, suggests who should review it, and lets the reviewer accept or override. It never blocks or approves anything on its own.

## Read in this order

| # | Document | What it covers |
|---|---|---|
| 01 | [Executive Summary](01_Executive_Summary.md) | Problem, user, concept, why AI, recommendation |
| 02 | [Product Strategy](02_Product_Strategy.md) | Vision, JTBD, alternatives, opportunity matrix, build vs buy, first wedge, course cases |
| 03 | [PM Artifact Pack](03_PM_Artifact_Pack.md) | Problem statement, PRD-lite, RICE, MVP, roadmap with gates, metrics, how artifacts change for AI |
| 04 | [UX, Workflow and Trust](04_UX_Workflow_Trust.md) | Reviewer journey, screens, explainability, uncertainty, human-in-the-loop |
| 05 | [Data, Model and Evaluation](05_Data_Model_Evaluation.md) | AI tasks, data, labels, baseline, model choice, prototype results, pilot thresholds |
| 06 | [Business, Economics and Scaling](06_Business_Economics_Scaling.md) | Value logic, costs, unit economics, scaling risks |
| 07 | [Ethics, Governance and Risk](07_Ethics_Governance_Risk.md) | Bias, privacy, hallucination, misuse, controls, launch blockers |
| 08 | [Prototype / MVP](08_Prototype_MVP.md) | How to run, demo script, what it proves and what it doesn't |
| 09 | [AI Collaboration Log](09_AI_Collaboration_Log.md) | How AI was used, where it was wrong, what I decided |
| 10 | [Individual Contribution](10_Individual_Contribution.md) | Single-member team, roles covered |

Phase 1 problem framing (submitted earlier): [AI-Powered Merge Request Risk and Code Review Decision Support System.pdf](AI-Powered%20Merge%20Request%20Risk%20and%20Code%20Review%20Decision%20Support%20System.pdf)

## Prototype

Open [`prototype/index.html`](prototype/index.html) in a browser. It works offline, and all MRs in it are synthetic.

On 24 sample MRs, the "review big MRs carefully" rule caught 1 of 11 problem MRs. The prototype caught 8 of 11 with one false alarm. Since I wrote both the rules and the samples, treat this as a demo of the mechanism, not proof of accuracy. Details and the three misses are in [05](05_Data_Model_Evaluation.md#prototype-evaluation-synthetic-data).

## Mapping to the packet's submission structure

| Packet item | Where it is |
|---|---|
| 01_Executive_Summary | [01_Executive_Summary.md](01_Executive_Summary.md) |
| 02_Final_Report | Documents 01-08 together |
| 03_Presentation_Deck | [Appendix/Presentation_Outline.md](Appendix/Presentation_Outline.md) |
| 04_Prototype_Readme_or_Link | [08_Prototype_MVP.md](08_Prototype_MVP.md) |
| 05_AI_Collaboration_Log | [09_AI_Collaboration_Log.md](09_AI_Collaboration_Log.md) |
| 06_Individual_Contribution_Statement | [10_Individual_Contribution.md](10_Individual_Contribution.md) |
| Appendix: PRD, wireframes, metrics, roadmap, risk | Inside 03, 04, 05 and 07 |
