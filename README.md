# FRONTIER: Decision-Directed Probes and Representation Revision for Frozen Coding Agents

Companion artifact for the paper *Beyond Retrieval: Learning the Applicability Boundaries of Agent Memory* (Kaggle Gemma 4 Developer Agent Paper track).

Author: Gael IRAMBONA

## What this is

A theoretical architecture and an exactly enumerated finite example. The paper proposes treating the applicability of a stored correction as an unresolved decision problem: the agent keeps competing applicability hypotheses and, before reusing a memory, either finds an action that is optimal under every retained hypothesis or selects a probe intended to reduce uncertainty about the next decision.

## What this is not

- No Gemma run, software-issue benchmark, or competition-harness integration is reported.
- The four hypotheses, the probe outputs, the uniform prior, and the correct actions are constructed by hand. The results are exact counts for that constructed example, not measured gains on coding tasks.
- The architecture, the representation-expansion policy, and the proposed Gemma study are described in the paper but not implemented here.
- Choosing experiments for a downstream decision is classical Bayesian decision theory. The paper does not claim a new information principle, and it states that a comprehensive novelty audit remains necessary.

## Files

| File | Content |
|---|---|
| `FRONTIER_Paper_Track.pdf` | The paper |
| `frontier_finite.py` | Script that enumerates the finite example and checks its assertions |
| `finite_results.json` | Output of the script (query statistics, policy results, misspecification case, verification summary) |
| `finite_trace.csv` | Per-case trace of the three policies |

## Reproduce

Python 3 with the standard library only. No LLM, dataset, or external package is used.

```
python3 frontier_finite.py --output frontier_results
```

The script writes `finite_results.json` and `finite_trace.csv` into the output folder and prints the results. The copies in this repository are the outputs of that run.

## Result of the finite example

Four equally likely hypotheses, two unit-cost probes (`signature`, `boundary`), one-probe budget.

| Probe | Information gain (bits) | Expected residual Bayes risk | Decision gain |
|---|---|---|---|
| signature | 1.0 | 0.25 | 0.0 |
| boundary | 0.8113 | 0.0 | 0.25 |

| Policy | Correct decisions | Probes per case |
|---|---|---|
| Passive majority action | 3/4 | 0 |
| Entropy-greedy, one probe | 3/4 | 1 |
| Decision-directed, one probe | 4/4 | 1 |

The example shows that information gain and decision value can differ. It does not show that entropy-based investigation is generally inferior.

**Out-of-class case.** An extra hypothesis `h4`, absent from the controller's initial set, gives the same probe outputs as `h2` but requires the other action. The decision-directed policy then conditionally authorizes the wrong action. A later independent action check contradicts every retained hypothesis, which puts the controller in the frame-failure state. No automatic recovery is claimed.

**Verification.** The script asserts the values above and checks the common-action property on all 15 nonempty subsets of the hypothesis set.

## Disclosure

The manuscript and this artifact were prepared with AI assistance. No institutional laboratory, external certification, completed Gemma evaluation, or exhaustive novelty guarantee is implied.
