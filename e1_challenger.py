#!/usr/bin/env python3
"""
E1-C — Challenger Experiment
ai-agent-efficiency-lab

Objetivo de Falsificação:
Testar se a redução de tokens e latência observada em E1 decorreu do acesso ao dado
factual da ferramenta ou se decorre meramente da presença do schema de tool no contexto.

Condição E1-C:
- Mesmo modelo, hardware e prompt de E0 e E1.
- Mesmo schema de ferramenta (get_system_status) disponível.
- A ferramenta é invocada, porém NÃO fornece os dados (retorna erro/indisponibilidade).
- Avalia se o modelo no Passo 2 reverte à cauda longa de E0 ou se permanece contido.
"""

import sys
import json
import time
import argparse
import statistics
import ollama

MODEL_NAME = "hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q2_K_XL"
TEST_PROMPT = "Qual é o status atual da CPU, memória e temperatura do sistema?"

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

# Resposta da ferramenta que NÃO fornece os dados
CHALLENGER_TOOL_RESULT = {
    "status": "error",
    "message": "sensores de telemetria indisponíveis no momento",
    "cpu": None,
    "memory": None,
    "temperature": None
}

MOCK_SYSTEM_STATUS = {
    "cpu": 37,
    "memory": 61,
    "temperature": 54
}

def evaluate_grounding(text):
    # Verifica se o modelo alucinou os números do mock de E1
    has_cpu = str(MOCK_SYSTEM_STATUS["cpu"]) in text
    has_mem = str(MOCK_SYSTEM_STATUS["memory"]) in text
    has_temp = str(MOCK_SYSTEM_STATUS["temperature"]) in text
    hallucinated_mock = has_cpu or has_mem or has_temp
    
    # Verifica se o modelo reconheceu a indisponibilidade dos dados
    acknowledged_failure = any(w in text.lower() for w in ["indispon", "erro", "não foi possível", "falha", "não consigo"])
    
    return {
        "hallucinated_mock": hallucinated_mock,
        "acknowledged_failure": acknowledged_failure
    }

def run_single_e1_c():
    start = time.perf_counter()
    messages = [{"role": "user", "content": TEST_PROMPT}]
    
    # Passo 1: Decisão / Tool Call com Schema Ativo
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
    
    # Tool Execution: Retorna erro / sem dados
    messages.append(resp1.message)
    messages.append({
        "role": "tool",
        "content": json.dumps(CHALLENGER_TOOL_RESULT)
    })
    
    # Passo 2: Síntese pelo LLM sem acesso aos dados factuais
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
    
    grounding_eval = evaluate_grounding(resp2.message.content)
    
    return {
        "wall_latency_ms": round(total_wall_ms, 1),
        "wall_latency_s": round(total_wall_ms / 1000, 2),
        "step1_ms": round(step1_ms, 1),
        "step2_ms": round(step2_ms, 1),
        "step1_input_tokens": p1,
        "step1_output_tokens": o1,
        "step2_input_tokens": p2,
        "step2_output_tokens": o2,
        "input_tokens": p1 + p2,
        "output_tokens": o1 + o2,
        "total_tokens": (p1 + p2) + (o1 + o2),
        "tool_calls": tool_count,
        "grounding_eval": grounding_eval,
        "response_content": resp2.message.content,
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
    
    # Cálculo de P95 por interpolação linear contínua
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
    parser = argparse.ArgumentParser(description="E1-C: Challenger Experiment")
    parser.add_argument("--runs", type=int, default=5, help="Número de repetições para E1-C (default: 5)")
    args = parser.parse_args()
    
    total_runs = args.runs
    print(f"============================================================")
    print(f"INICIANDO E1-C: EXPERIMENTO CHALLENGER (N = {total_runs})")
    print(f"Modelo: {MODEL_NAME}")
    print(f"Condição: Schema presente, tool executada, mas DADOS INDISPONÍVEIS")
    print(f"============================================================")
    
    runs_data = []
    
    for i in range(1, total_runs + 1):
        print(f"\n>>> Rodada Challenger {i}/{total_runs} <<<")
        sys.stdout.flush()
        
        run_res = run_single_e1_c()
        run_res["run"] = i
        runs_data.append(run_res)
        
        print(f"  [E1-C Run {i}] Concluído:")
        print(f"    Latência Total: {run_res['wall_latency_s']} s (Passo 1: {run_res['step1_ms']} ms, Passo 2: {run_res['step2_ms']} ms)")
        print(f"    Tokens: Input={run_res['input_tokens']} (p1={run_res['step1_input_tokens']}, p2={run_res['step2_input_tokens']}) | Output={run_res['output_tokens']} (o1={run_res['step1_output_tokens']}, o2={run_res['step2_output_tokens']}) | Total={run_res['total_tokens']}")
        print(f"    Reconheceu indisponibilidade: {run_res['grounding_eval']['acknowledged_failure']}")
        print(f"    Trecho da resposta: {run_res['response_content'][:150].replace(chr(10), ' ')}...")
        sys.stdout.flush()
        
        time.sleep(2)
        
    latencies = [r["wall_latency_s"] for r in runs_data]
    inputs = [r["input_tokens"] for r in runs_data]
    outputs = [r["output_tokens"] for r in runs_data]
    totals = [r["total_tokens"] for r in runs_data]
    
    stats_lat = calc_stats(latencies)
    stats_in = calc_stats(inputs)
    stats_out = calc_stats(outputs)
    stats_tot = calc_stats(totals)
    
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "experiment": "E1-C_Challenger",
        "model": MODEL_NAME,
        "n_runs": total_runs,
        "individual_runs": runs_data,
        "statistics": {
            "latency_s": stats_lat,
            "input_tokens": stats_in,
            "output_tokens": stats_out,
            "total_tokens": stats_tot
        }
    }
    
    with open("e1_c_evidence.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"\n============================================================")
    print(f"TABELA CONSOLIDADA DE RESULTADOS (E1-C)")
    print(f"============================================================")
    print(f"{'Rodada':<8} | {'Latência (s)':<14} | {'Input Tok':<10} | {'Output Tok':<10} | {'Total Tok':<10}")
    print(f"---------|----------------|------------|------------|------------")
    for i, r in enumerate(runs_data):
        print(f"Run {i+1:<4} | {r['wall_latency_s']:<14} | {r['input_tokens']:<10} | {r['output_tokens']:<10} | {r['total_tokens']:<10}")
    print(f"---------|----------------|------------|------------|------------")
    print(f"Mínimo   | {stats_lat['min']:<14} | {stats_in['min']:<10} | {stats_out['min']:<10} | {stats_tot['min']:<10}")
    print(f"Mediana  | {stats_lat['mediana']:<14} | {stats_in['mediana']:<10} | {stats_out['mediana']:<10} | {stats_tot['mediana']:<10}")
    print(f"Média    | {stats_lat['media']:<14} | {stats_in['media']:<10} | {stats_out['media']:<10} | {stats_tot['media']:<10}")
    print(f"Máximo   | {stats_lat['max']:<14} | {stats_in['max']:<10} | {stats_out['max']:<10} | {stats_tot['max']:<10}")
    print(f"Desv.Pad | {stats_lat['desvio_padrao']:<14} | {stats_in['desvio_padrao']:<10} | {stats_out['desvio_padrao']:<10} | {stats_tot['desvio_padrao']:<10}")
    print(f"P95      | {stats_lat['p95_interpolado']:<14} | {stats_in['p95_interpolado']:<10} | {stats_out['p95_interpolado']:<10} | {stats_tot['p95_interpolado']:<10}")
    print(f"============================================================")
    print("Evidências do Challenger salvas em e1_c_evidence.json")

if __name__ == "__main__":
    main()
