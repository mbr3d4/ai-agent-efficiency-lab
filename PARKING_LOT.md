# Parking Lot

Ideias, modelos e tecnologias registradas para avaliação futura, sem interromper ou inflar o escopo do experimento atual.

---

## Modelos e Runtimes

* **GSQ-RCO (Quantização / Download)**
  * *Contexto*: Teste alternativo de quantização ou modelo para comparar com o baseline Qwen3.8-27B-GGUF (UD-Q2_K_XL).
  * *Critério de ativação*: Somente se houver necessidade comprovada de comparar eficiência ou comportamento de quantização em etapas posteriores (ex.: E4).

---

## Tecnologias e Arquiteturas (Fora do escopo inicial)

* **Multi-agent architectures**
* **MCP complexo**
* **RAG / GraphRAG**
* **Sandboxing avançado / Docker / Kubernetes**
* **Model routing e serving engines dedicados**
* **Durable execution avançado**
* **Sistemas de Skills prévias / Abstrações antes de repetição comprovada**

---

## Experimentos Derivados Futuros

* **E1.5 — Tool Real Python (Leitura de métricas reais do Fedora)**
  * *Contexto*: Comparar o comportamento do agente com ferramenta determinística mock versus ferramenta com I/O real do sistema operacional (leitura de `/proc`, `psutil` ou subprocessos `top`/`free`).
  * *Critério de ativação*: Executar como validação de ambiente real após os estudos centrais de contexto e observabilidade (E2/E3), evitando introduzir ruído externo durante as fases comparativas de prompt e contexto.

