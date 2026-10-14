Discovery_AI 🔬⚡Discovery_AI is an autonomous, multi-agent scientific discovery engine designed to advance theoretical physics, gravitation, and quantum information research. It automates the full scientific research lifecycle: triaging open paradoxes, synthesizing literature across domains, generating mechanistic hypotheses, adversarial stress-testing, symbolic tensor/algebraic verification, quantitative peer review, and drafting publication-ready LaTeX preprints.🌟 Key FeaturesAutonomous Orchestration (director_ai): Continuously scans notes, open paradoxes, and prior experiments to dynamically route tasks to the optimal pipeline tier (fast, creative, council, or full).Adversarial Builder–Breaker Core: Proposes hypotheses with explicit empirical refutation signatures ("Kill Conditions") and subjects them to rigorous adversarial counter-theorems and energy condition checks.Cross-Domain Isomorphism Engine (analogist_ai): Maps gravitational and spacetime roadblocks to solvable structures in quantum error correction, condensed matter analogs, and non-Hermitian systems.Symbolic Mathematical Sandbox (SymPy): Automatically extracts candidate equations, metric components, and tensor scalars to evaluate syntax, asymptotic flatness ($r \to \infty$), and energy condition regimes prior to review.Vector Novelty Filter: Prevents circular inquiry by calculating cosine distance embeddings of candidate hypotheses against memory/discoveries.md and memory/failed_hypotheses.md before allocating compute.4-Pillar Quantitative Scorecard: Enforces a strict scoring gate ($\ge 0.80$ overall threshold, no subscore $< 0.60$) covering Falsifiability, Mathematical Consistency, Novelty, and Literature Grounding.Automated LaTeX Preprint Drafter: Auto-compiles accepted discoveries into standalone, publication-quality .tex manuscripts in vault/drafts/.🏗 System Architecture & Workflow                        ┌───────────────────────────────┐
                        │     vault/ & memory/          │
                        │ (papers, notes, discoveries)  │
                        └──────────────┬────────────────┘
                                       │
                                       ▼
      ┌─────────────────────────────────────────────────────────────────┐
      │ autonomous_director.py                                          │
      │  1. Director AI triages active theoretical gaps & paradoxes     │
      │  2. Novelty Filter checks cosine distance (threshold < 0.85)    │
      │  3. Selects pipeline tier & executes runner with --topic        │
      └────────────────────────────────┬────────────────────────────────┘
                                       │
                                       ▼
      ┌─────────────────────────────────────────────────────────────────┐
      │ full_runner.py                                                  │
      │  1. Scholar AI retrieves grounded RAG context                   │
      │  2. Breaker AI audits assumptions & targets kill conditions     │
      │  3. Builder AI formulates mechanistic hypothesis                │
      │  4. Math Verifier (SymPy) tests equations & boundary limits     │
      │  5. Pattern & Reasoner extract structures & logic               │
      │  6. Judge AI evaluates 4-pillar quantitative scorecard (JSON)   │
      └────────────────────────────────┬────────────────────────────────┘
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
               [If REJECTED]                     [If ACCEPTED]
         Log to failed_hypotheses.md         1. Log to discoveries.md
         to block future loops               2. Trigger paper_drafter.py
                                                to generate publication .tex
🤖 The Agent CouncilAgentBase BrainRole & ObjectiveDirector AIbrains/director_brain.mdStrategic orchestrator; detects bottlenecks, prioritizes assumptions, routes pipelines.Scholar AIbrains/scholar_brain.mdEpistemic foundation; organizes established science, RAG retrieval, and empirical facts.Builder AIbrains/builder_brain.mdTheoretical constructor; formulates mechanisms with explicit empirical Kill Conditions.Breaker AIbrains/breaker_brain.mdAdversarial red-team; stress-tests models against conservation laws and energy conditions.Analogist AIbrains/analogist_brain.mdCross-domain theorist; discovers mathematical dualities in quantum information and condensed matter.Pattern AIbrains/pattern_brain.mdStructure extractor; detects reusable mathematical and topological patterns across cycles.Reasoner AIbrains/reasoner_brain.mdFormal logician; identifies non-sequiturs, latent contradictions, and hidden assumptions.Judge AIbrains/judge_brain.mdChief gatekeeper; scores hypotheses quantitatively across four pillars.📊 Quantitative Scoring FormulaA hypothesis must satisfy:$$\text{Total Score} = 0.35 \times \text{Falsifiability} + 0.25 \times \text{Math} + 0.25 \times \text{Novelty} + 0.15 \times \text{Grounding}$$$$\text{Pass Condition}: \quad \text{Total} \ge 0.80 \quad \land \quad \min(\text{subscores}) \ge 0.60$$📁 Repository StructureDiscovery_AI/
├── brains/                      # Agent identities, missions, and prompt directives
│   ├── analogist_brain.md
│   ├── breaker_brain.md
│   ├── builder_brain.md
│   ├── director_brain.md
│   ├── judge_brain.md
│   └── scholar_brain.md
├── memory/                      # Persistent knowledge bases & research logs
│   ├── discoveries.md           # Peer-reviewed, accepted discoveries
│   ├── failed_hypotheses.md     # Red-teamed failures (guards against duplicate errors)
│   ├── patterns.md              # Reusable theoretical templates
│   └── session_memory.md        # Real-time execution logs & triage history
├── models/                      # Ollama Modelfiles for each specialized agent
│   ├── analogist_ai/Modelfile
│   ├── breaker_ai/Modelfile
│   ├── builder_ai/Modelfile
│   ├── director_ai/Modelfile
│   └── judge_ai/Modelfile
├── rag/                         # Vector search engine for scientific literature
│   ├── db/                      # ChromaDB vector store
│   └── rag_index.py             # Paper parsing and indexing pipeline
├── runner/                      # Execution pipelines and mathematical tools
│   ├── autonomous_director.py   # Continuous autonomous research daemon
│   ├── council_runner.py        # Dialectical council pipeline for paradoxes
│   ├── creative_runner.py       # Cross-domain exploratory pipeline
│   ├── fast_runner.py           # Rapid sanity and boundary check runner
│   ├── full_runner.py           # Complete end-to-end multi-agent pipeline
│   ├── math_verifier.py         # SymPy symbolic boundary & tensor checker
│   ├── novelty_filter.py        # Vector embedding cosine distance filter
│   ├── paper_drafter.py         # Academic LaTeX preprint compiler
│   └── shared.py                # Inter-agent communication & evaluation utilities
└── vault/
    ├── drafts/                  # Compiled LaTeX manuscripts (.tex)
    ├── notes/                   # Working theoretical notes
    └── papers/                  # Source PDFs and scientific literature
🚀 Getting Started1. PrerequisitesPython 3.10+Ollama installed and runningLaTeX distribution (e.g., pdflatex or texlive) for compiling drafts (optional)2. InstallationClone the repository and install the dependencies:git clone https://github.com/BaapOfCoding699/Discovery_AI.git
cd Discovery_AI
pip install chromadb pypdf sentence-transformers ollama sympy numpy
3. Build Agent ModelsEnsure your base LLM (e.g., llama3:8b) is pulled, then register all project models:ollama pull llama3:8b

ollama create director_ai -f models/director_ai/Modelfile
ollama create builder_ai -f models/builder_ai/Modelfile
ollama create breaker_ai -f models/breaker_ai/Modelfile
ollama create judge_ai -f models/judge_ai/Modelfile
ollama create scholar_ai -f models/scholar_ai/Modelfile
ollama create analogist_ai -f models/analogist_ai/Modelfile
4. Index Literature (RAG)Add research papers (.pdf) to vault/papers/ and index them into the vector database:python rag/rag_index.py
⚡ Execution ModesFully Autonomous Discovery LoopLaunch the autonomous director to triage hypotheses, screen them through the novelty filter, execute runners, and draft manuscripts indefinitely:python -m runner.autonomous_director
Single Topic / Interactive RunEvaluate a single, specific research question through the full pipeline:python runner/full_runner.py --topic "Traversable wormhole throat stabilization via post-selected Casimir entanglement"
Generate LaTeX Preprint ManuallyRe-compile or synthesize an academic preprint from the latest verified discovery in memory:python runner/paper_drafter.py
Compiled drafts will be written directly to vault/drafts/<Sanitized_Topic_Name>.tex.🛡 LicenseThis project is open-source and intended for autonomous theoretical exploration and scientific research.
