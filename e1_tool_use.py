#!/usr/bin/env python3
"""
E1 — Tool Use Experiment
ai-agent-efficiency-lab

Pergunta experimental:
Adicionar uma ferramenta permite que o agente resolva uma tarefa de forma mais eficiente/confiável
do que apenas gerar uma resposta com o LLM?
"""

import json
import time
import ollama

MODEL_NAME = "hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q2_K_XL"
TEST_PROMPT = "Qual é o status atual da CPU, memória e temperatura do sistema?"

# Mock controlado de dados do sistema (elimina ruído de ambiente externo)
MOCK_SYSTEM_STATUS = {
    "cpu": 37,
    "memory": 61,
    "temperature": 54
}

def get_system_status():
    """Retorna dados controlados do ambiente."""
    return MOCK_SYSTEM_STATUS

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

def run_e0_baseline():
    print("=" * 60)
    print("EXECUTANDO E0 — BASELINE (Sem ferramentas)")
    print("=" * 60)
    
    start_time = time.perf_counter()
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": TEST_PROMPT}],
        stream=False
    )
    wall_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    
    result = {
        "experiment": "E0_baseline",
        "prompt": TEST_PROMPT,
        "wall_latency_ms": wall_latency_ms,
        "total_duration_ms": format_ns_to_ms(getattr(response, "total_duration", None)),
        "prompt_eval_count": getattr(response, "prompt_eval_count", None),
        "eval_count": getattr(response, "eval_count", None),
        "llm_calls": 1,
        "tool_calls": 0,
        "content": response.message.content,
        "thinking": getattr(response.message, "thinking", None)
    }
    
    print(f"Latência total: {result['wall_latency_ms']} ms")
    print(f"Prompt Tokens: {result['prompt_eval_count']} | Output Tokens: {result['eval_count']}")
    print("\nResposta do LLM:")
    print(result["content"])
    print("-" * 60)
    return result

def run_e1_tool_use():
    print("=" * 60)
    print("EXECUTANDO E1 — TOOL USE (Com get_system_status mock)")
    print("=" * 60)
    
    messages = [{"role": "user", "content": TEST_PROMPT}]
    start_time = time.perf_counter()
    
    # Chamada 1: Decisão / Tool Calling
    step1_start = time.perf_counter()
    response1 = ollama.chat(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOL_DEFINITIONS,
        stream=False
    )
    step1_latency_ms = round((time.perf_counter() - step1_start) * 1000, 2)
    
    tool_calls = response1.message.tool_calls or []
    print(f"[Passo 1] LLM respondeu em {step1_latency_ms} ms. Tool calls detectadas: {len(tool_calls)}")
    
    tool_executed = False
    tool_result_str = None
    
    if tool_calls:
        for tc in tool_calls:
            func_name = tc.function.name
            print(f"[Tool Execution] Invocando ferramenta: {func_name}")
            if func_name == "get_system_status":
                status_data = get_system_status()
                tool_result_str = json.dumps(status_data)
                tool_executed = True
                print(f"[Tool Execution] Resultado retornado: {tool_result_str}")
        
        # Adiciona a resposta do assistente ao histórico
        messages.append(response1.message)
        
        # Adiciona o resultado da ferramenta ao histórico
        messages.append({
            "role": "tool",
            "content": tool_result_str
        })
        
        # Chamada 2: Síntese final com o resultado da ferramenta
        step2_start = time.perf_counter()
        response2 = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            stream=False
        )
        step2_latency_ms = round((time.perf_counter() - step2_start) * 1000, 2)
        total_wall_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        
        prompt_tokens_total = (getattr(response1, "prompt_eval_count", 0) or 0) + (getattr(response2, "prompt_eval_count", 0) or 0)
        eval_tokens_total = (getattr(response1, "eval_count", 0) or 0) + (getattr(response2, "eval_count", 0) or 0)
        
        result = {
            "experiment": "E1_tool_use",
            "prompt": TEST_PROMPT,
            "wall_latency_ms": total_wall_latency_ms,
            "step1_latency_ms": step1_latency_ms,
            "step2_latency_ms": step2_latency_ms,
            "llm_calls": 2,
            "tool_calls": len(tool_calls),
            "tool_executed": tool_executed,
            "tool_data": MOCK_SYSTEM_STATUS,
            "prompt_eval_count_total": prompt_tokens_total,
            "eval_count_total": eval_tokens_total,
            "step1_tokens": {
                "prompt": getattr(response1, "prompt_eval_count", None),
                "eval": getattr(response1, "eval_count", None)
            },
            "step2_tokens": {
                "prompt": getattr(response2, "prompt_eval_count", None),
                "eval": getattr(response2, "eval_count", None)
            },
            "final_content": response2.message.content,
            "thinking_step1": getattr(response1.message, "thinking", None),
            "thinking_step2": getattr(response2.message, "thinking", None)
        }
    else:
        # Caso o LLM não tenha chamado a ferramenta
        total_wall_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        result = {
            "experiment": "E1_tool_use_failed_trigger",
            "prompt": TEST_PROMPT,
            "wall_latency_ms": total_wall_latency_ms,
            "llm_calls": 1,
            "tool_calls": 0,
            "tool_executed": False,
            "final_content": response1.message.content
        }
    
    print(f"Latência total E1: {result['wall_latency_ms']} ms (Passo 1: {result.get('step1_latency_ms')} ms, Passo 2: {result.get('step2_latency_ms')} ms)")
    print(f"Tokens totais E1 - Prompt: {result.get('prompt_eval_count_total')} | Output: {result.get('eval_count_total')}")
    print("\nResposta Final do Agente:")
    print(result["final_content"])
    print("-" * 60)
    return result

def evaluate_factual_accuracy(text, mock_data):
    """Verifica se os valores exatos do mock foram citados na resposta."""
    cpu_str = str(mock_data["cpu"])
    mem_str = str(mock_data["memory"])
    temp_str = str(mock_data["temperature"])
    
    has_cpu = cpu_str in text
    has_mem = mem_str in text
    has_temp = temp_str in text
    
    return {
        "has_cpu": has_cpu,
        "has_memory": has_mem,
        "has_temperature": has_temp,
        "all_correct": has_cpu and has_mem and has_temp
    }

def main():
    print("Iniciando bateria comparativa E0 vs E1...")
    
    e0_result = run_e0_baseline()
    e1_result = run_e1_tool_use()
    
    # Avaliação de acurácia factual
    e0_acc = evaluate_factual_accuracy(e0_result["content"], MOCK_SYSTEM_STATUS)
    e1_acc = evaluate_factual_accuracy(e1_result["final_content"], MOCK_SYSTEM_STATUS)
    
    comparison = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": MODEL_NAME,
        "mock_ground_truth": MOCK_SYSTEM_STATUS,
        "e0": {
            "latency_ms": e0_result["wall_latency_ms"],
            "llm_calls": e0_result["llm_calls"],
            "prompt_tokens": e0_result["prompt_eval_count"],
            "output_tokens": e0_result["eval_count"],
            "factual_grounding": e0_acc,
            "response": e0_result["content"]
        },
        "e1": {
            "latency_ms": e1_result["wall_latency_ms"],
            "step1_latency_ms": e1_result.get("step1_latency_ms"),
            "step2_latency_ms": e1_result.get("step2_latency_ms"),
            "llm_calls": e1_result["llm_calls"],
            "tool_calls": e1_result["tool_calls"],
            "prompt_tokens": e1_result.get("prompt_eval_count_total"),
            "output_tokens": e1_result.get("eval_count_total"),
            "factual_grounding": e1_acc,
            "response": e1_result["final_content"]
        }
    }
    
    # Salva resultado em JSON para evidência pura
    with open("e1_evidence.json", "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("RESUMO COMPARATIVO DE EVIDÊNCIAS")
    print("=" * 60)
    print(f"Métrica               | E0 (Baseline)       | E1 (Tool Use)")
    print(f"----------------------|---------------------|---------------------")
    print(f"Latência Total        | {comparison['e0']['latency_ms']} ms           | {comparison['e1']['latency_ms']} ms")
    print(f"Chamadas ao LLM       | {comparison['e0']['llm_calls']}                   | {comparison['e1']['llm_calls']}")
    print(f"Chamadas de Ferramenta| 0                   | {comparison['e1']['tool_calls']}")
    print(f"Tokens de Entrada     | {comparison['e0']['prompt_tokens']}                 | {comparison['e1']['prompt_tokens']}")
    print(f"Tokens de Saída       | {comparison['e0']['output_tokens']}                 | {comparison['e1']['output_tokens']}")
    print(f"Factual Grounding     | {'SUCESSO' if comparison['e0']['factual_grounding']['all_correct'] else 'FALHA (Alucinação/Recusa)'} | {'SUCESSO' if comparison['e1']['factual_grounding']['all_correct'] else 'FALHA'}")
    print("=" * 60)
    print("Evidência salva em e1_evidence.json")

if __name__ == "__main__":
    main()
