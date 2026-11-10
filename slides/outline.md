# CAMP-II — teaching agents to remember through files

English research talk, 15 slides / approximately 15 minutes. Chinese speaker notes accompany the editable PPTX. Clean white academic style: large black action titles, blue evidence, sparse red for a measured loss. The website tells the same argument at reading pace.

## Story and exhibits

| # | Time | Action title | Exhibit and layout | Evidence |
|---|---|---|---|---|
| 1 | 0:30 | Coding Agent Memory Post-Training II | Typographic title + file bridging two contexts; full title, authors and affiliations | Paper identity |
| 2 | 1:00 | The context ends. The task does not. | Large task timeline: diagnose → write → context reset → read → continue | Visual example, schematic |
| 3 | 1:00 | A strong teacher still needs a usable memory interface | Two-sided bottleneck: student samples, teacher scores | Introduction; Figure 3 |
| 4 | 1:00 | Use the file operations both models already know | One shared workspace, native Bash operations, file retained across reset | Method |
| 5 | 1:15 | The student acts. The frozen teacher scores. | On-policy sampled response; same-context scoring; token signal and update | Method equations 5–6 |
| 6 | 0:50 | One policy learns across five task worlds | Five task illustrations with native tasks above one shared file-memory band | CAMG-II section |
| 7 | 1:15 | File-based OPD gives the largest average gain | All seven learned-memory baseline variants + initial 4B and CAMP-I; highlight 64.6 | Table 1 |
| 8 | 0:55 | The average improves; Visual remains a trade-off | Five-domain comparison with CAMP-I, including Visual 40.2 vs 46.5 | Table 1 |
| 9 | 1:00 | Files expose more memory actions to learning | Action share 21.6 / 7.8 / 5.9 and frozen teacher/student NLL | Figure 3 |
| 10 | 0:55 | The teacher better recognizes task-matched notes | 76.5 / 63.8 / 70.0 preference, clearly defined as matched vs foreign note | Appendix D.3 |
| 11 | 1:15 | Learning what to write carries the gain | Memory-content mask vs equal-size random mask, with interface controls | Figure 6 |
| 12 | 1:00 | The agent resumes from a plan it wrote | Full actual Visual case figure at projection scale; not a causal intervention | Figure 5 |
| 13 | 0:45 | The result repeats across five training seeds | Five native editable points; mean and sample standard deviation | Appendix C.3 |
| 14 | 1:10 | The learned policy improves on two external benchmarks | Base→CAMP-II paired bars at 4B and 9B; exact 35B-A3B reference | Table 2 |
| 15 | 0:30 | Familiar operations make better teaching channels | Three linked contributions; one final visual anchor | Conclusion |

Main claim: ordinary files are a useful interface for distilling long-horizon memory, because they give both the student and the teacher a familiar channel. This is evidence under the reported comparison, not a theorem that unfamiliar interfaces cannot work.

## Presentation rules

- Introduce the context-loss problem before the phrase “interface prior”. Explain OPD before its equation.
- CAMP-II is the method; CAMG-II is the five-environment suite. Coding refers to how memory is operated, not the semantics of all five tasks.
- A file write is sampled by the student. The frozen teacher scores that same response under the same visible context; it does not execute the task or write a replacement note.
- The training signal covers sampled task and memory tokens. Instructions and observations are not targets. The file persists; reset does not inject its contents back into context.
- Quantitative source: `data/research.json`. Main-table metric is the equal-weight mean of four success rates and Visual panel-mean judge score. Do not label every domain a binary success rate.
- 2.97× is the ratio of gains over Frozen 4B, not a ratio of final scores. Display arithmetic: (64.6−45.3)/(51.8−45.3). CAMP-I is the task-RL reference, not an OPD baseline.
- Retain the full main comparison set. Teacher preference is task-match discrimination, not proof that a highly scored note causes success. The Visual trace is an example, not an intervention.
- No theoretical detour or default references appendix in this 15-minute deck. Put additional protocol context in speaker notes. End on the takeaways, not a blank thank-you slide.

## Editability

Titles, prose, diagrams, charts, data labels and annotations are native PowerPoint elements. The actual Visual case is a frozen paper image. PDF is produced headlessly from the same native scene; it is a shareable rendition, not a claim of Microsoft PowerPoint pixel-identical export.
