"""
Offline Evidence and Mathematics Integrity Tests
ai-agent-efficiency-lab

This test suite validates the integrity, syntax, and mathematical precision
of all experimental evidence and reports without requiring local GPU, Ollama,
or external dependencies (uses standard library unittest, compatible with pytest).
"""

import json
import math
import statistics
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def calc_stats_linear(values):
    s = sorted(values)
    n = len(s)
    mean_val = statistics.mean(s)
    median_val = statistics.median(s)
    stdev_val = statistics.stdev(s) if n > 1 else 0.0
    
    if n == 1:
        p95_val = s[0]
    else:
        idx = 0.95 * (n - 1)
        i = int(idx)
        frac = idx - i
        if i + 1 < n:
            p95_val = s[i] + frac * (s[i+1] - s[i])
        else:
            p95_val = s[-1]
            
    return {
        "min": round(s[0], 2),
        "mediana": round(median_val, 2),
        "media": round(mean_val, 2),
        "max": round(s[-1], 2),
        "desvio_padrao": round(stdev_val, 2),
        "p95": round(p95_val, 2)
    }

class TestEvidenceIntegrity(unittest.TestCase):

    def test_01_json_files_syntax(self):
        json_files = [
            "e1_evidence.json",
            "e1_r1_evidence.json",
            "e1_c_evidence.json",
            "session_audit_log.json"
        ]
        for filename in json_files:
            path = REPO_ROOT / filename
            self.assertTrue(path.exists(), f"File {filename} does not exist")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIsInstance(data, dict), f"File {filename} root is not a dict"

    def test_02_e1_r1_metric_integrity(self):
        path = REPO_ROOT / "e1_r1_evidence.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        e0_runs = data["e0"]["individual_runs"]
        e1_runs = data["e1"]["individual_runs"]
        self.assertEqual(len(e0_runs), 5)
        self.assertEqual(len(e1_runs), 5)
        
        # E0 Latency recalculation
        e0_lat = [r["wall_latency_s"] for r in e0_runs]
        e0_lat_stats = calc_stats_linear(e0_lat)
        stored_e0_lat = data["e0"]["latency_s_stats"]
        self.assertAlmostEqual(e0_lat_stats["media"], stored_e0_lat["media"], places=2)
        self.assertAlmostEqual(e0_lat_stats["mediana"], stored_e0_lat["mediana"], places=2)
        self.assertAlmostEqual(e0_lat_stats["desvio_padrao"], stored_e0_lat["desvio_padrao"], places=2)
        self.assertAlmostEqual(e0_lat_stats["p95"], stored_e0_lat["p95_interpolado"], places=2)
        
        # E1 Latency recalculation
        e1_lat = [r["wall_latency_s"] for r in e1_runs]
        e1_lat_stats = calc_stats_linear(e1_lat)
        stored_e1_lat = data["e1"]["latency_s_stats"]
        self.assertAlmostEqual(e1_lat_stats["media"], stored_e1_lat["media"], places=2)
        self.assertAlmostEqual(e1_lat_stats["mediana"], stored_e1_lat["mediana"], places=2)
        self.assertAlmostEqual(e1_lat_stats["desvio_padrao"], stored_e1_lat["desvio_padrao"], places=2)
        self.assertAlmostEqual(e1_lat_stats["p95"], stored_e1_lat["p95_interpolado"], places=2)
        
        # Output tokens verification
        e0_tok = [r["output_tokens"] for r in e0_runs]
        e0_tok_stats = calc_stats_linear(e0_tok)
        self.assertAlmostEqual(e0_tok_stats["media"], data["e0"]["output_tokens_stats"]["media"], places=1)
        
        e1_tok = [r["output_tokens"] for r in e1_runs]
        e1_tok_stats = calc_stats_linear(e1_tok)
        self.assertAlmostEqual(e1_tok_stats["media"], data["e1"]["output_tokens_stats"]["media"], places=1)

    def test_03_e1_c_metric_integrity(self):
        path = REPO_ROOT / "e1_c_evidence.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        runs = data["individual_runs"]
        self.assertEqual(len(runs), 5)
        
        # Latency verification
        lats = [r["wall_latency_s"] for r in runs]
        lat_stats = calc_stats_linear(lats)
        stored_lat = data["statistics"]["latency_s"]
        self.assertAlmostEqual(lat_stats["media"], stored_lat["media"], places=2)
        self.assertAlmostEqual(lat_stats["desvio_padrao"], stored_lat["desvio_padrao"], places=2)
        
        # Multi-step decomposition verification
        for r in runs:
            self.assertEqual(r["input_tokens"], r["step1_input_tokens"] + r["step2_input_tokens"])
            self.assertEqual(r["output_tokens"], r["step1_output_tokens"] + r["step2_output_tokens"])
            self.assertEqual(r["total_tokens"], r["input_tokens"] + r["output_tokens"])
            self.assertFalse(r["grounding_eval"]["hallucinated_mock"])
            self.assertTrue(r["grounding_eval"]["acknowledged_failure"])

    def test_04_no_leaked_absolute_paths(self):
        reports = ["E1_REPORT.md", "E1_CHALLENGER_REPORT.md", "AGENT_INSTRUCTIONS.md"]
        for rep in reports:
            path = REPO_ROOT / rep
            if path.exists():
                content = path.read_text(encoding="utf-8")
                self.assertNotIn("file:///home/", content, f"Leaked local file:///home/ path in {rep}")

if __name__ == "__main__":
    unittest.main()
