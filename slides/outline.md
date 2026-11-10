# CAMP-II public talk

Audience: ML and agent researchers. Language: English. Fifteen slides, about 15 minutes.
Source: the paper in `assets/paper.pdf`. Numbers match Table 1, Table 2 and Appendix C.3.

Main claim: what memory distillation can teach is set by the interface both models already know.

| # | Role | Action title | Main exhibit | Source |
|---|---|---|---|---|
| 1 | Title | Coding Agent Memory Post-Training II | Title, authors, JD.com, links | Paper p.1 |
| 2 | Framing | Distillation asks two questions, not one | One prior vs two priors | Section 1 |
| 3 | Idea | The interface has to satisfy both sides | Coverage on the left, scoring on the right | Section 3; Figure 3 |
| 4 | Prior | The file interface is already familiar to both | Third of the teacher's cost; 21.6% of actions | Figure 3a,b |
| 5 | Environment | CAMG-II: five environments, one substrate | Five task rows | Section 4; Appendix A |
| 6 | Method | Distil on what the student actually writes | Sample, score, learn | Section 5; Appendix C |
| 7 | Result | 64.6% average task success | Five-method average chart | Table 1 |
| 8 | Result | The gain lands where the interface carries the most | Per-domain CAMP-II against CAMP-I | Table 1 |
| 9 | Ablation | Every variant that touches supervision loses the gain | Five-bar ablation | Figure 6 |
| 10 | Supervision | The teacher prefers the write that keeps the task | Preference by interface | Appendix D.3 |
| 11 | Content | What the note says decides the next context | Visual case study | Figure 5 |
| 12 | Stability | The result does not rest on one draw | Five seeds, 64.9 +/- 0.5 | Appendix C.3 |
| 13 | Transfer | Trained memory carries outside the gym | Terminal-Bench 2.1 and SWE-Bench Pro V2 | Table 2 |
| 14 | Theory | Why the interface decides the cost | Rare-action form of Theorem 1 | Appendix B |
| 15 | Close | What this paper establishes | Three takeaways | Conclusion |

## Notes for the speaker

- Slide 3 argues the design principle before any result. Hold the two columns apart: the student has to
  emit the action, the teacher has to score what it wrote.
- Slide 4 quotes the paper's own comparisons: the teacher's cost on files is a third of its cost on
  compaction, and memory actions are 21.6% of all actions on files against 7.8% and 5.9%.
- Slide 7 compares averages only. The per-domain row sits on slide 8, where Shop saturates at 100 and
  Visual stays bounded by the judge.
- Slide 10 uses the appendix's preference experiment. The intervals for file and compaction overlap over
  a narrow band, so the slide reports the estimate and leaves significance to the appendix.
- Slide 12 states the spread, not a confidence interval: five seeds, sample standard deviation.
- Slide 14 says plainly that the cost law is a limit. Do not present it as a universal law.
