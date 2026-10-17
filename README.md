# AI Agent Efficiency Lab 🧪

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Evidence Integrity](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg)](tests/test_evidence_integrity.py)
[![Methodology](https://img.shields.io/badge/Protocol-Popperian%20Challenger-orange.svg)](AGENT_INSTRUCTIONS.md)

**Can we make an AI agent significantly faster, more factual, and resource-efficient by changing how it works, rather than simply choosing a bigger model?**

That was the central question behind this experiment.

---

## 📖 Layer 1: Understanding the Problem, Experiment, and Learning

### Why I Built This
When an AI agent is asked to solve a real-world task, it frequently exhibits three common failure modes:
1. It takes too long to respond.
2. It generates sprawling, verbose text.
3. It fails to ground its conclusions in verified facts.

When that happens, the standard industry reflex is often to **upgrade to a larger, more expensive model**. But that is not the only option — and in many production environments, it merely makes mistakes and latency more expensive.

I wanted to treat **agent instructions, context structure, and tool-interaction protocols as primary engineering variables**. Could a disciplined architecture make a local open-weights model perform with predictable latency, minimal token waste, and 100% factual grounding?

### What I Did
I designed an empirical micro-benchmark evaluating an open-source model (`Qwen3.8-27B-GGUF` running locally on an NVIDIA RTX 4070 SUPER 12 GB via Ollama) on an identical environment query:
> *"Qual é o status atual da CPU, memória e temperatura do sistema?"* (*"What is the current CPU, memory, and temperature of the system?"*)

I compared three controlled execution strategies:

* **E0 — Baseline (Direct LLM):** The model is prompted directly with no tools available. Because it lacks direct access to the host OS, it must rely solely on its pre-trained weights.
* **E1 — Tool-Assisted Execution:** The agent is equipped with a deterministic tool schema (`get_system_status`). It executes a two-step cycle: decide to call the tool $\to$ invoke mock telemetry $\to$ synthesize a factual answer.
* **E1-C — Popperian Challenger (Falsification):** A deliberate attempt to disprove our initial conclusion. *Did E1 become faster and concise only because the tool returned specific numbers (37% CPU, 61% RAM)?* To test this, the tool protocol was kept active, but the environment **injected a sensor failure** (returning `null` with an error message). The agent was forced to answer without data.

Across 5 alternated runs per condition ($N=5$), I measured wall-clock execution time, generated output tokens, total resource consumption (including multi-step prompt overhead), and factual grounding.

### What I Learned
The runs revealed a fundamental **structural dissociation** in agent architectures:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          STRUCTURAL DISSOCIATION                       │
├───────────────────────────────────┬────────────────────────────────────┤
│ FACTUAL GROUNDING (Efficacy)      │ DEPENDS ON THE DATA RETURNED       │
│                                   │ BY THE TOOL.                       │
├───────────────────────────────────┼────────────────────────────────────┤
│ LATENCY & VARIANCE (Efficiency)   │ DEPENDS ON THE PROTOCOL STRUCTURE  │
│                                   │ OF THE TOOL INTERACTION.           │
└───────────────────────────────────┴────────────────────────────────────┘
```

1. **Why E0 is chaotic:** Without tools, the generalist LLM realizes it lacks real-time data. Under default sampling, it attempts to **compensate for its inability to act** by writing encyclopedic troubleshooting tutorials for Linux, macOS, and Windows. In our runs, E0 fluctuated from **20.62 s** (a brief refusal) to **282.11 s** (> 4.5 minutes, generating 4,030 tokens), with an extreme standard deviation of $\pm 104.10\text{ s}$.
2. **Why E1 is efficient:** With a tool, the agent transitions into a structured dispatcher role: it calls the function and summarizes the result. Latency dropped by ~78% (averaging 21.11 s), output generation dropped by ~81%, and factual grounding was 100%.
3. **The Challenger Discovery (E1-C):** When the tool failed and returned `null`, **the model did NOT revert to the 4,000-token tutorial of E0**. It simply reported the sensor failure cleanly in ~322 tokens with nearly identical latency stability (26.91 s, standard deviation $\pm 3.16\text{ s}$).

**Key Takeaway:** The data provides factual truth; but **the protocol itself acts as a syntactic shock absorber**, eliminating runaway generation and taming tail latency.

### What I Cannot Yet Claim (Honest Engineering Limitations)
* **Sample Size ($N=5$):** $N=5$ is an exploratory micro-benchmark. Tail metrics like P95 have wide confidence intervals in small samples. The findings are valid as descriptive observations, not universal population statistics.
* **Task Bias:** The evaluation prompt specifically requires external host state. In tasks involving purely static reasoning or creative writing, tool overhead may not yield token savings.
* **Sampling Parameters:** Inferences used default Ollama sampling temperatures (~0.8). Setting temperature to 0.0 would reduce baseline variance, though observational data confirms that protocol containment remains the dominant factor.

### Why This Matters
As I develop my AI Engineering portfolio, I approach agent systems with the same discipline used in Site Reliability Engineering (SRE) and distributed systems:

> **Measure first. Compare controlled alternatives. Attempt to falsify (Popperian Challenger). Keep the raw evidence. Document the limitations.**

---

## 🛠️ Layer 2: The Engineering Behind the Results

### 📊 Consolidated Results Matrix (N=5)

Identical prompt tested across all conditions:
> *"Qual é o status atual da CPU, memória e temperatura do sistema?"*

| Metric | E0 (Baseline Direct) | E1 (Tool with Mock Data) | E1-C (Challenger: Tool with Null Data) | Architectural Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Mean Latency** | **100.13 s** | **21.11 s** | **26.91 s** | **~78% latency reduction** |
| **Median Latency** | **69.85 s** | **19.83 s** | **25.57 s** | **Predictable response SLA** |
| **Min / Max Latency** | **20.62 s / 282.11 s** | **17.37 s / 25.54 s** | **24.87 s / 32.47 s** | **Damped dynamic range** |
| **Std. Deviation (Latency)**| **± 104.10 s** | **± 3.42 s** | **± 3.16 s** | **Elimination of long-tail chaos** |
| **P95 Latency (Linear Interp.)\*** | **241.26 s** | **25.19 s** | **31.24 s** | **Guaranteed tail SLA** |
| **Mean Output Tokens** | **1,443.4** | **273.4** | **322.0** | **~78% token reduction** |
| **Mean Input Tokens (Multi-step)**| **66.0** | **444.0** ($p_1=325, p_2=119$) | **465.0** ($p_1=325, p_2=140$) | +378 tokens schema overhead |
| **Mean Total Tokens** | **1,509.4** | **717.4** | **787.0** | **-52.5% net token savings** |
| **Factual Grounding Rate** | **0% (0/5)** | **100% (5/5)** | **100% (5/5)** (grounded on error) | Strict adherence to evidence |

\* *P95 calculated via continuous linear interpolation between adjacent ranks: $C = 0.95 \times (N - 1)$.*

---

### 🖥️ Hardware & Runtime Environment

* **Host Hardware:** Dedicated Linux Workstation (Fedora)
* **GPU:** NVIDIA GeForce RTX 4070 SUPER 12 GB (Loaded VRAM: ~11 GB)
* **CPU / Memory:** 16 Cores / 32 GB DDR5
* **Local Inference Engine:** Ollama 0.32.1
* **Tested Model:** `hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q2_K_XL` (Quantization: UD-Q2_K_XL)
* **Context Window:** 4096 tokens

---

### 📁 Repository Structure

```text
ai-agent-efficiency-lab/
├── README.md                   # Two-layer documentation: Human story + Technical specs
├── AGENT_INSTRUCTIONS.md       # Operational rules, anti-overengineering contract
├── PARKING_LOT.md              # Scope boundary & deferred research registry
├── LICENSE                     # MIT License
├── requirements.txt            # Python dependencies (ollama, pytest)
├── .gitignore                  # Exclusion rules for bytecode and cache
│
├── e1_tool_use.py              # Script for exploratory single-run benchmark (N=1)
├── e1_evidence.json            # Raw JSON evidence for exploratory E1
├── E1_REPORT.md                # Comprehensive technical report for E1 and E1-R1
│
├── e1_r1_repetition.py         # Automation script for alternated runs (N=5)
├── e1_r1_evidence.json         # Raw JSON evidence for 5-round E0 vs E1
│
├── e1_challenger.py            # Popperian falsification test script
├── e1_c_evidence.json          # Raw JSON evidence for 5-round Challenger E1-C
├── E1_CHALLENGER_REPORT.md     # Detailed report on the Challenger findings
│
├── session_audit_log.json      # Complete chronological audit trail of agent turns
└── tests/
    └── test_evidence_integrity.py  # Zero-dependency offline verification test suite
```

---

### 🚀 Reproducibility & Quickstart

#### 1. Instant Offline Verification (< 1 second, zero dependencies)
Anyone can independently verify that every single number, average, standard deviation, and P95 reported in this repository matches the raw recorded data with 100% mathematical precision:

```bash
git clone https://github.com/mbr3d4/ai-agent-efficiency-lab.git
cd ai-agent-efficiency-lab
python3 tests/test_evidence_integrity.py
```
*(Runs standard Python `unittest`. Compatible with `pytest`. Requires no GPU or Ollama).*

#### 2. Full Live Experiment Reproduction
To execute the live LLM inferences on your own local setup:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Pull the model into Ollama
ollama run hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q2_K_XL

# 3. Run the 5-round alternated benchmark (E0 vs E1)
python3 e1_r1_repetition.py --runs 5

# 4. Run the Popperian Challenger experiment (E1-C)
python3 e1_challenger.py --runs 5
```

---

### 🛡️ Engineering Governance & Multi-Step Accounting

This laboratory follows strict operational guardrails (documented in [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md)):
* **Evidence Before Assumption:** Every claim must be backed by a raw JSON evidence file.
* **Challenge Before Conclude:** No result is frozen until subjected to a Challenger test.
* **Mandatory Multi-Step Accounting:** Never report only the last step of a tool-using agent. Total consumption must reflect all LLM round-trips:
  $$\text{Total Tokens} = \sum p_i + \sum o_i$$
* **Session Auditability:** Every engineering decision and execution turn is recorded chronologically in [`session_audit_log.json`](session_audit_log.json).

---

### 📜 License

Distributed under the [MIT License](LICENSE).
