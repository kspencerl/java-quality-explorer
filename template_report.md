# 📝 Relatório Final - LAB02 (versão atualizada com hipóteses quantitativas)

## 1. Informações do grupo
- **🎓 Curso:** Engenharia de Software  
- **📘 Disciplina:** Laboratório de Experimentação de Software  
- **🗓 Período:** 6° Período  
- **👨‍🏫 Professor(a):** Prof. Dr. João Paulo Carneiro Aramuni  
- **👥 Membros do Grupo:** Arthur Ferreira, Kimberly Liz, Renato Cazzoletti

---

## 2. Introdução
Este laboratório tem como objetivo analisar aspectos da qualidade de repositórios Java desenvolvidos de forma colaborativa, correlacionando-os com características do processo de desenvolvimento. Em projetos open-source, onde diversos desenvolvedores contribuem, existe o risco de degradação dos atributos de qualidade interna como modularidade, manutenibilidade e legibilidade.

A análise será realizada nos top-1.000 repositórios Java mais populares do GitHub, utilizando a ferramenta CK (Code Metrics) para calcular métricas de qualidade de código, correlacionando-as com métricas de processo de desenvolvimento.


---

## 3. Tecnologias e ferramentas utilizadas
- **💻 Linguagem:** Python 3.x  
- **Bibliotecas:** pandas, numpy, matplotlib, scipy
- **🌐 APIs utilizadas:** GitHub GraphQL API
- **Ferramenta de métricas:** CK (Coupling Between Objects, Depth Inheritance Tree, Lack of Cohesion of Methods)  
- **Fonte de dados:** CSVs com métricas agregadas por repositório.

---

## 4. Metodologia

### 4.1 Pré-processamento  
- Remoção de entradas inconsistentes ou incompletas (ex.: repositórios com métricas nulas ou negativas).
- Normalização de formatos de datas (para cálculo de idade dos repositórios).
- Verificação de outliers extremos em métricas como LOC e LCOM (registrados mas não excluídos, pois refletem a realidade de projetos muito grandes).

 
### 4.2 Filtragem e paginação
- Utilizada paginação da API GitHub para coletar grandes volumes de dados de forma eficiente.
- Implementado sistema de retry com backoff exponencial para lidar com rate limits da API.
- Tempo médio de coleta: aproximadamente 5 horas e 30 minutos para 1.000 repositórios.
- Os dados foram organizados em formato CSV para facilitar análise posterior.

### 4.2 Cálculo de métricas de processo  
- **Popularidade:** número de estrelas do repositório.  
- **Atividade:** número de releases.  
- **Maturidade:** idade em anos (diferença entre data de criação e 21/09/2025).  
- **Tamanho:** linhas de código (LOC). 

### 4.4 Análises realizadas  
- Estatísticas descritivas (média, mediana, desvio-padrão) para cada métrica.  
- **Correlação de Spearman** para testar associações entre métricas de processo e qualidade.  
- **Visualizações gráficas** (scatterplots) para apoiar a interpretação.

###  4.5 Interpretação das estatísticas
As análises utilizaram duas principais medidas estatísticas:
ρ de Spearman (Rho de Spearman): Medida de correlação que indica a força e direção da relação entre duas variáveis:

-  -1 a -0.7: Correlação negativa forte
- -0.7 a -0.3: Correlação negativa moderada
- -0.3 a 0.3: Correlação fraca ou inexistente
- 0.3 a 0.7: Correlação positiva moderada
- 0.7 a 1: Correlação positiva forte

p-valor: Indica se a correlação é estatisticamente significativa:

- p < 0.05: Correlação significativa (confiável)
- p ≥ 0.05: Correlação não significativa (pode ser coincidência)


---

## 5. Resultados por Questão de Pesquisa (RQ)

### RQ01 — Popularidade (stars) vs métricas de qualidade  

- Stars vs CBO: ρ = -0.001, p = 0.969 (correlação muito fraca, não significativa)
- Stars vs DIT: ρ = -0.018, p = 0.596 (correlação muito fraca, não significativa)
- Stars vs LCOM: ρ = 0.034, p = 0.324 (correlação muito fraca, não significativa)

- Correlações fracas/nulas.  
- Não há evidência de que repositórios mais populares tenham melhor qualidade interna.

<img width="2941" height="2062" alt="image" src="https://github.com/user-attachments/assets/cf109f08-1844-4666-a234-c6dc62fdf47f" />
<img width="2942" height="2062" alt="image" src="https://github.com/user-attachments/assets/b643c039-ff00-46cc-8704-fb0b30d4fbdc" />
<img width="2943" height="2062" alt="image" src="https://github.com/user-attachments/assets/3617aacf-b134-4b6d-a624-6308808df07f" />



---

### RQ02 — Maturidade (idade) vs métricas de qualidade  

- Age vs CBO: ρ = -0.002, p = 0.946 (correlação muito fraca, não significativa)
- Age vs DIT: ρ = 0.280, p = 1.34e-16 (correlação fraca positiva, significativa)
- Age vs LCOM: ρ = 0.177, p = 2.16e-07 (correlação fraca positiva, significativa)

- Idade correlaciona positivamente com DIT e LCOM.  
- Projetos mais antigos tendem a apresentar hierarquias mais profundas e menor coesão.

<img width="2949" height="2062" alt="image" src="https://github.com/user-attachments/assets/d0f011fb-9327-4a90-a4c4-53db74dafd14" />
<img width="2950" height="2062" alt="image" src="https://github.com/user-attachments/assets/1f6c08f4-79b6-49e6-8995-f309e6457c11" />
<img width="2950" height="2062" alt="image" src="https://github.com/user-attachments/assets/744c38fc-03cd-4b9b-835c-c18e8e67bee9" />


---

### RQ03 — Atividade (número de releases) vs métricas de qualidade  

- Releases vs CBO: ρ = 0.386, p = 2.86e-31 (correlação moderada positiva, significativa)
- Releases vs DIT: ρ = 0.257, p = 3.37e-14 (correlação fraca positiva, significativa)
- Releases vs LCOM: ρ = 0.339, p = 4.13e-24 (correlação moderada positiva, significativa)

- Correlações positivas com CBO e LCOM.  
- Projetos com mais releases apresentam maior acoplamento e menor coesão.

<img width="2949" height="2062" alt="image" src="https://github.com/user-attachments/assets/521510a4-14ac-42b7-8d46-83b4ee20fbac" />
<img width="2950" height="2062" alt="image" src="https://github.com/user-attachments/assets/f593c224-2bc9-4824-90d3-7f481d5bbb3a" />
<img width="2950" height="2062" alt="image" src="https://github.com/user-attachments/assets/ad757d40-bb32-4989-8c56-b50102d462c3" />


---

### RQ04 — Tamanho (LOC) vs métricas de qualidade  

- LOC vs CBO: ρ = 0.291, p = 6.47e-18 (correlação fraca positiva, significativa)
- LOC vs DIT: ρ = 0.258, p = 2.64e-14 (correlação fraca positiva, significativa)
- LOC vs LCOM: ρ = 0.327, p = 2.1e-22 (correlação moderada positiva, significativa)

- Correlações positivas com CBO e LCOM.  
- Projetos maiores tendem a ser mais acoplados e menos coesos.

<img width="2949" height="2062" alt="image" src="https://github.com/user-attachments/assets/6f7391ce-96e0-4cf0-8357-81648bbe8834" />
<img width="2950" height="2062" alt="image" src="https://github.com/user-attachments/assets/4fe96523-bc3e-42b5-b45f-9e598cfd73ac" />
<img width="2950" height="2062" alt="image" src="https://github.com/user-attachments/assets/47a09ada-de4d-4679-a198-c9d89f16cff1" />


---

## 6. hipóteses quantitativas

1. **H1 — Repositórios mais populares (mais estrelas) têm mais releases.**  
   *Teste:* Spearman (stars vs releases).

Resultado: ρ = 0.108, p = 0.00167 (correlação fraca positiva, significativa)
Interpretação: Existe uma correlação fraca mas significativa entre popularidade e atividade de releases. Repositórios mais populares tendem a ter ligeiramente mais releases, o que pode refletir maior engajamento da comunidade ou pressão por atualizações.

  <img width="2943" height="2062" alt="image" src="https://github.com/user-attachments/assets/b0197965-fadb-4830-9645-2bc380281464" />


3. **H2 — Repositórios mais antigos apresentam maior LOC.**  
   *Teste:* Spearman (idade vs LOC).

Resultado: ρ = 0.102, p = 0.00302 (correlação fraca positiva, significativa)
Interpretação: Projetos mais antigos tendem a ser maiores, confirmando a hipótese de que sistemas crescem ao longo do tempo com adição de funcionalidades e melhorias.

 <img width="2950" height="2062" alt="image" src="https://github.com/user-attachments/assets/b52bd800-8e34-4b7d-847f-a659f6445273" />
 

5. **H3 — Projetos maiores (LOC) têm maior CBO.**  
   *Teste:* Spearman (LOC vs CBO).

Resultado: ρ = 0.291, p = 6.47e-18 (correlação fraca positiva, significativa)
Interpretação: Sistemas maiores apresentam maior acoplamento entre objetos, confirmando que o crescimento do sistema está associado ao aumento da complexidade estrutural.

<img width="2949" height="2062" alt="image" src="https://github.com/user-attachments/assets/76e316f2-a991-4aa2-9738-62a39240fb55" />


7. **H4 — Repositórios com mais releases apresentam maior LCOM.**  
   *Teste:* Spearman (releases vs LCOM).

Resultado: ρ = 0.339, p = 4.13e-24 (correlação moderada positiva, significativa)
Interpretação: Projetos com mais releases têm menor coesão (LCOM maior), sugerindo que a pressão por entregas frequentes pode impactar negativamente a qualidade interna do código.

  <img width="2950" height="2062" alt="image" src="https://github.com/user-attachments/assets/c153d9a0-5e31-4d99-b6e4-9080cfac46b1" />
 

9. **H5 — Repositórios mais populares (estrelas) apresentam maior DIT.**  
   *Teste:* Spearman (stars vs DIT).

Resultado: ρ = -0.018, p = 0.596 (correlação muito fraca negativa, não significativa)
Interpretação: Não há relação significativa entre popularidade e profundidade de herança. A popularidade não está associada à complexidade das hierarquias de classes.

<img width="2942" height="2062" alt="image" src="https://github.com/user-attachments/assets/b42252fb-f79b-4744-929a-c0d6c715a2dd" />

---

## 7. Estatísticas descritivas

| Métrica | Média | Mediana | Desvio Padrão | Mín | Máx |
|---------|--------|---------|---------------|-----|-----|
| Stars | 8,901 | 5,579 | 10,326 | 3,415 | 117,049 |
| Releases | 33 | 9 | 73 | 0 | 1,000 |
| Age (anos) | 9.65 | 9.76 | 2.97 | 0.18 | 16.68 |
| LOC | 115,828 | 32,740 | 253,247 | 50 | 2,523,271 |
| CBO | 5.22 | 5.19 | 1.79 | 0.00 | 16.33 |
| DIT | 1.47 | 1.41 | 0.37 | 1.00 | 4.39 |
| LCOM | 61.02 | 23.62 | 159.99 | 0.00 | 1,674.70 |

---

## 8. Discussão e limitações
- As hipóteses H1, H2, H3 e H4 foram confirmadas com significância estatística, embora com correlações entre fracas e moderadas.
- A hipótese H5 foi rejeitada, não havendo relação entre popularidade e profundidade de herança.
- Correlação não implica causalidade - as relações encontradas indicam associações, mas não relações de causa e efeito.
- A alta variabilidade nas métricas (desvios padrão elevados) indica grande diversidade nos projetos analisados.
---

## 9. Conclusão
- **Popularidade vs Qualidade:** Não há relação forte entre popularidade (estrelas) e qualidade interna do código.
- **Maturidade:** Projetos mais antigos tendem a ter hierarquias mais complexas e menor coesão.
- **Atividade:** Maior frequência de releases está associada a maior acoplamento e menor coesão.
- **Tamanho:** Sistemas maiores apresentam maior complexidade estrutural e menor qualidade interna.
- **Implicações:** O desenvolvimento colaborativo em projetos open-source pode estar sujeito a trade-offs entre produtividade (releases frequentes) e qualidade interna.

---
