# Global Memory v1

Purpose:
Shared long-term memory for all Discovery AI agents.

Rules:

* Store only important discoveries, rejected hypotheses, strong evidence, and unresolved anomalies.
* Do not store normal conversations.
* Compress information aggressively.
* Prefer insights over raw data.

Memory Categories:

## Accepted Strong Knowledge

Store highly reliable knowledge.

Format:

* Claim
* Confidence
* Evidence Basis

---

## Open Problems

Store unresolved important questions.

Format:

* Problem
* Why unresolved
* Importance

---

## Rejected Hypotheses

Store ideas strongly weakened by evidence.

Format:

* Hypothesis
* Rejection Reason

---

## Promising Leads

Store ideas worth future investigation.

Format:

* Lead
* Why promising
* Next test

---

## Discovery Log

Discovery entries:

### Discovery #001

Question:
Can perpetual motion exist if thermodynamics is incomplete?

Verdict:
No current evidence supports perpetual motion.
Unknown physics may theoretically allow loopholes but no mechanism exists.

Confidence:
78/100

Reason:
Strong thermodynamic evidence, weak speculative alternatives.
