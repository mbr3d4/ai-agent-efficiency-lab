#!/usr/bin/env python3
"""
E1-R1 — Repetição Controlada do Experimento E1 (Tool Use vs Baseline)
ai-agent-efficiency-lab

Objetivo:
Validar por repetição estatística (N=5) se o ganho de latência e redução de tokens
observados em E1 são comportamentos consistentes ou anomalias amostrais.
"""

import sys
import json
import time
import argparse
import statistics
import ollama

MODEL_NAME = "hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q2_K_XL"
TEST_PROMPT = "Qual é o status atual da CPU, memória e temperatura do sistema?"

MOCK_SYSTEM_STATUS = {
    "cpu": 37,
    "memory": 61,
    "temperature": 54
}

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_system_status",
            "description": "Retorna o status atual de telemetria do sistema contendo cpu (%), memory (%) e temperature (°C).",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

def format_ns_to_ms(ns):
    if ns is None:
        return 0.0
    return round(ns / 1_000_000, 2)

def evaluate_grounding(text, mock_data):
    has_cpu = str(mock_data["cpu"]) in text
    has_mem = str(mock_data["memory"]) in text
    has_temp = str(mock_data["temperature"]) in text
    return has_cpu and has_mem and has_temp

def run_single_e0():
    start = time.perf_counter()
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": TEST_PROMPT}],
        stream=False
    )
    wall_ms = (time.perf_counter() - start) * 1000
    prompt_tokens = getattr(response, "prompt_eval_count", 0) or 0
    output_tokens = getattr(response, "eval_count", 0) or 0
    eval_duration_ns = getattr(response, "eval_duration", 0) or 1
    tps = round(output_tokens / (eval_duration_ns / 1e9), 2) if eval_duration_ns else 0.0
    
    grounded = evaluate_grounding(response.message.content, MOCK_SYSTEM_STATUS)
    
    return {
        "wall_latency_ms": round(wall_ms, 1),
        "wall_latency_s": round(wall_ms / 1000, 2),
        "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens,
        "tokens_per_sec": tps,
        "tool_calls": 0,
        "grounding_success": grounded,
        "content_length_chars": len(response.message.content)
    }

def run_single_e1():
    start = time.perf_counter()
    messages = [{"role": "user", "content": TEST_PROMPT}]
    
    # Passo 1: Decisão / Tool Call
    step1_start = time.perf_counter()
    resp1 = ollama.chat(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOL_DEFINITIONS,
        stream=False
    )
    step1_ms = (time.perf_counter() - step1_start) * 1000
    
    tool_calls = resp1.message.tool_calls or []
    tool_count = len(tool_calls)
    
    # Execução da ferramenta mock
    messages.append(resp1.message)
    messages.append({
        "role": "tool",
        "content": json.dumps(MOCK_SYSTEM_STATUS)
    })
    
    # Passo 2: Síntese final
    step2_start = time.perf_counter()
    resp2 = ollama.chat(
        model=MODEL_NAME,
        messages=messages,
        stream=False
    )
    step2_ms = (time.perf_counter() - step2_start) * 1000
    total_wall_ms = (time.perf_counter() - start) * 1000
    
    p1 = getattr(resp1, "prompt_eval_count", 0) or 0
    p2 = getattr(resp2, "prompt_eval_count", 0) or 0
    o1 = getattr(resp1, "eval_count", 0) or 0
    o2 = getattr(resp2, "eval_count", 0) or 0
    
    grounded = evaluate_grounding(resp2.message.content, MOCK_SYSTEM_STATUS)
    
    return {
        "wall_latency_ms": round(total_wall_ms, 1),
        "wall_latency_s": round(total_wall_ms / 1000, 2),
        "step1_ms": round(step1_ms, 1),
        "step2_ms": round(step2_ms, 1),
        "prompt_tokens": p1 + p2,
        "output_tokens": o1 + o2,
        "tool_calls": tool_count,
        "grounding_success": grounded,
        "content_length_chars": len(resp2.message.content)
    }

def calc_stats(values):
    if not values:
        return {}
    s_values = sorted(values)
    n = len(s_values)
    mean_val = statistics.mean(s_values)
    median_val = statistics.median(s_values)
    stdev_val = statistics.stdev(s_values) if n > 1 else 0.0
    
    # Cálculo de P95 por interpolação linear contínua entre postos adjacentes: p * (n - 1)
    if n == 1:
        p95_val = s_values[0]
    else:
        idx_float = 0.95 * (n - 1)
        i = int(idx_float)
        frac = idx_float - i
        if i + 1 < n:
            p95_val = s_values[i] + frac * (s_values[i+1] - s_values[i])
        else:
            p95_val = s_values[-1]
        
    return {
        "min": round(s_values[0], 2),
        "mediana": round(median_val, 2),
        "media": round(mean_val, 2),
        "max": round(s_values[-1], 2),
        "desvio_padrao": round(stdev_val, 2),
        "p95_interpolado": round(p95_val, 2),
        "p95_metodo": "linear_interpolation_c0.95(n-1)"
    }


def main():
    parser = argparse.ArgumentParser(description="E1-R1: Repetição Controlada")
    parser.add_argument("--runs", type=int, default=5, help="Número de repetições para cada condição (default: 5)")
    args = parser.parse_args()
    
    total_runs = args.runs
    print(f"============================================================")
    print(f"INICIANDO E1-R1: REPETIÇÃO CONTROLADA (N = {total_runs})")
    print(f"Modelo: {MODEL_NAME}")
    print(f"Estratégia: Execução alternada (E0 -> E1) a cada rodada")
    print(f"============================================================")
    
    e0_runs = []
    e1_runs = []
    
    for i in range(1, total_runs + 1):
        print(f"\n>>> Rodada {i}/{total_runs} <<<")
        
        # 1. Executa E0
        print(f"  [E0 - Run {i}] Executando baseline...")
        sys.stdout.flush()
        e0_res = run_single_e0()
        e0_res["run"] = i
        e0_runs.append(e0_res)
        print(f"  [E0 - Run {i}] Concluído: {e0_res['wall_latency_s']} s | {e0_res['output_tokens']} tokens saída | Grounding: {e0_res['grounding_success']}")
        sys.stdout.flush()
        
        # Pequeno intervalo para estabilização de hardware/VRAM
        time.sleep(2)
        
        # 2. Executa E1
        print(f"  [E1 - Run {i}] Executando tool use...")
        sys.stdout.flush()
        e1_res = run_single_e1()
        e1_res["run"] = i
        e1_runs.append(e1_res)
        print(f"  [E1 - Run {i}] Concluído: {e1_res['wall_latency_s']} s | {e1_res['output_tokens']} tokens saída | Grounding: {e1_res['grounding_success']}")
        sys.stdout.flush()
        
        time.sleep(2)
        
    # Estatísticas agregadas
    e0_latencies_s = [r["wall_latency_s"] for r in e0_runs]
    e0_output_tokens = [r["output_tokens"] for r in e0_runs]
    
    e1_latencies_s = [r["wall_latency_s"] for r in e1_runs]
    e1_output_tokens = [r["output_tokens"] for r in e1_runs]
    
    stats_e0_lat = calc_stats(e0_latencies_s)
    stats_e0_tok = calc_stats(e0_output_tokens)
    
    stats_e1_lat = calc_stats(e1_latencies_s)
    stats_e1_tok = calc_stats(e1_output_tokens)
    
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": MODEL_NAME,
        "n_runs": total_runs,
        "e0": {
            "individual_runs": e0_runs,
            "latency_s_stats": stats_e0_lat,
            "output_tokens_stats": stats_e0_tok
        },
        "e1": {
            "individual_runs": e1_runs,
            "latency_s_stats": stats_e1_lat,
            "output_tokens_stats": stats_e1_tok
        }
    }
    
    with open("e1_r1_evidence.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"\n============================================================")
    print(f"TABELA CONSOLIDADA DE RESULTADOS (E1-R1)")
    print(f"============================================================")
    print(f"{'Rodada':<8} | {'E0 Lat (s)':<12} | {'E0 Tokens':<10} | {'E1 Lat (s)':<12} | {'E1 Tokens':<10}")
    print(f"---------|--------------|------------|--------------|------------")
    for i in range(total_runs):
        print(f"Run {i+1:<4} | {e0_runs[i]['wall_latency_s']:<12} | {e0_runs[i]['output_tokens']:<10} | {e1_runs[i]['wall_latency_s']:<12} | {e1_runs[i]['output_tokens']:<10}")
    print(f"---------|--------------|------------|--------------|------------")
    print(f"Mínimo   | {stats_e0_lat['min']:<12} | {stats_e0_tok['min']:<10} | {stats_e1_lat['min']:<12} | {stats_e1_tok['min']:<10}")
    print(f"Mediana  | {stats_e0_lat['mediana']:<12} | {stats_e0_tok['mediana']:<10} | {stats_e1_lat['mediana']:<12} | {stats_e1_tok['mediana']:<10}")
    print(f"Média    | {stats_e0_lat['media']:<12} | {stats_e0_tok['media']:<10} | {stats_e1_lat['media']:<12} | {stats_e1_tok['media']:<10}")
    print(f"Máximo   | {stats_e0_lat['max']:<12} | {stats_e0_tok['max']:<10} | {stats_e1_lat['max']:<12} | {stats_e1_tok['max']:<10}")
    print(f"Desv.Pad | {stats_e0_lat['desvio_padrao']:<12} | {stats_e0_tok['desvio_padrao']:<10} | {stats_e1_lat['desvio_padrao']:<12} | {stats_e1_tok['desvio_padrao']:<10}")
    print(f"P95      | {stats_e0_lat['p95_interpolado']:<12} | {stats_e0_tok['p95_interpolado']:<10} | {stats_e1_lat['p95_interpolado']:<12} | {stats_e1_tok['p95_interpolado']:<10}")
    print(f"============================================================")
    print("Evidências salvas em e1_r1_evidence.json")

if __name__ == "__main__":
    main()
