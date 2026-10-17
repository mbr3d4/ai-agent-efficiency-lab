# AI Agent Efficiency Lab 🧪

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Evidence Integrity](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg)](tests/test_evidence_integrity.py)
[![Methodology](https://img.shields.io/badge/Protocol-Popperian%20Challenger-orange.svg)](AGENT_INSTRUCTIONS.md)

An empirical AI Engineering laboratory designed to answer a central practical question:

> **How to make an AI agent significantly faster, more factual, and resource-efficient without simply swapping it for a larger model?**

This repository provides **raw evidence**, **automated test scripts**, **statistical aggregations**, and **technical reports** investigating the impact of tool protocols on LLM generation variance, tail latency (P95), and token consumption.

---

## 📑 Table of Contents
1. [Core Scientific Discovery](#-core-scientific-discovery)
2. [Experimental Roadmap](#-experimental-roadmap)
3. [Consolidated Results Matrix (N=5)](#-consolidated-results-matrix-n5)
4. [Hardware & Runtime Environment](#-hardware--runtime-environment)
5. [Repository Structure](#-repository-structure)
6. [Reproducibility & Quickstart](#-reproducibility--quickstart)
7. [Experimental Limitations & Rigor Notes](#-experimental-limitations--rigor-notes)
8. [Engineering Governance](#-engineering-governance)
9. [License](#-license)

---

## 💡 Core Scientific Discovery

Through controlled repetition ($N=5$) and a deliberate falsification attempt (**E1-C Challenger**), this laboratory uncovered a fundamental **structural dissociation** in AI agent architectures:

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

### Why does a baseline LLM (E0) exhibit chaotic tail latency?
When a user asks a real-time environment question (*"What is the current CPU, memory, and temperature of the system?"*), a generalist LLM without tools realizes it lacks direct hardware access. Under default sampling, the model frequently tries to **compensate for its inability to act** by writing encyclopedic troubleshooting manuals for Linux, macOS, and Windows. In our runs, E0 fluctuated from **20.62 s** (a short refusal) to **282.11 s** (> 4.5 minutes, generating 4,030 tokens), yielding a standard deviation of $\pm 104.10\text{ s}$.

### Why are Tool Use (E1) and Tool Failure (E1-C) predictable?
When a tool protocol is present, the LLM transitions into a structured dispatcher role:
1. **Step 1 (Decision):** Formulates the JSON function call (~4.3 s to 6.0 s).
2. **Environment Execution:** Invokes the tool (< 1 ms in mock).
3. **Step 2 (Synthesis):** Summarizes the event and closes its turn.

Even when the tool **failed and returned `null` with an error message** (E1-C), the model **did not revert** to the 4,000-token tutorial of E0. Instead, it generated ~322 tokens with a standard deviation of only $\pm 3.16\text{ s}$. **The protocol itself acts as a syntactic shock absorber.**

---

## 🔬 Experimental Roadmap

```text
E0 — Baseline
  │ (Direct prompt without tools: high variance, long tail)
  ▼
E1 — Tool Use
  │ (Controlled mock tool: 100% grounding, lower latency)
  ▼
E1-R1 — Controlled Repetition (N=5)
  │ (Statistical validation: mean, median, linear P95, std dev)
  ▼
E1-C — Popperian Challenger
  │ (Falsification: tool invoked with simulated error / null data)
  ▼
E2 — Context Engineering (Next Phase)
```

---

## 📊 Consolidated Results Matrix (N=5)

Identical prompt tested across all conditions:
> *"Qual é o status atual da CPU, memória e temperatura do sistema?"*

| Metric | E0 (Baseline Direct) | E1 (Tool with Mock Data) | E1-C (Challenger: Tool with Null Data) | Impact of Tool Protocol |
| :--- | :--- | :--- | :--- | :--- |
| **Mean Latency** | **100.13 s** | **21.11 s** | **26.91 s** | **~78% reduction in latency** |
| **Median Latency** | **69.85 s** | **19.83 s** | **25.57 s** | **Predictable response SLA** |
| **Min / Max Latency** | **20.62 s / 282.11 s** | **17.37 s / 25.54 s** | **24.87 s / 32.47 s** | **Damped dynamic range** |
| **Std. Deviation (Latency)**| **± 104.10 s** | **± 3.42 s** | **± 3.16 s** | **Elimination of long-tail chaos** |
| **P95 Latency (Linear Interp.)\*** | **241.26 s** | **25.19 s** | **31.24 s** | **Tail SLA guaranteed** |
| **Mean Output Tokens** | **1,443.4** | **273.4** | **322.0** | **~78% token reduction** |
| **Mean Input Tokens (Multi-step)**| **66.0** | **444.0** ($p_1=325, p_2=119$) | **465.0** ($p_1=325, p_2=140$) | +378 tokens tool schema overhead |
| **Mean Total Tokens** | **1,509.4** | **717.4** | **787.0** | **-52.5% net token savings** |
| **Factual Grounding Rate** | **0% (0/5)** | **100% (5/5)** | **100% (5/5)** (grounded on error) | Strict adherence to evidence |

\* *P95 calculated via continuous linear interpolation between adjacent ranks: $C = 0.95 \times (N - 1)$.*

---

## 🖥️ Hardware & Runtime Environment

Experiments were executed locally on an isolated workstation:
* **Model:** `hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q2_K_XL` (Quantization: UD-Q2_K_XL)
* **Runtime:** Ollama 0.32.1
* **Context Length:** 4096 tokens
* **Operating System:** Linux (Fedora)
* **GPU:** NVIDIA GeForce RTX 4070 SUPER 12 GB (Loaded VRAM: ~11 GB)
* **CPU / RAM:** 16 Cores / 32 GB DDR5

---

## 📁 Repository Structure

```text
ai-agent-efficiency-lab/
├── README.md                   # Project overview, discoveries & reproduction guide
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

## 🚀 Reproducibility & Quickstart

### 1. Instant Offline Verification (No GPU / Ollama needed)
You can verify the mathematical and schema integrity of every reported metric directly from the raw recorded data in < 1 second using standard Python:

```bash
git clone https://github.com/your-username/ai-agent-efficiency-lab.git
cd ai-agent-efficiency-lab
python3 tests/test_evidence_integrity.py
```

### 2. Full Live Experiment Reproduction
To run the live inferences against the local model:

#### Prerequisites
1. Install [Ollama](https://ollama.com/).
2. Pull the quantized GGUF model:
   ```bash
   ollama run hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q2_K_XL
   ```
3. Install the Python library:
   ```bash
   pip install -r requirements.txt
   ```

#### Run the Alternated 5-Round Benchmark (E1-R1)
Executes 5 alternated rounds of E0 (baseline) and E1 (tool use) with 2-second thermal stabilization intervals:
```bash
python3 e1_r1_repetition.py --runs 5
```

#### Run the Challenger Falsification Experiment (E1-C)
Executes 5 rounds injecting hardware sensor unavailability to evaluate generation containment:
```bash
python3 e1_challenger.py --runs 5
```

---

## ⚠️ Experimental Limitations & Rigor Notes

In alignment with scientific engineering principles:
1. **Sample Size ($N=5$):** $N=5$ is an exploratory sample suitable for micro-benchmarks and rapid hypothesis testing. Tail percentiles (such as P95) have broad confidence intervals with $N=5$; descriptive statistics (Min, Median, Mean, Max, Std Dev) provide the most reliable representation.
2. **Task Specificity:** The evaluation prompt specifically targets real-time environment telemetry, where a model physically cannot answer factually without an external tool. In static reasoning or purely creative tasks, tool overhead might not be compensated by token generation savings.
3. **Sampling Parameters:** Default sampling temperatures were used. Fixing `temperature=0.0` would reduce baseline variance, though observational data confirms that the structural containment of the tool protocol remains the dominant factor.

---

## 🛡️ Engineering Governance

This lab operates under strict operational guardrails (documented in [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md)):
* **Evidence before assumption:** No claims without raw JSON evidence.
* **Challenge before conclude:** Every positive result must be subjected to a Popperian Challenger test before freezing conclusions.
* **Simple before complex:** Avoid premature architectural bloat (no unneeded multi-agent frameworks, RAG, or distributed engines).
* **Multi-step Token Accounting:** Always report true total cost:
  $$\text{Total Tokens} = \sum p_i + \sum o_i$$

Every design decision and operational step is permanently logged in [`session_audit_log.json`](session_audit_log.json).

---

## 📜 License

Distributed under the [MIT License](LICENSE).
