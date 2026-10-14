<div align="center">

# 🔬 Discovery_AI

### *Autonomous Multi-Agent Theoretical Physics & Hypothesis Engine*

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-black?logo=ollama&logoColor=white)](https://ollama.com/)
[![SymPy](https://img.shields.io/badge/Verification-SymPy_CAS-green?logo=scipy&logoColor=white)](https://www.sympy.org/)
[![ChromaDB](https://img.shields.io/badge/RAG-ChromaDB-orange)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

<p align="center">
  <b>Discovery_AI</b> automates the theoretical research lifecycle from reading academic papers to adversarial red-teaming, computer algebra verification, quantitative scoring, and formal LaTeX preprint drafting.
</p>

[Architecture](#-architecture) •
[Agent Council](#-the-agent-council) •
[Google Colab](#-running-on-google-colab-free-gpu) •
[Quickstart](#-quickstart-local) •
[Execution](#-execution)

---

</div>

## 📌 Overview

Most LLM-based research frameworks default to plausible-sounding speculation without empirical grounding. **Discovery_AI** addresses this by coupling local multi-agent cognition with strict validation gates:

- **Adversarial Red-Teaming**: Hypotheses must supply an empirical **Kill Condition** tested by `breaker_ai`.
- **Symbolic Tensor & Limit Sandbox**: Uses **SymPy** to verify asymptotic flatness ($r \to \infty$) and evaluate energy density invariants before human review.
- **Vector Novelty Gating**: Cosine distance screening ($\text{similarity} < 0.85$) against verified discoveries and logged failures prevents redundant research loops.
- **Quantitative Peer-Review Scorecard**: Weighted numerical thresholds reject models that fail conservation bounds or lack testability.
- **Preprint Synthesis**: Accepted discoveries are compiled directly into compile-ready academic LaTeX manuscripts (`.tex`).

---

## 🏗 Architecture

```
                       ┌───────────────────────────────┐
                       │    vault/ & memory/ archives  │
                       │ (papers, notes, discoveries)  │
                       └──────────────┬────────────────┘
                                      │
                                      ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │ runner/autonomous_director.py                                   │
     │   1. Director AI triages active theoretical gaps & paradoxes    │
     │   2. Novelty Filter validates cosine distance (sim < 0.85)      │
     │   3. Selects tier & executes designated runner with --topic     │
     └────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │ runner/full_runner.py                                           │
     │   1. Scholar AI retrieves grounded RAG context from vault/      │
     │   2. Breaker AI audits assumptions & targets kill conditions    │
     │   3. Builder AI constructs mechanistic hypothesis               │
     │   4. SymPy CAS validates syntax, coordinates & asymptotic limits│
     │   5. Pattern AI & Reasoner AI audit structure and logical flow  │
     │   6. Judge AI scores 4-pillar quantitative JSON rubric          │
     └────────────────────────────────┬────────────────────────────────┘
                                      │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
              [If REJECTED]                     [If ACCEPTED]
     Logged to failed_hypotheses.md         1. Written to discoveries.md
     to block duplicate cyclic loops        2. Auto-triggers paper_drafter.py
                                               to produce publication LaTeX
```

---

## 🤖 The Agent Council

Discovery_AI divides cognition across specialized local personas running via Ollama:

| Agent | Core Persona File | Operational Mission |
| :--- | :--- | :--- |
| **Director AI** | `brains/director_brain.md` | Strategic orchestrator; detects research bottlenecks and routes execution tiers. |
| **Scholar AI** | `brains/scholar_brain.md` | Epistemic foundation; organizes verified facts and grounds arguments in RAG context. |
| **Builder AI** | `brains/builder_brain.md` | Theoretical constructor; formulates mechanisms with explicit refutation conditions. |
| **Breaker AI** | `brains/breaker_brain.md` | Adversarial red-team; stress-tests assumptions against energy and conservation bounds. |
| **Analogist AI** | `brains/analogist_brain.md` | Cross-domain theorist; maps paradoxes to quantum error-correcting codes and condensed matter. |
| **Pattern AI** | `brains/pattern_brain.md` | Structural mapper; extracts recurring mathematical, topological, and systemic invariants. |
| **Reasoner AI** | `brains/reasoner_brain.md` | Formal logician; isolates non-sequiturs, latent contradictions, and hidden assumptions. |
| **Judge AI** | `brains/judge_brain.md` | Chief scientific gatekeeper; issues quantitative scorecards and final verdict. |

---

## ⚖ Quantitative Review Rubric

A hypothesis only passes if the overall weighted threshold is met with no sub-metric failure:

$$\text{Score} = 0.35(\text{Falsifiability}) + 0.25(\text{Math}) + 0.25(\text{Novelty}) + 0.15(\text{Grounding})$$

$$\text{Verdict} = \begin{cases} \text{ACCEPTED}, & \text{if } \text{Score} \ge 0.80 \quad \land \quad \min(\text{subscores}) \ge 0.60 \\ \text{REJECTED}, & \text{otherwise} \end{cases}$$

---

## 📂 Repository Structure

```graphql
Discovery_AI/
├── brains/                     # Standardized identity & directive definitions
│   ├── analogist_brain.md      # Cross-domain dualities (QEC, topological matter)
│   ├── breaker_brain.md        # Adversarial falsification directives
│   ├── builder_brain.md        # Hypothesis generation & Kill Conditions
│   ├── director_brain.md       # Triage & runner routing logic
│   ├── judge_brain.md          # 4-pillar quantitative scorecard rubric
│   └── scholar_brain.md        # Academic grounding & RAG extraction guidelines
├── memory/                     # Persistent engine memory
│   ├── discoveries.md          # Peer-reviewed, accepted discoveries
│   ├── failed_hypotheses.md    # Red-teamed failures (guards against duplicate errors)
│   ├── patterns.md             # Reusable structural templates
│   └── session_memory.md       # Real-time execution logs & triage history
├── models/                     # Ollama Modelfiles for local agent instances
│   ├── analogist_ai/Modelfile
│   ├── breaker_ai/Modelfile
│   ├── builder_ai/Modelfile
│   ├── director_ai/Modelfile
│   └── judge_ai/Modelfile
├── rag/                        # Literature retrieval subsystem
│   ├── db/                     # ChromaDB vector store
│   └── rag_index.py            # PDF parsing, chunking, and embedding pipeline
├── runner/                     # Execution orchestration and analytical tools
│   ├── autonomous_director.py  # Top-level autonomous discovery loop
│   ├── council_runner.py       # Dialectical council pipeline for paradoxes
│   ├── creative_runner.py      # Exploratory cross-domain pipeline
│   ├── fast_runner.py          # Rapid formula check & boundary runner
│   ├── full_runner.py          # Complete multi-agent pipeline with Math & Judge gates
│   ├── math_verifier.py        # SymPy symbolic algebra & asymptotic limit engine
│   ├── novelty_filter.py       # Cosine distance embedding novelty gate
│   ├── paper_drafter.py        # Publication-ready LaTeX manuscript compiler
│   └── shared.py               # Central IPC, execution routing, and memory helpers
└── vault/
    ├── drafts/                 # Generated academic LaTeX articles (.tex)
    ├── notes/                  # Working theoretical notes and conjectures
    └── papers/                 # Source scientific preprints (PDF)
```

---

## ⚡ Running on Google Colab (Free GPU)

Run Discovery_AI autonomously with GPU acceleration (T4/V100/A100) on Google Colab:

1. **Set Runtime**: Go to **Runtime** → **Change runtime type** → select **T4 GPU** → **Save**.
2. **Execute Setup & Runner Cells**:

```python
# 1. Mount Google Drive for persistent memory & preprints
from google.colab import drive
import os
drive.mount('/content/drive')
WORKSPACE = "/content/drive/MyDrive/Discovery_AI_Workspace"
os.makedirs(WORKSPACE, exist_ok=True)
```

```bash
# 2. Clone repo and install requirements
!git clone https://github.com/BaapOfCoding699/Discovery_AI.git /content/Discovery_AI
%cd /content/Discovery_AI
!pip install -q chromadb pypdf sentence-transformers ollama sympy numpy
```

```python
# 3. Start Ollama background daemon
import subprocess, time
!curl -fsSL https://ollama.com/install.sh | sh
ollama_proc = subprocess.Popen(["ollama", "serve"])
time.sleep(5)
!ollama --version
```

```bash
# 4. Pull base model and build custom agents
!ollama pull llama3:8b

!ollama create director_ai  -f models/director_ai/Modelfile
!ollama create builder_ai   -f models/builder_ai/Modelfile
!ollama create breaker_ai   -f models/breaker_ai/Modelfile
!ollama create judge_ai     -f models/judge_ai/Modelfile
!ollama create scholar_ai   -f models/scholar_ai/Modelfile
!ollama create pattern_ai   -f models/pattern_ai/Modelfile
!ollama create analogist_ai -f models/analogist_ai/Modelfile
!ollama create reasoner_ai  -f models/reasoner_ai/Modelfile
```

```bash
# 5. Index literature vault (optional if vault/papers has PDFs)
!python rag/rag_index.py

# 6. Launch autonomous research engine
!python -m runner.autonomous_director
```

```python
# 7. Backup outputs to Google Drive
!cp -r /content/Discovery_AI/memory/* /content/drive/MyDrive/Discovery_AI_Workspace/
!cp -r /content/Discovery_AI/vault/drafts/* /content/drive/MyDrive/Discovery_AI_Workspace/ 2>/dev/null || true
print("[+] Backed up discoveries, logs, and preprints to Drive.")
```

---

## 🚀 Quickstart (Local)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/BaapOfCoding699/Discovery_AI.git
cd Discovery_AI

# Install dependencies
pip install chromadb pypdf sentence-transformers ollama sympy numpy
```

### 2. Build Ollama Agents

Ensure Ollama is running (`ollama serve`), then register the custom agent models:

```bash
# Pull foundational model
ollama pull llama3:8b

# Build agent council
ollama create director_ai  -f models/director_ai/Modelfile
ollama create builder_ai   -f models/builder_ai/Modelfile
ollama create breaker_ai   -f models/breaker_ai/Modelfile
ollama create judge_ai     -f models/judge_ai/Modelfile
ollama create scholar_ai   -f models/scholar_ai/Modelfile
ollama create pattern_ai   -f models/pattern_ai/Modelfile
ollama create analogist_ai -f models/analogist_ai/Modelfile
ollama create reasoner_ai  -f models/reasoner_ai/Modelfile
```

### 3. Ingest Scientific Literature

Drop research papers (`.pdf`) into `vault/papers/` and index the vector store:

```bash
python rag/rag_index.py
```

---

## 💻 Execution

<details open>
<summary><b>1. Autonomous Research Loop (Default)</b></summary>

Runs the autonomous director loop to triage context, check novelty, dispatch runners, and compile discoveries:

```bash
python -m runner.autonomous_director
```
</details>

<details>
<summary><b>2. Direct Single-Topic Full Pipeline</b></summary>

Run an isolated test on a dedicated theoretical conjecture:

```bash
python runner/full_runner.py --topic "Traversable wormhole stabilization via post-selected Casimir boundary states"
```
</details>

<details>
<summary><b>3. Compile Preprints from Memory</b></summary>

Manually compile a LaTeX paper for the latest discovery in `memory/discoveries.md`:

```bash
python runner/paper_drafter.py
```
Outputs compile-ready LaTeX files directly into `vault/drafts/`.
</details>

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.