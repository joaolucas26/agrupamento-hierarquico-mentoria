# Guia Definitivo: Estratégia Divisiva (Top-Down), DIANA e Bisecting K-Means
> **Material Didático e de Aprofundamento para Palestra**  
> *Autor: João / Preparado para Apresentação Técnica e Didática*

---

## Sumário
1. [A Grande Intuição: Esculpir em Mármore vs. Montar Lego](#1-a-grande-intuição-esculpir-em-mármore-vs-montar-lego)
2. [O Desafio Combinatório: Por que a Divisão Ingênua é Impossível?](#2-o-desafio-combinatório-por-que-a-divisão-ingênua-é-impossível)
3. [Algoritmo DIANA (Divisive Analysis) Desmistificado](#3-algoritmo-diana-divisive-analysis-desmistificado)
   - [A Analogia do "Motim na Sala de Reunião"](#a-analogia-do-motim-na-sala-de-reunião)
   - [O Algoritmo Matemático de Macnaughton-Smith](#o-algoritmo-matemático-de-macnaughton-smith)
   - [Exemplo Numérico Resolvido Passo a Passo na Mão](#exemplo-numérico-resolvido-passo-a-passo-na-mão)
4. [Bisecting K-Means (K-Means Bissectante)](#4-bisecting-k-means-k-means-bissectante)
   - [Como Funciona](#como-funciona)
   - [Critérios de Escolha do Próximo Cluster a Dividir](#critérios-de-escolha-do-próximo-cluster-a-dividir)
   - [Por que ele supera o K-Means tradicional?](#por-que-ele-supera-o-k-means-tradicional)
   - [Código Prático com Scikit-Learn](#código-prático-com-scikit-learn)
5. [Outras Heurísticas Top-Down Modernas](#5-outras-heurísticas-top-down-modernas)
   - [PDDP: Divisão por Hiperplano de PCA](#pddp-divisão-por-hiperplano-de-pca)
   - [Furthest-Pair (2-Medoids Divisivo)](#furthest-pair-2-medoids-divisivo)
6. [Batalha de Titãs: Aglomerativo (Bottom-Up) vs. Divisivo (Top-Down)](#6-batalha-de-titãs-aglomerativo-bottom-up-vs-divisivo-top-down)
7. [Roteiro e Dicas de Ouro para a sua Palestra](#7-roteiro-e-dicas-de-ouro-para-a-sua-palestra)

---

## 1. A Grande Intuição: Esculpir em Mármore vs. Montar Lego

Para explicar a diferença entre as duas famílias de clustering hierárquico na sua palestra, use esta analogia visual:

```
[ BOTTOM-UP (Aglomerativo) ]                   [ TOP-DOWN (Divisivo) ]
       "Montar Lego"                              "Esculpir em Mármore"
  
  •   •   •   •   •   •                        ┌─────────────────────────┐
                                               │  •   •   •   •   •   •  │
  Começa com cada peça solta                   │                         │
  e vai conectando os pares mais               │ Um bloco maciço que vai │
  próximos até formar o castelo.               │ sendo talhado em partes │
                                               └───────────┬─────────────┘
          ▼                                                ▼
     [ CASTELO ]                                   [ 2 MACRO-GRUPOS ]
```

* **Aglomerativo (Bottom-Up):** Tem uma **visão míope** no início. Ele decide unir os vizinhos imediatos sem saber se isso fará sentido na estrutura global macroscópica mais tarde.
* **Divisivo (Top-Down):** Tem uma **visão panorâmica (holística)**. Ele enxerga a nuvem inteira de dados e identifica primeiro as maiores fraturas e disparidades estruturais antes de se preocupar com os detalhes individuais.

---

## 2. O Desafio Combinatório: Por que a Divisão Ingênua é Impossível?

Se você perguntar para a plateia: *"Por que 95% das aulas só ensinam o método aglomerativo e ignoram o divisivo?"*, a resposta está na matemática da combinação.

No método aglomerativo, para unir dois clusters entre $N$ existentes, precisamos apenas avaliar:
$$\binom{N}{2} = \frac{N(N-1)}{2} \text{ pares possíveis}$$
Para $N = 100$, são apenas $4.950$ pares. O computador calcula isso em milissegundos.

Porém, para **dividir** um cluster com $N$ pontos em dois subgrupos não vazios ($A$ e $B$):
Cada ponto tem 2 escolhas: ou vai para o subgrupo $A$, ou vai para o subgrupo $B$ ($2^N$ combinações).  
Como a ordem dos subgrupos não importa ($\{A, B\} = \{B, A\}$) e nenhum subgrupo pode ser vazio, o número exato de partições possíveis é:
$$\text{Partições possíveis} = 2^{N-1} - 1$$

### A Tabela da Explosão Combinatória:

| Número de Pontos ($N$) | Maneiras de Dividir em 2 Grupos | Viabilidade Computacional |
| :---: | :---: | :---: |
| **5** | $2^4 - 1 = \mathbf{15}$ | Instantâneo na mão |
| **10** | $2^9 - 1 = \mathbf{511}$ | Instantâneo no PC |
| **20** | $2^{19} - 1 = \mathbf{524.287}$ | Menos de 1 segundo |
| **30** | $2^{29} - 1 = \mathbf{536.870.911}$ ($\approx 5,3 \times 10^8$) | Alguns segundos |
| **50** | $\approx \mathbf{5,6 \times 10^{14}}$ | Horas em supercomputador |
| **100** | $\approx \mathbf{6,3 \times 10^{29}}$ | **Inviável até o fim do universo** |

> 💡 **Conclusão:** É **impossível** testar todas as divisões exatas. Por isso, a estratégia Top-Down depende obrigatoriamente de **heurísticas inteligentes** para encontrar boas divisões em tempo polinomial. As duas mais consagradas são o **DIANA** e o **Bisecting K-Means**.

---

## 3. Algoritmo DIANA (Divisive Analysis) Desmistificado

Introduzido por Leonard Kaufman e Peter J. Rousseeuw em 1990 (no clássico livro *Finding Groups in Data*), o **DIANA** é o algoritmo divisivo determinístico padrão da literatura.

### A Analogia do "Motim na Sala de Reunião"
Imagine uma sala cheia de pessoas em uma reunião que está se tornando desconfortável:

1. **O Descontente Solitário:** Existe uma pessoa que é a mais deslocada de todas (sua distância média para o resto da sala é a maior de todas). Ela não aguenta mais, levanta-se e vai para o outro canto da sala sozinha. Ela acabou de fundar o **Grupo Dissidente** (*Splinter Group*).
2. **O Dilema dos Indecisos:** As outras pessoas que ficaram no grupo original olham para a rodinha antiga e olham para a pessoa dissidente no canto.
3. **A Migração:** Para cada pessoa que ainda está no grupo original, calculamos:
   * *"Qual é minha distância média para as pessoas que ficaram aqui?"*
   * *"Qual é minha distância média para quem já foi para o grupo dissidente?"*
4. Se alguém estiver **mais próximo do grupo dissidente** do que do grupo original, essa pessoa se levanta e migra para o grupo dissidente!
5. Esse processo se repete até que **ninguém mais queira migrar** (todos os que ficaram estão mais próximos dos seus companheiros atuais do que do grupo dissidente).
6. **Pronto!** O grupo foi partido em dois de forma natural e sem testar combinações exponenciais.

---

### O Algoritmo Matemático de Macnaughton-Smith

Seja um cluster $C$ que queremos dividir em dois subgrupos: o remanescente $R$ e o dissidente $S$.

#### Passo 1: Inicialização do Grupo Dissidente ($S$)
Para cada ponto $i \in C$, calcule sua dissimilaridade média em relação a todos os outros pontos de $C$:
$$d_{\text{médio}}(i, C \setminus \{i\}) = \frac{1}{|C| - 1} \sum_{j \in C, j \neq i} d(i, j)$$

O ponto mais isolado (com a **maior distância média**) torna-se a semente do grupo dissidente:
$$i^* = \arg\max_{i \in C} d_{\text{médio}}(i, C \setminus \{i\})$$

Inicializamos:
* $S = \{i^*\}$ (Grupo Dissidente)
* $R = C \setminus \{i^*\}$ (Grupo Remanescente)

#### Passo 2: O Processo Iterativo de Migração
Enquanto houver pontos em $R$, avaliamos cada candidato $i \in R$:
* Distância média de $i$ aos membros do grupo que ele ainda pertence ($R$):
  $$d(i, R \setminus \{i\}) = \frac{1}{|R| - 1} \sum_{j \in R, j \neq i} d(i, j)$$
* Distância média de $i$ aos membros do grupo dissidente ($S$):
  $$d(i, S) = \frac{1}{|S|} \sum_{s \in S} d(i, s)$$
* Calculamos a **diferença de atração**:
  $$D_i = d(i, R \setminus \{i\}) - d(i, S)$$

* **Interpretação de $D_i$:**
  * Se $D_i > 0$: o ponto $i$ está mais longe do seu grupo atual do que do dissidente (ele prefere migrar!).
  * Se $D_i \le 0$: o ponto $i$ prefere ficar onde está.

* Encontramos o ponto $k \in R$ com o **maior valor positivo** de $D_k$:
  $$k = \arg\max_{i \in R} D_i$$
  * Se $D_k > 0$: migramos o ponto $k$ ($R \leftarrow R \setminus \{k\}$ e $S \leftarrow S \cup \{k\}$) e repetimos o Passo 2.
  * Se $D_k \le 0$: **Paramos!** Nenhum ponto restante deseja migrar. A divisão está concluída: o cluster $C$ foi dividido em $R$ e $S$.

#### Passo 3: Escolha do Próximo Cluster a Dividir
Se precisarmos continuar a árvore hierárquica, escolhemos o cluster ativo com o **maior diâmetro** (onde o diâmetro é a maior distância entre qualquer par de pontos do cluster):
$$\text{Diâmetro}(C) = \max_{x, y \in C} d(x, y)$$
E repetimos os Passos 1 e 2 sobre esse cluster até que todos os pontos sejam folhas individuais.

---

### Exemplo Numérico Resolvido Passo a Passo na Mão

Vamos resolver um exemplo didático com **5 pontos unidimensionais** para você mostrar nos slides ou quadro:

$$X = \{A: 1.0, \quad B: 2.0, \quad C: 3.0, \quad D: 8.0, \quad E: 9.0\}$$

Visualmente, qualquer ser humano vê que existem dois grupos naturais: $\{A, B, C\}$ e $\{D, E\}$. Vamos ver a matemática do DIANA provando isso!

#### Matriz de Distâncias Euclidiana:
| | A (1) | B (2) | C (3) | D (8) | E (9) |
|---|---|---|---|---|---|
| **A (1)** | 0 | 1 | 2 | 7 | 8 |
| **B (2)** | 1 | 0 | 1 | 6 | 7 |
| **C (3)** | 2 | 1 | 0 | 5 | 6 |
| **D (8)** | 7 | 6 | 5 | 0 | 1 |
| **E (9)** | 8 | 7 | 6 | 1 | 0 |

#### Etapa 1: Encontrar o Ponto Inicial do Motim (Maior Distância Média)
Calculamos a distância média de cada ponto para os outros 4 pontos:
* $\bar{d}(A) = \frac{1 + 2 + 7 + 8}{4} = \frac{18}{4} = \mathbf{4.50}$
* $\bar{d}(B) = \frac{1 + 1 + 6 + 7}{4} = \frac{15}{4} = 3.75$
* $\bar{d}(C) = \frac{2 + 1 + 5 + 6}{4} = \frac{14}{4} = 3.50$
* $\bar{d}(D) = \frac{7 + 6 + 5 + 1}{4} = \frac{19}{4} = 4.75$
* $\bar{d}(E) = \frac{8 + 7 + 6 + 1}{4} = \frac{22}{4} = \mathbf{5.50}$ ⭐ **(VENCEDOR: Ponto E)**

O ponto **$E$** tem a maior distância média ($5.50$). Logo, **$E$ funda o grupo dissidente!**
* **Dissidente ($S$):** $\{E\}$
* **Remanescente ($R$):** $\{A, B, C, D\}$

---

#### Etapa 2: Primeira Rodada de Migração
Vamos testar quem em $R = \{A, B, C, D\}$ quer se juntar a $S = \{E\}$:

* Para o ponto **A**:
  * Distância média para os outros em $R$ ($\{B, C, D\}$): $\frac{1 + 2 + 7}{3} = \frac{10}{3} \approx 3.33$
  * Distância para $S$ ($\{E\}$): $d(A, E) = 8.0$
  * $D_A = 3.33 - 8.0 = \mathbf{-4.67}$ (Muito negativo, quer ficar!)

* Para o ponto **B**:
  * Distância média em $R$ ($\{A, C, D\}$): $\frac{1 + 1 + 6}{3} = \frac{8}{3} \approx 2.67$
  * Distância para $S$: $d(B, E) = 7.0$
  * $D_B = 2.67 - 7.0 = \mathbf{-4.33}$ (Quer ficar!)

* Para o ponto **C**:
  * Distância média em $R$ ($\{A, B, D\}$): $\frac{2 + 1 + 5}{3} = \frac{8}{3} \approx 2.67$
  * Distância para $S$: $d(C, E) = 6.0$
  * $D_C = 2.67 - 6.0 = \mathbf{-3.33}$ (Quer ficar!)

* Para o ponto **D**:
  * Distância média em $R$ ($\{A, B, C\}$): $\frac{7 + 6 + 5}{3} = \frac{18}{3} = \mathbf{6.00}$
  * Distância para $S$: $d(D, E) = \mathbf{1.0}$
  * $D_D = 6.00 - 1.0 = \mathbf{+5.00}$ 🔥 **(Positivo e expressivo!)**

Como o maior valor é $D_D = +5.00 > 0$, o ponto **$D$ migra para o grupo dissidente!**

Atualização dos grupos:
* **Dissidente ($S$):** $\{D, E\}$
* **Remanescente ($R$):** $\{A, B, C\}$

---

#### Etapa 3: Segunda Rodada de Migração
Vamos testar se alguém restante em $R = \{A, B, C\}$ quer ir para $S = \{D, E\}$:

* Para o ponto **A**:
  * Média em $R$ ($\{B, C\}$): $\frac{1 + 2}{2} = 1.5$
  * Média para $S$ ($\{D, E\}$): $\frac{7 + 8}{2} = 7.5$
  * $D_A = 1.5 - 7.5 = \mathbf{-6.00} < 0$

* Para o ponto **B**:
  * Média em $R$ ($\{A, C\}$): $\frac{1 + 1}{2} = 1.0$
  * Média para $S$ ($\{D, E\}$): $\frac{6 + 7}{2} = 6.5$
  * $D_B = 1.0 - 6.5 = \mathbf{-5.50} < 0$

* Para o ponto **C**:
  * Média em $R$ ($\{A, B\}$): $\frac{2 + 1}{2} = 1.5$
  * Média para $S$ ($\{D, E\}$): $\frac{5 + 6}{2} = 5.5$
  * $D_C = 1.5 - 5.5 = \mathbf{-4.00} < 0$

**Resultado:** Todos os valores $D_i$ são estritamente negativos! Ninguém quer migrar.  
**Fim da Primeira Divisão:** Obtivemos perfeitamente os clusters $\{A, B, C\}$ e $\{D, E\}$.

> 🎯 **Impacto na Palestra:** Esse cálculo manual dura 3 minutos no slide e prova por A + B que a heurística do DIANA é elegante, intuitiva e matematicamente infalível para encontrar a macro-estrutura dos dados.

---

## 4. Bisecting K-Means (K-Means Bissectante)

Se o DIANA é elegante e determinístico, o **Bisecting K-Means** é a versão focada em **alta velocidade e escalabilidade industrial**.

```
                   [ CLUSTER RAIZ: TODOS OS DADOS ]
                                  │
                 Aplica K-Means tradicional com k=2
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
             Cluster 1                       Cluster 2
             (SSE = 450)                    (SSE = 1200) <-- MAIOR ERRO!
                  │                               │
            Mantém parado                   Aplica 2-Means
                                                  │
                                          ┌───────┴───────┐
                                          ▼               ▼
                                     Cluster 2A      Cluster 2B
```

### Como Funciona:
1. Comece com todos os dados em um único cluster.
2. Escolha qual cluster ativo dividir (geralmente o cluster com **maior SSE** - Soma dos Erros Quadráticos).
3. Aplique o algoritmo **K-Means padrão com $k=2$** apenas sobre os pontos desse cluster escolhido.
4. Repita os passos 2 e 3 até atingir a quantidade $k$ de clusters desejada pelo usuário.

---

### Breve Recapitulação: Como Funciona o K-Means Tradicional?

Antes de entender a bisseção, vamos lembrar como o **K-Means padrão** funciona em 4 passos simples:

```
[ PASSO 1: INICIALIZAÇÃO ]    Coloca k centroides aleatórios no espaço.
           ▼
[ PASSO 2: ATRIBUIÇÃO ]       Cada ponto é atribuído ao centróide mais próximo (distância Euclidiana).
           ▼
[ PASSO 3: ATUALIZAÇÃO ]      Cada centróide se move para a média aritmética (centro de massa) dos seus pontos.
           ▼
[ PASSO 4: CONVERGÊNCIA ]     Repete os Passos 2 e 3 até que os centroides parem de se mover.
```

No **Bisecting K-Means**, usamos exatamente esse mesmo algoritmo, mas sempre com **$k=2$** (bisseção), fatiando um único cluster de cada vez em duas metades.

---

### O que é o SSE (Sum of Squared Errors / Inércia)?

**SSE** significa **S**um of **S**quared **E**rrors (*Soma dos Erros Quadráticos*).  
No Scikit-Learn e em estatística, ele também é conhecido como **Inércia** (*Inertia*) ou **Variância Intra-Cluster** (*WCSS - Within-Cluster Sum of Squares*).

#### 1. O que é o "Erro" em Clusterização?
Em aprendizado não supervisionado, o "gabarito" de um ponto é o **centróide ($\mu$)** do cluster ao qual ele foi atribuído.  
Portanto, o **erro** de um ponto $x_i$ é simplesmente a distância entre ele e o centróide do seu grupo:
$$\text{Erro}(x_i) = \|x_i - \mu\|$$

#### 2. Por que elevamos ao quadrado?
Elevamos a distância ao quadrado por dois motivos:
1. **Evitar cancelamentos:** Distâncias positivas em direções opostas não se anulam.
2. **Penalizar fortemente pontos distantes:** Um ponto muito afastado do centroide gera um erro quadrático desproporcionalmente alto, alertando que o cluster está "esticado" ou heterogêneo.

#### 3. A Fórmula Matemática:
Para um cluster individual $C_j$ com centróide $\mu_j$:
$$SSE(C_j) = \sum_{x \in C_j} \|x - \mu_j\|^2 = \sum_{x \in C_j} \sum_{d=1}^D (x_d - \mu_{j, d})^2$$

E o **SSE Total** de toda a clusterização (composta por $k$ clusters) é a soma dos erros de todos os grupos:
$$SSE_{\text{Total}} = \sum_{j=1}^k SSE(C_j)$$

---

### Exemplo Numérico: Calculando o SSE na Mão (3 Pontos)

Imagine um cluster 2D formado por 3 pontos:
* Ponto 1: $(1, 2)$
* Ponto 2: $(2, 4)$
* Ponto 3: $(3, 3)$

#### Passo 1: Calcular o Centróide ($\mu$)
O centróide é a média das coordenadas $X$ e a média das coordenadas $Y$:
* $\mu_X = \frac{1 + 2 + 3}{3} = \frac{6}{3} = \mathbf{2}$
* $\mu_Y = \frac{2 + 4 + 3}{3} = \frac{9}{3} = \mathbf{3}$  
Logo, o centróide deste cluster é: **$\mu = (2, 3)$**.

#### Passo 2: Calcular o Erro Quadrático de Cada Ponto ao Centróide
* **Para o Ponto 1 $(1, 2)$:**
  $$\text{dist}^2 = (1 - 2)^2 + (2 - 3)^2 = (-1)^2 + (-1)^2 = 1 + 1 = \mathbf{2}$$
* **Para o Ponto 2 $(2, 4)$:**
  $$\text{dist}^2 = (2 - 2)^2 + (4 - 3)^2 = (0)^2 + (1)^2 = 0 + 1 = \mathbf{1}$$
* **Para o Ponto 3 $(3, 3)$:**
  $$\text{dist}^2 = (3 - 2)^2 + (3 - 3)^2 = (1)^2 + (0)^2 = 1 + 0 = \mathbf{1}$$

#### Passo 3: Somar os Erros (SSE do Cluster)
$$SSE = 2 + 1 + 1 = \mathbf{4.0}$$

---

### Por que o Bisecting K-Means Escolhe o Cluster com "Maior SSE" para Dividir?

Pense no SSE como um **termômetro de desorganização (heterogeneidade)**:
* Se um cluster tem **SSE baixo**, significa que os pontos estão super compactos e colados no centróide (já é um grupo excelente e coeso).
* Se um cluster tem **SSE alto**, significa que ele é grande, espalhado ou provavelmente abriga **dois ou mais grupos naturais misturados** sob o mesmo teto!

> 💡 **A Lógica do Bisecting K-Means:**  
> Ao escolher o cluster com **maior SSE** para passar a tesoura do 2-Means, você ataca o ponto mais desorganizado da sua base, garantindo a **maior redução possível no erro total** da partição a cada rodada.

---

### Critérios de Escolha do Próximo Cluster a Dividir:
Na hora de decidir qual cluster fatiar, existem 3 estratégias:
1. **Maior SSE (*Sum of Squared Errors*) - Recomendado:** Divide o cluster mais disperso e heterogêneo (aquele onde os pontos estão mais distantes do seu centroide).
2. **Maior Diâmetro:** Divide o cluster que tem a maior distância euclidiana máxima entre dois pontos.
3. **Maior Contagem de Amostras:** Divide o cluster mais volumoso em quantidade de linhas.


---

### Por que ele supera o K-Means tradicional?
1. **Menos suscetível a mínimos locais:** O K-Means tradicional tenta posicionar todos os $k$ centroides ao mesmo tempo e frequentemente fica preso em configurações sub-ótimas se a inicialização for ruim. O Bisecting K-Means resolve um problema muito mais simples e estável: dividir **1 grupo em 2** a cada iteração.
2. **Produz uma Árvore Hierárquica:** Diferente do K-Means convencional (que só gera uma partição plana), o Bisecting K-Means gera um **dendrograma divisivo completo**.
3. **Complexidade Temporal Quase Linear:** Roda em tempo $O(N \cdot \log k \cdot d \cdot i)$, sendo infinitamente mais rápido que os algoritmos aglomerativos ($O(N^2)$ a $O(N^3)$). É perfeito para grandes bases de dados!

---

### Código Prático com Scikit-Learn

Desde as versões recentes do Scikit-Learn, o `BisectingKMeans` está disponível nativamente:

```python
from sklearn.cluster import BisectingKMeans
from sklearn.datasets import make_blobs

# 1. Gerar dados sintéticos
X, _ = make_blobs(n_samples=500, centers=4, cluster_std=0.8, random_state=42)

# 2. Instanciar Bisecting K-Means
# bisecting_strategy pode ser 'biggest_inertia' (SSE) ou 'largest_cluster'
b_kmeans = BisectingKMeans(
    n_clusters=4,
    bisecting_strategy='biggest_inertia',
    random_state=42
)

# 3. Ajustar o modelo
rotulos = b_kmeans.fit_predict(X)

print(f"Centróides finais encontrados:\n{b_kmeans.cluster_centers_}")
```

---

## 5. Outras Heurísticas Top-Down Modernas

Se a plateia for sênior ou acadêmica, cite estas duas técnicas com elegância:

### 1. PDDP (Principal Direction Divisive Partitioning)
* **Como funciona:** Calcula a Análise de Componentes Principais (PCA) dos dados e projeta todos os pontos sobre o **primeiro autovetor (PC1)** — que é a direção de maior variância dos dados.
* Em seguida, traça um hiperplano perpendicular passando pela média ou mediana para cortar o cluster em dois.
* **Vantagem:** É extremamente rápido e completamente determinístico (sem aleatoriedade de centróides).

### 2. Furthest-Pair (2-Medoids Divisivo)
* **Como funciona:** Encontra o par de pontos com a maior distância mútua no cluster (os dois extremos do diâmetro).
* Usa esses dois pontos como âncoras (medóides) e atribui cada ponto restante à âncora mais próxima.
* Muito intuitivo e resistente a distorções circulares.

---

## 6. Batalha de Titãs: Aglomerativo (Bottom-Up) vs. Divisivo (Top-Down)

| Critério | Aglomerativo (*Bottom-Up*) | Divisivo (*Top-Down* / DIANA / Bisecting) |
| :--- | :--- | :--- |
| **Ponto de Partida** | $N$ clusters de 1 ponto cada | 1 cluster gigante com todos os $N$ pontos |
| **Visão Estrutural** | **Míope:** Decide localmente nas primeiras fusões | **Holística:** Enxerga a dispersão global antes |
| **Complexidade Temporal** | $O(N^2)$ a $O(N^3)$ | $O(N^2)$ no DIANA; **$O(N \cdot k)$** no Bisecting K-Means |
| **Consumo de Memória** | Exige a matriz $N \times N$ ($O(N^2)$) | Bisecting K-Means exige apenas $O(N \cdot d)$ |
| **Eficiência para poucos $k$** | **Ruim:** precisa calcular todas as $N-1$ fusões para chegar em $k=3$ | **Excelente:** para em 2 divisões para achar $k=3$ |
| **Sensibilidade ao Ruído** | Single linkage sofre com *chaining* | Menos suscetível a ruídos pontuais no nível macro |
| **Disponibilidade em libs** | Nativo no Scipy (`linkage`) e Sklearn (`AgglomerativeClustering`) | Scikit-Learn tem `BisectingKMeans`; DIANA presente no pacote `cluster` do R |

---

## 7. Roteiro e Dicas de Ouro para a sua Palestra

### O "Momento Show" na Palestra:
1. **Abra o arquivo interativo [`comparativo_divisivo.html`](file:///c:/Users/joaol/ReposGit/agrupamento%20hierarquico/comparativo_divisivo.html):**
   * Ele foi construído exatamente com os 4 algoritmos divisivos: DIANA, Bisecting K-Means, Furthest-Pair e PDDP.
   * Mostre o botão de avançar passos: a audiência vai ver a linha de corte cortando o plano e as fronteiras ativas separando os grupos de cima para baixo.
2. **Faça a provocação sobre a biblioteca padrão:**
   * *"Pessoal, vocês sabiam que todo mundo usa Aglomerativo não porque ele é melhor, mas porque ele era mais fácil de implementar nos anos 80 sem estourar tempo de CPU? Quando você quer apenas 3 perfis de clientes para o time de marketing, o Top-Down faz muito mais sentido matemático!"*
3. **Feche com a comparação do DIANA:**
   * Mostre o exemplo numérico de 5 pontos ($A, B, C, D, E$). Explique a metáfora do "Motim do ponto E" fundando o grupo dissidente. A plateia nunca mais vai esquecer o conceito.
