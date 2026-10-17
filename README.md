# AI Agent Efficiency Lab 🧪

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Evidence Integrity](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg)](tests/test_evidence_integrity.py)
[![Methodology](https://img.shields.io/badge/Protocol-Popperian%20Challenger-orange.svg)](AGENT_INSTRUCTIONS.md)

**Can we make an AI agent faster, more consistent, and more resource-efficient by changing how it works, rather than simply choosing a bigger model?**

That was the central question behind this experiment.

---

## 📖 Layer 1: Understanding the Problem, Experiment, and Learning

### Why I Built This
AI agents can produce excessively long answers, take too long to complete a task, or fail to support their conclusions with verified evidence.

When that happens, upgrading to a larger, more expensive model is one possible solution. But it is not the only one — and in production, larger models often simply make latency, compute costs, and errors more expensive.

I wanted to investigate whether changes in the agent's instructions, context structure, and tool-interaction strategy could improve its efficiency and the quality of its results.

### What I Did
I ran a controlled empirical micro-benchmark evaluating an open-source model (`Qwen3.8-27B-GGUF` running locally on an NVIDIA RTX 4070 SUPER 12 GB via Ollama) on an identical system telemetry query:
> *"Qual é o status atual da CPU, memória e temperatura do sistema?"* (*"What is the current CPU, memory, and temperature of the system?"*)

I compared three execution strategies across 5 alternated runs each ($N=5$):

* **E0 — Baseline (Direct LLM):** The model answered directly without access to tools. Lacking access to the host operating system, it had to rely purely on internal weights.
* **E1 — Tool-Assisted Execution:** The agent was equipped with a deterministic tool schema (`get_system_status`). It executed a 2-step loop: decide to call the tool $\to$ receive mock telemetry $\to$ synthesize a factual answer.
* **E1-C — Challenger (Falsification Test):** A deliberate attempt to test alternative explanations. *Did E1 become faster and more concise simply because it received specific numbers (37% CPU, 61% RAM, 54 °C)?* To test this, the tool schema remained active, but the environment **returned an error with null data** (simulating unavailable sensors). The agent was forced to respond without telemetry.

I measured wall-clock execution time, generated output tokens, total resource consumption (including multi-step prompt overhead), and whether the agent grounded its response in evidence.

### 💡 What I Discovered
The main observation was that the way an agent approaches a task directly affects its execution time, response length, and ability to handle available evidence:

1. **Why E0 was erratic:** Without tools, the generalist LLM realized it lacked real-time system data. Under default sampling, it frequently tried to **compensate for its inability to act** by writing encyclopedic troubleshooting tutorials for Linux, macOS, and Windows. In our runs, E0 fluctuated from **20.62 s** (a brief refusal) to **282.11 s** (> 4.5 minutes, generating 4,030 tokens), with high variance ($\pm 104.10\text{ s}$).
2. **Why E1 was consistent:** With a tool, the agent assumed a structured dispatcher role: it requested the function and summarized the returned numbers. In this test, latency dropped to an average of **21.11 s** (~79% reduction), output tokens dropped by ~81%, and factual grounding was 100%.
3. **What the Challenger test (E1-C) showed:** Even when the tool **failed and returned an error message with null values**, the agent's response remained relatively short (~322 output tokens) and consistent in execution time (26.91 s, std dev $\pm 3.16\text{ s}$). It did not revert to the 4,000-token tutorials of E0.

That distinction matters: **a short response is not necessarily a factually correct response, and handling an error appropriately is not the same as obtaining accurate telemetry data.** In these runs, the tool protocol helped bound generation and keep latency predictable, while the tool data determined whether the response was factually grounded.

### What I Cannot Yet Claim (Honest Engineering Limitations)
* **Small Sample Size ($N=5$):** This was a preliminary micro-benchmark designed for a focused laboratory session. Tail percentiles (like P95) have broad confidence intervals with $N=5$. The numbers describe this specific run, not an SLA guarantee or a universal law.
* **Task Bias:** The evaluation prompt specifically targets real-time environment metrics, where an LLM physically cannot answer factually without external access. In static reasoning or purely creative tasks, tool overhead might not yield token savings.
* **Sampling Parameters:** Inferences used default Ollama sampling temperatures (~0.8). Setting temperature to 0.0 would reduce baseline variance, though observational data indicates that protocol containment remains a dominant factor.

### Why This Matters
As I develop my AI Engineering portfolio, I approach agent architectures with the same mindset I use in Site Reliability Engineering (SRE) and systems observability:

> **Measure first. Compare controlled alternatives. Attempt to falsify (Challenger). Keep the raw evidence. Document the limitations.**

This repository is a practical exploration of that mindset. The code, reports, and raw evidence files are fully accessible below for inspection and reproduction.

---

## 🛠️ Layer 2: The Engineering Behind the Results

### 📊 Consolidated Results Matrix (N=5)

Identical prompt tested across all conditions:
> *"Qual é o status atual da CPU, memória e temperatura do sistema?"*

| Metric | E0 (Baseline Direct) | E1 (Tool with Mock Data) | E1-C (Challenger: Tool with Null Data) | Observed Impact in This Test |
| :--- | :--- | :--- | :--- | :--- |
| **Mean Latency** | **100.13 s** | **21.11 s** | **26.91 s** | **~79% latency reduction in E1** |
| **Median Latency** | **69.85 s** | **19.83 s** | **25.57 s** | **Substantially faster response** |
| **Min / Max Latency** | **20.62 s / 282.11 s** | **17.37 s / 25.54 s** | **24.87 s / 32.47 s** | **Narrower dynamic range** |
| **Std. Deviation (Latency)**| **± 104.10 s** | **± 3.42 s** | **± 3.16 s** | **Lower observed variance** |
| **P95 Latency (Linear Interp.)\*** | **241.26 s** | **25.19 s** | **31.24 s** | **Damped tail latency in sample** |
| **Mean Output Tokens** | **1,443.4** | **273.4** | **322.0** | **~81% output token reduction in E1** |
| **Mean Input Tokens (Multi-step)**| **66.0** | **444.0** ($p_1=325, p_2=119$) | **465.0** ($p_1=325, p_2=140$) | +378 tokens tool schema overhead |
| **Mean Total Tokens** | **1,509.4** | **717.4** | **787.0** | **-52.5% net token savings in E1** |
| **Evidence Grounding / Outcome** | **0% (0/5)** (Refusal / ungrounded OS manual) | **100% (5/5)** (Correctly grounded on mock data) | **0% data** (Sensors offline) — **100% (5/5) graceful failure handling** | Clear separation of grounding vs error handling |

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
