# Relatório Experimental — E1: Tool Use

## 1. Experimento
* **Identificador:** E1 — Tool Use
* **Data/Hora:** 2026-09-12
* **Modelo Local:** `hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q2_K_XL` (Ollama 0.32.1, contexto 4096, GPU NVIDIA RTX 4070 SUPER 12 GB)
* **Assistente de Condução:** Gemini 3.8 Flash (High)
* **Status:** CONCLUÍDO E CONGELADO (Auditado em 2026-09-12)

---

## 2. Hipótese
> **Hipótese:** Adicionar uma ferramenta determinística controlada (`get_system_status`) permite que o agente responda com 100% de ancoragem factual (*factual grounding*), evitando alucinação ou evasão/verbosidade excessiva, com ganho líquido de eficiência em tarefas que dependem de dados do ambiente.

---

## 3. Implementação
* **Script:** [`e1_tool_use.py`](./e1_tool_use.py)
* **Ferramenta Controlada:** `get_system_status()` retornando mock determinístico:
  ```json
  {
    "cpu": 37,
    "memory": 61,
    "temperature": 54
  }
  ```
* **Caso de Teste Controlado:** Pergunta idêntica em ambos os cenários:
  > *"Qual é o status atual da CPU, memória e temperatura do sistema?"*
* **Fluxo E0 (Baseline):** Usuário → LLM → Resposta direta sem ferramentas.
* **Fluxo E1 (Tool Use):** Usuário → LLM (Passo 1: decisão) → Execução da Tool → LLM (Passo 2: síntese) → Resposta final.

---

## 4. Execução e Evidências

### Tabela Consolidada — Repetição Controlada E1-R1 (N=5 rodadas alternadas)

| Rodada | E0 Latência (s) | E0 Tokens Saída | E0 Grounding | E1 Latência (s) | E1 Tokens Saída | E1 Grounding |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Run 1** | 282,11 s (~4m42s) | 4.030 | Falha | 17,37 s | 211 | **Sucesso** |
| **Run 2** | 69,85 s (~1m10s) | 1.022 | Falha | 19,83 s | 256 | **Sucesso** |
| **Run 3** | 50,22 s (~50s) | 733 | Falha | 25,54 s | 343 | **Sucesso** |
| **Run 4** | 77,84 s (~1m18s) | 1.142 | Falha | 23,77 s | 313 | **Sucesso** |
| **Run 5** | 20,62 s (~21s) | 290 | Falha | 19,03 s | 244 | **Sucesso** |

#### Estatística Descritiva de Latência e Geração (N=5)

| Métrica | E0 Latência (s) | E0 Tokens Saída | E1 Latência (s) | E1 Tokens Saída |
| :--- | :--- | :--- | :--- | :--- |
| **Mínimo** | **20,62 s** | **290** | **17,37 s** | **211** |
| **Mediana** | **69,85 s** | **1.022** | **19,83 s** | **256** |
| **Média** | **100,13 s** | **1.443,4** | **21,11 s** | **273,4** |
| **Máximo** | **282,11 s** | **4.030** | **25,54 s** | **343** |
| **Desvio Padrão** | **± 104,10 s** | **± 1.482,7** | **± 3,42 s** | **± 53,6** |
| **P95 (Interp. Linear)\*** | **241,26 s** | **3.452,4** | **25,19 s** | **337,0** |
| **Taxa de Grounding** | **0% (0/5)** | — | **100% de grounding nas 5 execuções (ancoragem no retorno da ferramenta)** | — |

> \***Nota metodológica sobre P95 com N=5:** Em amostras pequenas ($N=5$), percentis de cauda como P95 são sensíveis ao método de cálculo. O valor de `77,84 s` relatado anteriormente decorreu de um truncamento de índice inteiro no script (`int(0.95 * 4) = 3`, selecionando o 4º elemento ordenado e ignorando a cauda). Com interpolação linear contínua padrão ($C = 0.95 \times (N-1)$), o P95 de E0 situa-se em `241,26 s` (ou `282,11 s` por posto mais próximo). Para $N=5$, **Mínimo, Mediana, Média e Máximo** fornecem uma representação descritiva muito mais íntegra.

---

### Auditoria da Decomposição Multi-Step de Tokens (E1)

Em cumprimento à regra mandatória multi-step, auditamos individualmente as duas chamadas ao LLM em E1:

* **Chamada 1 (Decisão / Emissão de Tool Call):**
  * `prompt_eval_count` ($p_1$): **325 tokens** (prompt do usuário + schema JSON da ferramenta + formatação de template).
  * `eval_count` ($o_1$): **~50 a 55 tokens** (raciocínio interno e estrutura do `ToolCall`).
* **Chamada 2 (Síntese da Resposta Ancorada):**
  * `prompt_eval_count` ($p_2$): **119 tokens** (delta do histórico contendo a resposta da ferramenta).
  * `eval_count` ($o_2$): **~190 a 280 tokens** (geração da resposta em markdown).
* **Totalização Comprovada por Rodada:**
  $$\text{total\_input\_tokens} = p_1 + p_2 = 325 + 119 = \mathbf{444\text{ tokens}}$$
  $$\text{total\_output\_tokens} = o_1 + o_2 = \mathbf{273,4\text{ tokens (média)}}$$
  $$\text{total\_tokens} = \text{total\_input} + \text{total\_output} = \mathbf{717,4\text{ tokens (média)}}$$

---

### Consumo Total de Recursos da LLM (Entrada, Saída e Chamadas)

| Dimensão de Consumo | E0 (Baseline) | E1 (Tool Use) | Delta / Impacto de E1 |
| :--- | :--- | :--- | :--- |
| **Tokens de Entrada (Prompt)** | **66** (constante) | **444** ($325 + 119$, constante) | **+378 tokens (+572%)** de overhead de schema/contexto |
| **Tokens de Saída (Média)** | **1.443,4** | **273,4** ($o_1 + o_2$) | **-1.170,0 tokens (-81,1%)** de redução de geração |
| **Tokens de Saída (Mediana)** | **1.022,0** | **256,0** | **-766,0 tokens (-75,0%)** |
| **Tokens Totais (Média)** | **1.509,4** | **717,4** | **-792,0 tokens (-52,5%)** de economia líquida total |
| **Tokens Totais (Mediana)** | **1.088,0** | **700,0** | **-388,0 tokens (-35,7%)** |
| **Tokens Totais (Pior caso E0)** | **4.096,0** (Run 1) | **655,0** (Run 1) | **-3.441,0 tokens (-84,0%)** |
| **Tokens Totais (Melhor caso E0)**| **356,0** (Run 5) | **688,0** (Run 5) | **+332,0 tokens (+93,3%)** (overhead de tool em recusa curta) |
| **Chamadas ao LLM** | **1** | **2** (Decisão + Síntese) | +1 chamada |
| **Chamadas de Ferramenta** | **0** | **1** (`get_system_status`) | +1 execução |

* Arquivo de evidências brutas: [`e1_r1_evidence.json`](./e1_r1_evidence.json)
* Script de repetição: [`e1_r1_repetition.py`](./e1_r1_repetition.py)

---

## 5. Observações Comportamentais

1. **E0 (Baseline) — Alta Dispersão e Resposta Não Ancorada:**
   * O baseline exibiu dispersão acentuada de comportamento: oscilou de **20,62 s** (quando realizou uma recusa direta de 290 tokens) a **282,11 s** (quando produziu um manual técnico exaustivo de 4.030 tokens para múltiplos sistemas operacionais).
   * A amplitude de latência em E0 foi de **261,49 s** (> 4 minutos e 20 segundos) entre a menor e a maior execução, com desvio padrão de **±104,10 s**.
   * Em nenhuma das 5 execuções (0/5) forneceu os dados factuais solicitados.

2. **E1 (Tool Use) — Baixa Dispersão e Resposta Orientada pelo Dado:**
   * Neste experimento, E1 apresentou variabilidade de latência e de volume de tokens muito menor que E0.
   * A latência situou-se entre **17,37 s** (mínimo) e **25,54 s** (máximo), com amplitude de apenas **8,17 s** e desvio padrão de **±3,42 s**.
   * A decomposição do tempo de inferência manteve-se estreita:
     * **Passo 1 (Decisão de invocar a tool):** 4,3 s a 6,0 s.
     * **Execução da ferramenta determinística:** < 1 ms.
     * **Passo 2 (Síntese da resposta):** 11,3 s a 20,8 s.
   * Em 100% das rodadas (5/5), o modelo utilizou a ferramenta correta e ancorou a resposta estritamente nos valores retornados.

---

## 6. Conclusão Descritiva (N=5)

> **Neste cenário controlado e dependente de dados externos, o uso da ferramenta garantiu 100% de ancoragem factual e E1 apresentou variabilidade de latência e de geração de tokens substancialmente menor que E0.**

1. **Análise de Trade-off de Consumo (Cenários Observados):**
   * **Na média e na mediana (Cenário A dominante):** E1 gerou **menos tokens de saída**, consumiu **menos tokens totais** (-52,5% na média) e exibiu **menor latência média** (-78,9%), pois a economia de geração compensou com folga o overhead de contexto.
   * **No cenário de recusa concisa de E0 (Run 5 — Cenário C):** Quando o baseline optou por uma recusa curta (290 tokens de saída / 356 tokens totais), E1 consumiu mais tokens totais (688 tokens) para entregar uma latência similar (~19 s vs ~20 s). Contudo, esse overhead de tokens converteu-se em entrega factual correta (100% de grounding contra 0% de factualidade do baseline).

2. **Comportamento Sistêmico:**
   * Nas execuções observadas, o modelo sem ferramenta frequentemente compensou a ausência de dados empíricos com explicações e procedimentos teóricos, produzindo maior dispersão de latência e geração.
   * Com ferramenta, a disponibilidade imediata do fato restringe o espaço de geração do modelo a uma síntese direta, resultando em menor dispersão operacional.

---

## 7. Próximo Passo
Com E1 formalmente concluído e congelado sob repetição controlada ($N=5$) e consumo integralmente caracterizado:
* **E1.5 (Parking Lot):** Avaliação de ferramenta real Python lendo métricas reais do sistema operacional (Fedora).
* **E2 — Context Engineering:** Formular a hipótese experimental sobre o impacto da estrutura e volume de contexto (tamanho do schema da ferramenta, clareza das descrições e inclusão de histórico) na eficiência, latência e precisão da chamada da LLM.




