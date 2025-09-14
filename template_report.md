# 📝 Template de Relatório Técnico de Laboratório

## 1. Informações do grupo
- **🎓 Curso:** Engenharia de Software
- **📘 Disciplina:** Laboratório de Experimentação de Software
- **🗓 Período:** 6° Período
- **👨‍🏫 Professor(a):** Prof. Dr. João Paulo Carneiro Aramuni
- **👥 Membros do Grupo:** [Arthur Ferreira, Kimberly Liz, Renato Cazzoletti]

---

## 2. Introdução
Este laboratório tem como objetivo analisar aspectos da qualidade de repositórios Java desenvolvidos de forma colaborativa, correlacionando-os com características do processo de desenvolvimento. Em projetos open-source, onde diversos desenvolvedores contribuem, existe o risco de degradação dos atributos de qualidade interna como modularidade, manutenibilidade e legibilidade.

A análise será realizada nos top-1.000 repositórios Java mais populares do GitHub, utilizando a ferramenta CK (Code Metrics) para calcular métricas de qualidade de código, correlacionando-as com métricas de processo de desenvolvimento.

### 💡 Hipóteses Informais - Informal Hypotheses (IH):

- **IH01:** Repositórios mais populares (maior número de estrelas) tendem a apresentar melhor qualidade de código, com menores valores de acoplamento (CBO) devido a maior revisão por pares.
- **IH02:** Sistemas mais maduros (maior idade) apresentam maior profundidade de herança (DIT), indicando evolução arquitetural ao longo do tempo.
- **IH03:** Repositórios com maior atividade (mais releases) mantêm melhor coesão (menores valores de LCOM), devido à refatoração contínua.
- **IH04:** Projetos maiores (maior LOC) tendem a ter maior acoplamento (CBO) devido à complexidade inerente do sistema.
- **IH05:** Repositórios populares apresentam correlação positiva entre tamanho e número de releases, indicando desenvolvimento ativo.

---

## 3. Tecnologias e ferramentas utilizadas
- **💻 Linguagem de Programação:** Python 3.x
- **🛠 Frameworks/Bibliotecas:** Pandas, Matplotlib, Seaborn, GitPython, GQL (GraphQL)
- **🌐 APIs utilizadas:** GitHub GraphQL API
- **📦 Dependências:** requests, python-dotenv, gql
- **⚙️ Ferramenta de Análise:** CK Tool (Code Metrics)

---

## 4. Metodologia

### 4.1 Coleta de dados
- Foram coletados dados dos top-1.000 repositórios Java mais populares do GitHub utilizando a GitHub GraphQL API.
- Critérios de seleção: repositórios com linguagem primária Java, ordenados por número de estrelas (stargazerCount).
- Paginação implementada com PAGE_SIZE = 25 para otimizar as requisições à API.

### 4.2 Filtragem e paginação
- Utilizada paginação da API GitHub para coletar grandes volumes de dados de forma eficiente.
- Implementado sistema de retry com backoff exponencial para lidar com rate limits da API.
- ⏱ Tempo médio de coleta: aproximadamente 15-20 minutos para 1.000 repositórios.

### 4.3 Normalização e pré-processamento
- Os dados foram organizados em formato CSV para facilitar análise posterior.
- Tratamento de dados ausentes e normalização de datas (formato ISO 8601).
- Cálculo da idade dos repositórios baseado na data de criação.

### 4.4 Cálculo de métricas

#### Métricas de Processo:
- **Popularidade:** Número de estrelas (stargazerCount)
- **Tamanho:** Linhas de código (LOC) e linhas de comentários
- **Atividade:** Número de releases
- **Maturidade:** Idade em anos (calculada a partir de createdAt)

#### Métricas de Qualidade (CK Tool):
- **CBO:** Coupling Between Objects - mede acoplamento entre classes
- **DIT:** Depth of Inheritance Tree - profundidade da árvore de herança
- **LCOM:** Lack of Cohesion of Methods - falta de coesão entre métodos

### 4.5 Automação da coleta
- Desenvolvido script Python para automação do processo de:
  1. Clonagem de repositórios via download de ZIP
  2. Execução da ferramenta CK em cada repositório
  3. Consolidação dos resultados em arquivos CSV
  4. Sumarização das métricas por repositório

---

## 5. Questões de pesquisa

Liste as questões de pesquisa que guiaram o estudo, com suas métricas associadas:

**🔍 Questões de Pesquisa - Research Questions (RQs):**

| RQ   | Pergunta | Métrica utilizada | Código da Métrica |
|------|----------|-----------------|-----------------|
| RQ01 | Qual a relação entre a popularidade dos repositórios e as suas características de qualidade? | ⭐ Número de Estrelas vs CBO, DIT, LCOM | LM01, QM01, QM02, QM03 |
| RQ02 | Qual a relação entre a maturidade dos repositórios e as suas características de qualidade? | 🕰 Idade do Repositório vs CBO, DIT, LCOM | LM02, QM01, QM02, QM03 |
| RQ03 | Qual a relação entre a atividade dos repositórios e as suas características de qualidade? | 📦 Número de Releases vs CBO, DIT, LCOM | LM03, QM01, QM02, QM03 |
| RQ04 | Qual a relação entre o tamanho dos repositórios e as suas características de qualidade? | 📏 LOC vs CBO, DIT, LCOM | LM04, QM01, QM02, QM03 |

---

## 6. Resultados

Apresente os resultados obtidos, com tabelas e gráficos sempre que possível.

---

### 6.1 Métricas

Inclua métricas relevantes de repositórios do GitHub, separando **métricas do laboratório** e **métricas adicionais trazidas pelo grupo**:

#### 📊 Métricas de Laboratório - Lab Metrics (LM)
| Código | Métrica | Descrição |
|--------|--------|-----------|
| LM01 | 🕰 Idade do Repositório (anos) | Tempo desde a criação do repositório até o momento atual, medido em anos. |
| LM02 | ✅ Pull Requests Aceitas | Quantidade de pull requests que foram aceitas e incorporadas ao repositório. |
| LM03 | 📦 Número de Releases | Total de versões ou releases oficiais publicadas no repositório. |
| LM04 | ⏳ Tempo desde a Última Atualização (dias) | Número de dias desde a última modificação ou commit no repositório. |
| LM05 | 📋 Percentual de Issues Fechadas (%) | Proporção de issues fechadas em relação ao total de issues criadas, em percentual. |
| LM06 | ⭐ Número de Estrelas | Quantidade de estrelas recebidas no GitHub, representando interesse ou popularidade. |
| LM07 | 🍴 Número de Forks | Número de forks, indicando quantas vezes o repositório foi copiado por outros usuários. |
| LM08 | 📏 Tamanho do Repositório (LOC) | Total de linhas de código (Lines of Code) contidas no repositório. |

#### 💡 Métricas adicionais trazidas pelo grupo - Additional Metrics (AM)
| Código | Métrica | Descrição |
|------|--------|------------|
| AM01 | 💻 Linguagem Primária | Linguagem de programação principal do repositório (ex.: Python, JavaScript, Java) |
| AM02 | 🔗 Forks vs Pull Requests Aceitas | Relação entre número de forks e pull requests aceitas |
| AM03 | 📈 Evolução Temporal | Evolução temporal de releases e pull requests aceitas |
| AM04 | 🌟 Big Numbers | Métricas com valores expressivos (commits, branches, stars, releases) |

> Obs.: Adapte ou acrescente métricas conforme o seu dataset.

---

### 6.2 Distribuição por categoria

Para métricas categóricas, como linguagem de programação, faça contagens e tabelas de frequência:

| Linguagem | Quantidade de Repositórios |
|---------------|------------------------|
| 🐍 Python     | 350                    |
| 💻 JavaScript | 300                    |
| ☕ Java        | 200                    |
| 📦 Outros     | 150                    |

---

### 6.3 Relação das RQs com as Métricas

| RQ   | Pergunta | Métrica utilizada | Código |
|------|----------|-----------------|--------|
| RQ01 | Sistemas populares são maduros/antigos? | 🕰 Idade do Repositório (calculado a partir da data de criação) | LM01 |
| RQ02 | Sistemas populares recebem muita contribuição externa? | ✅ Total de Pull Requests Aceitas | LM02 |
| RQ03 | Sistemas populares lançam releases com frequência? | 📦 Total de Releases | LM03 |
| RQ04 | Sistemas populares são atualizados com frequência? | ⏳ Tempo desde a Última Atualização (dias) | LM04 |
| RQ05 | Sistemas populares são escritos nas linguagens mais populares? | 💻 Linguagem primária de cada repositório | AM01 |
| RQ06 | Sistemas populares possuem alto percentual de issues fechadas? | 📋 Razão entre número de issues fechadas pelo total de issues | LM05 |
| RQ07 | Sistemas escritos em linguagens mais populares recebem mais contribuição externa, lançam mais releases e são atualizados com mais frequência? | ✅ Pull Requests Aceitas, 📦 Número de Releases, ⏳ Tempo desde a Última Atualização, 💻 Linguagem primária | LM02, LM03, LM04, AM01 |

---

### 6.4 Sugestões de gráficos

Para criar visualizações das métricas, recomenda-se utilizar como referência o projeto **Seaborn Samples**:  
- 🔗 Repositório: [Projeto Seaborn Samples](https://github.com/joaopauloaramuni/laboratorio-de-experimentacao-de-software/tree/main/PROJETOS/Projeto%20Seaborn%20Samples)

- **📊 Histograma**: `grafico_histograma.png` → distribuição de idade, PRs aceitas ou estrelas.  
- **📈 Boxplot**: `grafico_boxplot.png` → dispersão de métricas como forks, issues fechadas ou LOC.  
- **📊 Gráfico de Barras**: `grafico_barras.png` → comparação de métricas entre linguagens.  
- **🥧 Gráfico de Pizza**: `grafico_pizza.png` → percentual de repositórios por linguagem.  
- **📈 Gráfico de Linha**: `grafico_linha.png` → evolução de releases ou PRs ao longo do tempo.  
- **🔹 Scatterplot / Dispersão**: `grafico_dispersao.png` → relação entre estrelas e forks.  
- **🌡 Heatmap**: `grafico_heatmap.png` → correlação entre métricas (idade, PRs, stars, forks, issues).  
- **🔗 Pairplot**: `grafico_pairplot.png` → análise de múltiplas métricas simultaneamente.  
- **🎻 Violin Plot**: `grafico_violin.png` → distribuição detalhada de métricas por subgrupo.  
- **📊 Barras Empilhadas**: `grafico_barras_empilhadas.png` → comparação de categorias dentro de métricas.

> 💡 Dica: combine tabelas e gráficos para facilitar a interpretação e evidenciar padrões nos dados.

### 6.5 Estatísticas Descritivas

Apresente as estatísticas descritivas das métricas analisadas, permitindo uma compreensão mais detalhada da distribuição dos dados.

| Métrica | Código | Média | Mediana | Moda | Desvio Padrão | Mínimo | Máximo |
|---------|--------|------|--------|-----|---------------|--------|--------|
| 🕰 Idade do Repositório (anos) | LM01 | X | Y | Z | A | B | C |
| ✅ Pull Requests Aceitas | LM02 | X | Y | Z | A | B | C |
| 📦 Número de Releases | LM03 | X | Y | Z | A | B | C |
| ⏳ Tempo desde a Última Atualização (dias) | LM04 | X | Y | Z | A | B | C |
| 📋 Percentual de Issues Fechadas (%) | LM05 | X | Y | Z | A | B | C |
| ⭐ Número de Estrelas (Stars) | LM06 | X | Y | Z | A | B | C |
| 🍴 Número de Forks | LM07 | X | Y | Z | A | B | C |
| 📏 Tamanho do Repositório (LOC) | LM08 | X | Y | Z | A | B | C |

> 💡 Dica: Inclua gráficos como histogramas ou boxplots junto com essas estatísticas para facilitar a interpretação.

---

## 7. Discussão

Nesta seção, compare os resultados obtidos com as hipóteses informais levantadas pelo grupo no início do experimento.

- **✅ Confirmação ou refutação das hipóteses**: identifique quais hipóteses foram confirmadas pelos dados e quais foram refutadas.  
- **❌ Explicações para resultados divergentes**: caso algum resultado seja diferente do esperado, tente levantar possíveis causas ou fatores que possam ter influenciado.  
- **🔍 Padrões e insights interessantes**: destaque tendências ou comportamentos relevantes observados nos dados que não haviam sido previstos nas hipóteses.  
- **📊 Comparação por subgrupos (opcional)**: se houver segmentação dos dados (ex.: por linguagem de programação, tamanho do repositório), discuta como os resultados se comportam em cada grupo.  

> Relacione sempre os pontos observados com as hipóteses informais definidas na introdução, fortalecendo a análise crítica do experimento.

---

## 8. Conclusão

Resumo das principais descobertas do laboratório.

- **🏆 Principais insights:**  
  - Big numbers encontrados nos repositórios, popularidade e métricas destacadas.  
  - Descobertas relevantes sobre padrões de contribuição, releases, issues fechadas ou linguagens mais utilizadas.  
  - Confirmações ou refutações das hipóteses informais levantadas pelo grupo.

- **⚠️ Problemas e dificuldades enfrentadas:**  
  - Limitações da API do GitHub e paginação de grandes volumes de dados.  
  - Normalização e tratamento de dados inconsistentes ou ausentes.  
  - Desafios com cálculos de métricas ou integração de múltiplos arquivos CSV.  

- **🚀 Sugestões para trabalhos futuros:**  
  - Analisar métricas adicionais ou aprofundar correlações entre métricas de qualidade e métricas de processo.  
  - Testar outras linguagens de programação ou frameworks.  
  - Implementar dashboards interativos para visualização de grandes volumes de dados.  
  - Explorar métricas de tendências temporais ou evolução de repositórios ao longo do tempo.

---

## 9. Referências

- [📌 GitHub GraphQL API Documentation](https://docs.github.com/en/graphql)
- [📌 CK Metrics Tool](https://github.com/mauricioaniche/ck)
- [📌 Chidamber, S. R., & Kemerer, C. F. (1994). A metrics suite for object oriented design](https://ieeexplore.ieee.org/document/295895)
- [📌 Biblioteca Pandas](https://pandas.pydata.org/)
- [📌 Matplotlib Documentation](https://matplotlib.org/)
- [📌 Seaborn Statistical Data Visualization](https://seaborn.pydata.org/)

---

## 10. Apêndices

### A. Scripts Desenvolvidos

#### A.1 Script de Coleta via GitHub API (`github_collector.py`)
```python
# Script fornecido para coleta dos top-1000 repositórios Java
# Utiliza GraphQL API do GitHub com paginação e retry
```

#### A.2 Script de Extração de Métricas CK (`ck_metrics_extractor.py`)
```python
# Script para automação da ferramenta CK
# Inclui clonagem, execução e consolidação de resultados
```

#### A.3 Query GraphQL (`query.graphql`)
```graphql
# Query utilizada para buscar repositórios Java ordenados por estrelas
```

### B. Arquivos de Dados

- 💾 `repositories.csv` - Lista dos 1.000 repositórios coletados
- 💾 `all_class_metrics.csv` - Métricas consolidadas de todas as classes
- 💾 `summary_metrics.csv` - Sumarização das métricas por repositório

### C. Configuração do Ambiente

#### C.1 Dependências Python (`requirements.txt`)
```
pandas==1.5.3
gitpython==3.1.31
gql==3.4.1
python-dotenv==1.0.0
requests==2.31.0
matplotlib==3.7.1
seaborn==0.12.2
```

#### C.2 Configuração da Ferramenta CK
```bash
# Clonagem e compilação da ferramenta CK
git clone https://github.com/mauricioaniche/ck.git
cd ck
mvn clean package
```



---
