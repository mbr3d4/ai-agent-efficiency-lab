# Relatório Challenger — E1-C: Falsificação de Tool Use

## 1. Experimento e Protocolo
* **Identificador:** E1-C — Challenger (Tentativa de Falsificação Popperiana)
* **Data/Hora:** 2026-09-12
* **Modelo Local:** `hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q2_K_XL` (Ollama 0.32.1, RTX 4070 SUPER 12 GB)
* **Assistente de Condução:** Gemini 3.8 Flash (High)
* **Status de E1:** Preservado e congelado intacto.

---

## 2. Hipótese a Ser Atacada (do E1)
> *"A redução de latência, o amortecimento de variância e a concisão de tokens observados em E1 foram causados pelo acesso ao dado factual retornado pela ferramenta."*

### A Pergunta Central do Challenger:
> **"O ganho de eficiência (latência e tokens) observado em E1 pode ser explicado sem a entrega dos dados pela ferramenta?"**

---

## 3. Desenho Experimental Controlado
* **Constantes:** Mesmo hardware, mesmo modelo local, mesmo prompt exato:
  > *"Qual é o status atual da CPU, memória e temperatura do sistema?"*
* **Variável Isolada:** 
  * O schema da ferramenta `get_system_status` está ativo (idêntico a E1).
  * O modelo decide invocar a ferramenta no Passo 1 (idêntico a E1).
  * **Intervenção Challenger:** O ambiente **recusa/falha na entrega dos dados**, retornando:
    ```json
    {
      "status": "error",
      "message": "sensores de telemetria indisponíveis no momento",
      "cpu": null,
      "memory": null,
      "temperature": null
    }
    ```
  * O modelo no Passo 2 é forçado a responder **sem dispor dos dados de telemetria**.

---

## 4. Evidências Empíricas e Comparação Tridimensional (N=5)

### Tabela Comparativa: E0 (Baseline) vs E1 (Tool com Dados) vs E1-C (Tool com Falha de Dados)

| Métrica Descritiva | E0 (Baseline Sem Tool) | E1 (Tool com Dados Mock) | E1-C (Challenger: Tool Sem Dados) | Comparação E1 vs E1-C |
| :--- | :--- | :--- | :--- | :--- |
| **Latência Média** | **100,13 s** | **21,11 s** | **26,91 s** | Apenas +5,8 s de diferença |
| **Latência Mediana** | **69,85 s** | **19,83 s** | **25,57 s** | Apenas +5,7 s de diferença |
| **Latência Mín / Máx** | **20,62 s / 282,11 s** | **17,37 s / 25,54 s** | **24,87 s / 32,47 s** | Faixa de operação similar |
| **Desvio Padrão Latência**| **± 104,10 s** | **± 3,42 s** | **± 3,16 s** | **Idêntica estabilidade operacional** |
| **Tokens Saída (Média)** | **1.443,4** | **273,4** | **322,0** | Quase idêntico (-77,7% vs E0) |
| **Tokens Saída (Mediana)**| **1.022,0** | **256,0** | **312,0** | Quase idêntico (-69,5% vs E0) |
| **Tokens Entrada (Média)**| **66,0** | **444,0** ($p_1+p_2$) | **465,0** ($p_1=325, p_2=140$) | Overhead de contexto preservado |
| **Tokens Totais (Média)** | **1.509,4** | **717,4** | **787,0** | -47,9% vs E0 |
| **Resultado / Fundamentação** | **0% (0/5)** (Recusa / manual não ancorado) | **100% (5/5)** (Ancoragem factual nos números) | **0% dados** (Sensores offline) — **100% (5/5) tratamento adequado da falha** | Separação clara entre dado factual e tratamento de erro |

* Arquivo de dados brutos: [`e1_c_evidence.json`](./e1_c_evidence.json)
* Script utilizado: [`e1_challenger.py`](./e1_challenger.py)

---

## 5. Resposta Explícita à Pergunta do Challenger

> **"O resultado de E1 pode ser explicado sem a execução bem-sucedida da ferramenta?"**

### **SIM.**

O experimento Challenger **falsificou a premissa de que a concisão e a baixa variabilidade de E1 dependiam da entrega dos números (37% CPU, 61% RAM, 54 °C)**.

1. **O modelo NÃO reverteu à cauda longa de E0:**
   * Quando o retorno da ferramenta foi `null` com mensagem de erro, o modelo **não gerou** os tutoriais prolixos de 4.000 tokens com comandos para Linux/macOS/Windows.
   * Em todas as 5 rodadas (5/5), o modelo gerou entre **259 e 411 tokens**, limitando-se a reportar o status de indisponibilidade e sugerir diagnósticos pontuais do serviço de telemetria.
2. **A variância permaneceu amortecida:**
   * O desvio padrão de latência em E1-C foi de **±3,16 s** (virtualmente idêntico aos **±3,42 s** de E1), enquanto E0 exibiu **±104,10 s**.

---

## 6. Descoberta Fundamental de AI Engineering

O experimento E1-C revelou uma **dissociação estrutural** entre Eficiência e Eficácia:

```text
Eficácia (Factualidade / Grounding)  ---> Depende do DADO retornado pela ferramenta
Eficiência (Previsibilidade Temporal) ---> Depende da ESTRUTURA DO PROTOCOLO de tool calling
```

* **Por que E0 é caótico?**  
  Na ausência de um protocolo de ferramentas, o modelo assume o papel de "assistente generalista sem recursos". Quando não sabe algo, sua política de amostragem tenta compensar a falta de ação externa gerando manuais extensos e enciclopédicos.
* **Por que E1 e E1-C são estáveis?**  
  A simples presença do **protocolo de tool calling** (solicitação estruturada $\to$ resposta de ambiente $\to$ síntese) restringe o espaço de geração do modelo. O LLM atua como um despachante de serviço: uma vez que o evento da ferramenta ocorreu (seja sucesso ou falha), ele resume o resultado e encerra o turno.

---

## 7. Conclusão Final do Ciclo E1 / E1-C

1. A hipótese original de E1 foi **refinada**: o ganho de velocidade e previsibilidade não veio do valor numérico fornecido, mas da **imposição arquitetural do protocolo de ferramentas**, que elimina a prolixidade compensatória do LLM.
2. A ferramenta em si é necessária para a **qualidade do dado** (sem ela, temos 0% de grounding factual em E0 e E1-C); contudo, a **menor dispersão de tempo e a contenção de geração observadas** são produtos da **engenharia de contexto e protocolo**.
3. Esse achado encerra o ciclo de Tool Use e estabelece a ponte perfeita para **E2 — Context Engineering**.
