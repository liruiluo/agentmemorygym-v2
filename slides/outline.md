# CAMG public paper talk

Audience: ML and agent researchers. Language: English, matching the existing public project talks.
Duration: about 15 minutes, 16 slides. Source: arXiv:2609.34422v1 (28 September 2026),
as linked from the public project page. Ongoing experiments are outside this deck.

Main claim: RL on top of familiar coding-agent file operations can learn reusable
memory behavior for long-horizon tasks.

| # | Role | Action title / takeaway | Main exhibit | Source |
|---|---|---|---|---|
| 1 | Title | Coding Agent Memory Post-training | Full title, authors, JD.com, links | Paper p.1 |
| 2 | Motivation | Long tasks need state that outlives context | Context-only vs file-memory execution | Figure 1 |
| 3 | Question | Can task reward unlock the prior in file operations? | Familiar shell actions → learned strategy | Introduction |
| 4 | Environment | CAMG connects four long-horizon task worlds | Four native task vignettes | Section 4; Appendix A |
| 5 | System | One policy learns across all four environments | Shared policy, files, async queue and learner | Figure 2; Section 5 |
| 6 | Mechanism | Context changes; the working files remain | Write → mechanical reset → read | Section 5.1 |
| 7 | Learning | Task reward trains the entire memory-use chain | Response sequence → GAE/PPO | Section 5; Appendix B |
| 8 | Result | CAMG-RL reaches 54.4% average task success | Six-method chart + metrics | Table 2; Appendix C.1 |
| 9 | Result | The largest gains are in Coding and AutoResearch | Per-environment comparison | Table 2; Appendix C.1 |
| 10 | Prior | The frozen base already favors filesystem actions | Action NLL point estimates | Figure 3a; Appendix C.1 |
| 11 | Acquisition | RL turns familiar actions into complete memory chains | First- and final-quarter chain rates | Figure 3b; Appendix C.1 |
| 12 | Transfer | Trained competence transfers to external benchmarks | Selected readable Table 3 rows | Table 3 |
| 13 | Ablation | Memory-action credit and general files both matter | Four average-success bars | Figure 4 |
| 14 | Intervention | Changing saved content reduces subsequent success | Negative blank / shuffled deltas | Appendix D.3; Figure 8 |
| 15 | Case | A coding episode shows the write–read–use chain | Saved file + fresh-context verification | Figure 5; Appendix A.4.3 |
| 16 | Conclusion | Takeaways | CAMG, CAMG-RL, learned memory | Paper conclusion |

## Interpretation and speaking notes

- Slide 4 is a simplified task illustration, not a literal transcript. Shop retains earlier
  preferences; Coding retains patches and test evidence; DeepResearch retains sources;
  AutoResearch retains experiments and files.
- Slides 5–7 redraw the public framework. Native task and filesystem effects can overlap
  in one action. The common file interface is `shell_command`; the mechanical reset
  adds neither a sampled action nor an optimizer row. The paper allows free-form
  reasoning before executable actions.
- Slide 8 uses Table 2 averages: 17.4, 19.7, 17.8, 48.0, 25.3, and 54.4.
  The 6.4-point paired difference from CompactionRL has 95% CI [3.3, 9.5].
- Slide 9 uses CAMG-RL 97.1 / 26.6 / 55.5 / 38.3 and CompactionRL
  97.5 / 19.5 / 50.8 / 24.2. Coding and AutoResearch have significant paired
  improvements; DeepResearch does not separate, and Shop is near ceiling.
- Slide 10 selects two of the four plotted rendering variants and redraws the rounded
  point estimates shown in Figure 3a, without inventing error bars. Files: 1.19 / 0.08 /
  0.25 / 0.27; dedicated tools: 1.40 / 0.47 / 0.27 / 0.33. Exact filesystem values in the
  text are 1.193 / 0.076 / 0.252 / 0.272 nats per action token. Documented renaming changes
  the probe by at most 0.013. This does not identify specific pre-training data.
- Slide 11 shows measured first and final quarters only, not an interpolated curve:
  CAMG-RL 7.97% (rounded to 8.0%) → 20.9%; AgeMem 0% in both. A complete chain is a
  successful store/revision, later retrieval, and later task use. The mandatory
  continuation write is excluded. AgeMem here uses the common training protocol.
- Slide 12 selects the 4B / CAMG-RL-4B / 35B-A3B and 9B / CAMG-RL-9B / 122B-A10B
  comparisons. Other Table 3 rows remain in the paper. This supports task competence
  under distribution shift, not a memory-only causal explanation of external transfer.
- Slide 13: 54.4 full, 21.1 without memory-action actor gradients, 41.8 continuation-only
  retraining, 28.1 continuation-only restriction at evaluation. The no-gradient control
  retains rewards, returns, value targets, and critic training. Retraining and
  evaluation-only intervention are deliberately separated.
- Slide 14 forks the same post-reset state into intact, blank and shuffled conditions.
  Eligible n = Shop 128, Coding 29, DeepResearch 60, AutoResearch 23. Blank deltas:
  −29.4 / −13.8 / −4.8 / −8.3; shuffled deltas: −14.4 / −6.5 / −16.7 / −8.3.
  Equal-environment means are −14.1 and −11.5 pp. Shuffled donors are matched within
  environment and by content length. Shop has the largest blank drop; DeepResearch
  has the largest shuffled drop. The zero-at-right chart represents actual negative deltas.
- Slide 15 is a training trajectory, not held-out evidence. The saved note is shortened
  from Figure 5; line continuations only wrap the original commands. Hidden tests pass;
  return 1.00; final submission occurs at step 30 within 40.

## Design and verification

Reference: the author's 16-page CRG/SPHERE-style talk. White 16:9 canvas, short black
upper-left titles, genuine JD.com affiliation, prominent figures and sparse red emphasis.
Native diagrams, tables, and text remain editable. Result pages use a dominant chart
and a right-hand metric column. The prior probe and chain acquisition have separate
pages. No rounded prose cards, page-number chrome, or References/Appendix tail.

Render every slide; compare contact sheets and representative full-size pages against
CRG; inspect figure labels, arrows, text fit and page geometry; reconcile results with
the public paper. Replace PDF/PPTX together and verify both deployed files by hash.
Structural checks alone do not establish visual quality.
