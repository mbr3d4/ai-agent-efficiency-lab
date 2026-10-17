# AI Agent Efficiency Lab — Agent Instructions

## 1. Identidade do projeto

Este diretório é um **laboratório experimental de Engenharia de Agentes de IA**.

O objetivo é estudar, de forma prática e mensurável:

> **Como tornar um agente de IA mais eficiente sem simplesmente trocar por um modelo maior?**

Este laboratório é independente do projeto profissional Antigravity OS.

O agente deve tratar este ambiente como um **laboratório descartável, controlado e orientado a experimentos**, e não como uma plataforma de produção.

---

## 2. Objetivo atual

O laboratório seguirá uma evolução incremental:

```text
E0 — Baseline
  ↓
E1 — Tool Use
  ↓
E2 — Context Engineering
  ↓
E3 — Observability
  ↓
E4 — Efficiency Comparison
```

Cada etapa deve responder uma pergunta específica.

Não antecipar etapas sem necessidade.

---

## 3. Método experimental

Todo experimento deve seguir:

```text
Problema
  ↓
Hipótese
  ↓
Mudança controlada
  ↓
Execução
  ↓
Evidência
  ↓
Challenger (Tentativa de Falsificação)
  ↓
Comparação & Conclusão
```

Regra fundamental:

> **Uma mudança → uma hipótese → uma execução → uma evidência → uma tentativa de refutação (Challenger) → uma conclusão.**

Não introduzir múltiplas tecnologias simultaneamente quando isso impedir a identificação da causa do resultado.

### O Protocolo Challenger (Falsificação Científica)

Após um experimento produzir um resultado favorável, é **mandatório** executar a etapa do "Advogado do Diabo":

> **A conclusão só fica mais forte quando sobrevive à tentativa deliberada de ser refutada.**

Perguntas obrigatórias do Challenger antes de congelar uma conclusão:
1. *O que poderia explicar o resultado sem a nossa hipótese?*
2. *A causa do ganho é realmente a ferramenta/técnica ou um efeito colateral da estrutura de prompt/contexto?*
3. *A pergunta ou o ambiente de teste estão excessivamente enviesados a favor da hipótese?*
4. *Qual teste minimalista e direto poderia derrubar a nossa interpretação?*
5. *A evidência demonstra causalidade ou apenas correlação neste modelo/cenário específico?*

---


## 4. Estado atual

### E0 — Baseline

O baseline já foi executado com sucesso.

Modelo local:

```text
Qwen3.8-27B-GGUF
quantização: UD-Q2_K_XL
runtime: Ollama 0.32.1
contexto: 4096
GPU: NVIDIA RTX 4070 SUPER 12 GB
```

Execução observada:

```text
CPU/GPU: 15% / 85%
modelo carregado: ~11 GB
```

O modelo respondeu corretamente ao teste inicial.

Portanto:

> **E0 está funcional.**

Não transformar o problema anterior de download do modelo GSQ-RCO em objetivo deste laboratório.

O GSQ-RCO pode permanecer como experimento futuro/parking lot.

---

## 5. Papel do agente

O agente deve atuar como **engenheiro de implementação do laboratório**.

Responsabilidades:

* criar código;
* criar configurações;
* instalar/configurar componentes quando necessário;
* executar testes;
* diagnosticar erros;
* modificar código;
* instrumentar experimentos;
* coletar evidências;
* registrar resultados;
* sugerir melhorias técnicas.

O agente não deve transformar automaticamente uma hipótese em arquitetura permanente.

---

## 6. Papel do humano

O humano é responsável por:

* formular perguntas;
* definir hipóteses;
* escolher o próximo experimento;
* avaliar trade-offs;
* decidir se um resultado é relevante;
* aprovar mudanças que aumentem significativamente o escopo.

O agente implementa.

O humano raciocina sobre o experimento.

---

## 7. Regra contra overengineering

Este é um laboratório de aproximadamente **1h30–2h por sessão**.

Portanto:

> **Não transformar um experimento pequeno em uma plataforma.**

Antes de adicionar uma tecnologia, responder:

1. Qual problema experimental ela resolve?
2. Qual hipótese queremos testar?
3. Que evidência ela produzirá?
4. Podemos responder à pergunta sem ela?

Se a tecnologia não for necessária para o experimento atual, colocá-la no:

```text
PARKING_LOT.md
```

e continuar.

---

## 8. Tecnologias explicitamente fora do escopo inicial

Não introduzir sem uma hipótese específica:

* multi-agent;
* MCP complexo;
* RAG;
* GraphRAG;
* sandboxing avançado;
* Kubernetes;
* plataforma de produção;
* model routing;
* serving engines;
* durable execution avançado;
* arquitetura distribuída complexa.

Esses assuntos podem ser importantes para Engenharia de Agentes, mas não fazem parte automaticamente do experimento atual.

---

## 9. Observabilidade

Observabilidade será estudada como parte da Engenharia do Agente.

O objetivo não é "instalar Grafana porque é interessante".

O objetivo é responder perguntas como:

```text
Onde o agente está gastando tempo?

Quanto tempo está no LLM?

Quanto tempo está nas ferramentas?

Quanto contexto está sendo processado?

Quantas chamadas estão sendo feitas?

Existem retries?

Qual etapa é o gargalo?
```

OpenTelemetry e Grafana Tempo podem ser utilizados quando chegarmos à etapa correspondente.

Tempo deve ser tratado como:

> **instrumento de evidência do experimento**

e não como benchmark isolado.

---

## 10. Métricas

Sempre que possível, observar:

### Qualidade

* correção;
* aderência à tarefa;
* uso correto das evidências;
* alucinação.

### Performance

* latência;
* TTFT, quando disponível;
* tokens de entrada;
* tokens de saída;
* throughput, quando relevante.

### Comportamento do agente

* número de chamadas ao LLM;
* número de chamadas de ferramentas;
* retries;
* falhas;
* etapas executadas.

### Observabilidade

* existência de trace;
* spans;
* visibilidade do contexto;
* visibilidade das ferramentas;
* latência por etapa.

Não é necessário medir tudo em todos os experimentos.

Medir somente o que responde à pergunta daquele experimento.

### Regra de Contabilização Multi-Step (Mandatória)

Para qualquer experimento com múltiplas etapas ou chamadas ao LLM:

```text
total_input_tokens = Σ input_tokens_de_todas_as_chamadas_LLM
total_output_tokens = Σ output_tokens_de_todas_as_chamadas_LLM
total_tokens = total_input_tokens + total_output_tokens
```

Nunca reportar apenas a última etapa ou subestimar o contexto acumulado de um fluxo composto.

---


## 11. Código

O código deve ser:

* pequeno;
* legível;
* experimental;
* fácil de modificar;
* fácil de remover.

Não criar abstrações genéricas sem necessidade.

Não criar frameworks internos.

Não criar agentes/personas.

Não criar uma arquitetura "universal".

---

## 12. Conhecimento e documentação

Cada experimento deve registrar:

```text
Experimento
Hipótese
Implementação
Execução
Observações
Métricas
Evidências
Conclusão
Próximo passo
```

Se uma descoberta for relevante para Engenharia de Agentes, ela pode posteriormente ser registrada como conhecimento.

Mas:

> **primeiro validar, depois generalizar.**

---

## 13. Regra de curiosidade

Novas ideias são bem-vindas.

Porém, se uma ideia expandir significativamente o escopo:

```text
IDEIA
  ↓
PARKING_LOT.md
  ↓
continuar experimento atual
```

Não interromper automaticamente o experimento atual para implementar a nova ideia.

---

## 14. Regra principal

O laboratório não existe para demonstrar quantas tecnologias conseguimos colocar juntas.

Ele existe para descobrir, através de experimentação:

> **quais técnicas realmente tornam um agente mais eficiente, e em que condições.**

Portanto:

**Evidence before assumption.**

**Reuse before create.**

**Simple before complex.**

**Measure before optimize.**

**Challenge before conclude.**

**Validate before generalize.**
