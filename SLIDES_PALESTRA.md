---
marp: true
theme: default
paginate: true
header: "Agrupamento Hierárquico e Dendrogramas | Palestra Técnica"
footer: "Apresentação por João | Unsupervised Machine Learning"
style: |
  section {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Segoe UI', system-ui, sans-serif;
  }
  h1, h2, h3 {
    color: #38bdf8;
  }
  strong {
    color: #f43f5e;
  }
  code {
    background-color: #1e293b;
    color: #38bdf8;
  }
  blockquote {
    background-color: #1e293b;
    border-left: 4px solid #38bdf8;
    color: #e2e8f0;
  }
  table {
    font-size: 0.85rem;
  }
  th {
    background-color: #1e293b;
    color: #38bdf8;
  }
---

<!-- _class: lead -->
# Agrupamento Hierárquico & Dendrogramas
### Da Teoria Matemática à Prática em Machine Learning

**João**  
*Palestra Técnica e Didática*

---

## 📌 Agenda da Apresentação (45 min)

1. **A Grande Filosofia:** Por que Agrupamento Hierárquico? (5 min)
2. **Top-Down vs. Bottom-Up:** Duas formas de enxergar o mundo (7 min)
3. **A Matemática da Fusão Aglomerativa:** Fórmula de Lance-Williams (8 min)
4. **Batalha dos Métodos de Ligação:** Ward, Complete, Average, Single (10 min)
5. **Anatomia e Leitura do Dendrograma:** Linha de corte e Espaço Ultramétrico (5 min)
6. **Validação Formal:** Correlação Cofenética (CPCC) e Silhueta (5 min)
7. **Demonstração Interativa Ao Vivo & Conclusão** (5 min)

<!-- note
Boas-vindas à plateia. Ajuste o tom da apresentação: começaremos pela intuição cotidiana e subiremos até o rigor matemático com demonstração ao vivo no navegador.
Tempo estimado: 1 min
-->

---

## 1. O Problema Fundamental do Clustering Tradicional

No **K-Means**, somos forçados a responder uma pergunta crucial **antes** de começar:
> *"Quantos grupos (k) existem nos seus dados?"*

* Na vida real, **raramente sabemos essa resposta a priori**.
* O K-Means impõe partições forçadas e esféricas.
* E se a própria estrutura da natureza for organizada em **múltiplos níveis de zoom**?

<!-- note
Provoque a audiência: 'Quem aqui já teve que chutar o k no K-Means e torcer para o método do cotovelo funcionar?'. Mostre que o K-Means é uma partição plana e arbitrária.
Tempo estimado: 2 min
-->

---

## A Filosofia Hierárquica: A Árvore da Vida

> Em vez de forçar um número $k$ de clusters, construímos **toda a história de relacionamentos** entre os dados.

```
       [ REINO ]        (Macro-estrutura: Nível 1)
           ▼
        [ FILO ]
           ▼
       [ CLASSE ]
           ▼
       [ ESPÉCIE ]      (Micro-estrutura: Detalhe fino)
```

* **Decisão a posteriori:** Você escolhe o nível de abstração **depois** de ver o mapa completo!

<!-- note
Use a analogia taxonômica de Lineu ou pastas do computador. Em cada nível de corte, temos uma resposta válida com granularidade diferente.
Tempo estimado: 2 min
-->

---

## 2. As Duas Estratégias Fundamentais

```
                    [ TODOS OS DADOS EM 1 CLUSTER ]
                               ▲        │
               Divisivo        │        │   Aglomerativo
              (Top-Down)       │        │   (Bottom-Up)
               "Esculpir"      │        │    "Lego"
                               │        ▼
                    [ CADA DADO EM SEU PRÓPRIO CLUSTER ]
```

* **Aglomerativo (AGNES):** Começa com $N$ pontos isolados e vai fundindo os mais próximos. *(95% da literatura foca aqui)*.
* **Divisivo (DIANA):** Começa com 1 grupo gigante e vai fatiando nas maiores disparidades globais.

<!-- note
Enfatize a metáfora: Bottom-up é montar com blocos de Lego; Top-down é esculpir tirando lascas de um bloco de mármore maciço.
Tempo estimado: 2 min
-->

---

## O Desafio Oculto da Estratégia Divisiva (Top-Down)

Por que o método aglomerativo é muito mais popular? **Por causa da explosão combinatória!**

Para dividir um grupo de $N$ pontos em 2 subgrupos não vazios:
$$\text{Partições possíveis} = 2^{N-1} - 1$$

* Para $N = 10$: $511$ combinações (instantâneo).
* Para $N = 30$: mais de **536 milhões** de combinações.
* Para $N = 100$: **$\approx 6,3 \times 10^{29}$** combinações (impossível!).

> **Solução na Prática:** Heurísticas como **DIANA** (*Splinter Group*) e **Bisecting K-Means**.

<!-- note
Explique que o Top-Down só é viável graças a heurísticas inteligentes. Diga que detalharemos o DIANA e o Bisecting K-Means.
Tempo estimado: 2 min
-->

---

## O Algoritmo DIANA e o "Motim na Reunião"

1. **O Descontente:** Identifica o ponto com a **maior distância média** para todos os outros da sala. Ele levanta e funda o **Grupo Dissidente** ($S$).
2. **A Migração:** Para cada indivíduo que ficou no grupo original ($R$), calcula-se:
   $$D_i = d(i, R \setminus \{i\}) - d(i, S)$$
3. Se $D_i > 0$, o indivíduo está mais longe dos seus colegas atuais do que do grupo dissidente. **Ele migra para $S$!**
4. Repete até que ninguém mais queira migrar ($D_i \le 0$).

<!-- note
Conte a história com entusiasmo: 'Imagine aquela reunião chata em que a pessoa mais incomodada levanta, senta na outra mesa e começa a atrair os colegas insatisfeitos'. É exatamente isso que a matemática do DIANA faz.
Tempo estimado: 3 min
-->

---

## 3. O Algoritmo Aglomerativo (Passo a Passo)

1. **Inicialização:** Cada observação $x_i$ é um cluster $C_i = \{x_i\}$.
2. **Matriz de Distâncias:** Calcula a matriz $D_{N \times N}$ com métrica $L_2$ (Euclidiana).
3. **Busca Gulosa:** Localiza o par $(C_a, C_b)$ com a menor distância $D_{ab}$.
4. **Fusão:** Une $C_{novo} = C_a \cup C_b$ e registra a altura $D_{ab}$ no dendrograma.
5. **Atualização da Matriz:** Recalcula a distância entre $C_{novo}$ e todos os outros clusters remanescentes via **Critério de Ligação**.
6. **Repetição:** Executa $N-1$ iterações até restar 1 único cluster raiz.

<!-- note
Destaque a natureza 'gulosa' (greedy): uma vez que dois pontos se unem, a decisão é irreversível. Por isso a escolha da métrica e da ligação é crucial.
Tempo estimado: 3 min
-->

---

## ⚠️ Ponto Crítico: Padronização é Obrigatória!

A distância Euclidiana é **cega para unidades físicas**:
$$d(u, v) = \sqrt{(Salário_u - Salário_v)^2 + (Idade_u - Idade_v)^2}$$

* Se o Salário varia de $R\$ 2.000$ a $R\$ 50.000$ ($\Delta = 48.000$);
* E a Idade varia de $18$ a $70$ anos ($\Delta = 52$);
* **A Idade terá peso quase nulo no agrupamento!**

> **Regra de Ouro:** Sempre aplique `StandardScaler` (Z-score) antes de calcular distâncias.

<!-- note
Este é o erro mais comum em entrevistas e projetos práticos. Frise com energia para que a plateia nunca esqueça de padronizar.
Tempo estimado: 2 min
-->

---

## 4. Como Medir Distância entre Grupos? (Linkage)

Como definir a dissimilaridade entre dois conjuntos de pontos $A$ e $B$?

```
   Cluster A                   Cluster B
   ( •   • )                  ( •   • )
   (   •   )                  (   •   )
```

Existem 4 critérios clássicos:
1. **Single Linkage:** Par de pontos mais próximos ($\min$).
2. **Complete Linkage:** Par de pontos mais distantes ($\max$).
3. **Average Linkage (UPGMA):** Média de todas as distâncias par-a-par.
4. **Ward's Method:** Mínimo aumento na variância intra-cluster total ($ESS$).

<!-- note
Apresente os 4 métodos e anuncie que vamos dissecar o comportamento de cada um em seguida.
Tempo estimado: 2 min
-->

---

## Single Linkage e o Perigo do "Efeito Chaining"

$$D(A, B) = \min_{x \in A, y \in B} d(x, y)$$

* **Vantagem:** Consegue identificar clusters de **formatos arbitrários e não-esféricos** (ex.: anéis concêntricos, meias-luas).
* **Armadilha Fatal (Efeito Chaining):**
  * Um único ponto espúrio de ruído pode atuar como uma "ponte" entre duas ilhas distintas.
  * O algoritmo une os dois grandes grupos prematuramente através da ponte de ruído!

<!-- note
Explique o Chaining: basta um ponto no meio do caminho para o Single Linkage achar que as duas galáxias são uma só.
Tempo estimado: 3 min
-->

---

## Complete Linkage: Máxima Compactação

$$D(A, B) = \max_{x \in A, y \in B} d(x, y)$$

* **Comportamento:** Só funde dois grupos se **todos** os pares entre eles estiverem razoavelmente próximos.
* **Formato dos Clusters:** Gera grupos esféricos, densos e com diâmetros homogêneos.
* **Contras:** Muito sensível a *outliers* periféricos (um único ponto distante infla a distância máxima).

<!-- note
O Complete é o oposto conservador do Single. Ele protege contra o chaining, mas sofre se houver um outlier isolado no horizonte.
Tempo estimado: 2 min
-->

---

## Ward's Method: O Campeão dos Negócios

$$\Delta ESS(A, B) = \frac{|A| \cdot |B|}{|A| + |B|} \|\mu_A - \mu_B\|^2_2$$

* **Conceito:** Funde o par de clusters que causa o **menor aumento na variância interna total**.
* **Propriedades:**
  * Gera clusters com tamanhos balanceados e formas compactas.
  * Funciona como um K-Means hierárquico, mas determinístico.
  * Exige distância Euclidiana como base.
* **Recomendação Prática:** É quase sempre o **melhor ponto de partida** em segmentação de clientes e negócios!

<!-- note
Ward é o método padrão da indústria corporativa. Se você não souber qual usar, comece por Ward.
Tempo estimado: 3 min
-->

---

## A Fórmula Mágica de Lance-Williams (1967)

Recalcular a distância entre o novo cluster $(A \cup B)$ e cada cluster $K$ não exige olhar todos os pontos brutos novamente!

$$D(A \cup B, K) = \alpha_A D(A, K) + \alpha_B D(B, K) + \beta D(A, B) + \gamma |D(A, K) - D(B, K)|$$

| Método de Ligação | $\alpha_A$ | $\alpha_B$ | $\beta$ | $\gamma$ |
| :--- | :---: | :---: | :---: | :---: |
| **Single** | $1/2$ | $1/2$ | $0$ | $-1/2$ |
| **Complete** | $1/2$ | $1/2$ | $0$ | $+1/2$ |
| **Average (UPGMA)** | $\frac{\|A\|}{\|A\|+\|B\|}$ | $\frac{\|B\|}{\|A\|+\|B\|}$ | $0$ | $0$ |
| **Ward** | $\frac{\|A\|+\|K\|}{\|A\|+\|B\|+\|K\|}$ | $\frac{\|B\|+\|K\|}{\|A\|+\|B\|+\|K\|}$ | $\frac{-\|K\|}{\|A\|+\|B\|+\|K\|}$ | $0$ |

<!-- note
Mostre que essa fórmula unifica TODOS os métodos hierárquicos em uma única equação matricial rápida. Isso reduz a complexidade de O(N^3) para O(N^2).
Tempo estimado: 3 min
-->

---

## 5. Anatomia e Leitura do Dendrograma

```
  Altura (Dissimilaridade de Fusão)
    ▲
3.0 ┼               ┌───────────────┐          <-- Fusão tardia (grupos distantes)
    │               │               │
2.0 ┼       ┌───────┴───────┐       │
    │       │               │       │  - - - - - Linha de Corte (Threshold = 1.7)
1.0 ┼   ┌───┴───┐           │   ┌───┴───┐      --> 3 Clusters Resultantes!
    │   │       │           │   │       │
0.0 ┼───┴───────┴───────────┴───┴───────┴───►
        1       2           3   4       5      (Observações)
```

* **Eixo Vertical (Altura):** Distância exata na qual a fusão ocorreu.
* **Eixo Horizontal (Folhas):** Ordem arbitrária! Os nós podem girar 180° sem alterar a árvore.

<!-- note
Alerte sobre o erro comum de olhar a proximidade das folhas no eixo X. Mostre que o que vale é a altura do nó conector no eixo Y.
Tempo estimado: 2 min
-->

---

## O Conceito de Espaço Ultramétrico

Um dendrograma válido induz uma métrica especial chamada **Distância Cofenética** ($c_{ij}$).  
Ela atende à **Desigualdade Ultramétrica** (mais forte que a triangular):

$$c(x, z) \le \max(c(x, y), c(y, z))$$

> **Em um espaço ultramétrico, todo triângulo é isósceles com a base mais curta que os dois lados congruentes!**

* Se as alturas forem monótonas ($h_{passo+1} \ge h_{passo}$), a árvore é ultrametricamente perfeita (sem nós invertidos).

<!-- note
Para a audiência técnica/acadêmica, esse é o ápice do rigor formal: o dendrograma não é apenas um gráfico, é um espaço ultramétrico estrito.
Tempo estimado: 2 min
-->

---

## Como Escolher o Ponto de Corte?

Existem duas abordagens quantitativas complementares:

### 1. Critério do Maior Salto Vertical (Aceleração de Fusão)
Procure os ramos verticais mais longos que **não são cruzados** por nenhuma outra fusão horizontal.  
Um salto grande indica que clusters homogêneos tiveram que percorrer uma distância enorme para se unirem.

### 2. Análise do Coeficiente de Silhueta ($s \in [-1, 1]$)
Corta-se a árvore em diferentes valores de $k$ ($2 \le k \le 8$) e escolhe-se o $k$ que maximiza a silhueta média.

<!-- note
Explique como combinar o salto visual com o pico numérico de silhueta para justificar a escolha de k para executivos e clientes.
Tempo estimado: 2 min
-->

---

## 6. Coeficiente de Correlação Cofenética (CPCC)

Como saber se o dendrograma gerado é fiel às distâncias reais dos dados?  
Calcula-se a **Correlação de Pearson** entre a matriz de distâncias original ($d_{ij}$) e a matriz cofenética do dendrograma ($c_{ij}$):

$$r = \frac{\sum (d_{ij} - \bar{d})(c_{ij} - \bar{c})}{\sqrt{\sum (d_{ij} - \bar{d})^2 \sum (c_{ij} - \bar{c})^2}}$$

* **$r > 0.85$:** Excelente fidelidade métrica.
* **$0.75 \le r \le 0.85$:** Boa preservação estrutural.
* **$r < 0.70$:** O dendrograma distorceu o espaço original (experimente outro método de ligação!).

<!-- note
Destaque que o Average Linkage quase sempre atinge o maior CPCC, enquanto o Ward prioriza variância interna e pode ter um CPCC menor.
Tempo estimado: 3 min
-->

---

## Comparativo: Hierárquico vs. K-Means vs. DBSCAN

| Critério | Agrupamento Hierárquico | K-Means | DBSCAN |
| :--- | :---: | :---: | :---: |
| **Número de Clusters ($k$)** | Decidido **a posteriori** | Exigido **a priori** | Automático por densidade |
| **Formato dos Grupos** | Flexível (conforme linkage) | Rígido (esférico) | Formas arbitrárias |
| **Sensibilidade a Outliers** | Alta (Single) / Baixa (Ward) | Alta (afeta centróides) | Baixa (isola o ruído) |
| **Determinístico?** | **Sim (100% reprodutível)** | Não (depende do seed) | Quase sempre sim |
| **Complexidade Temporal** | $O(N^2)$ a $O(N^3)$ | $O(N \cdot k \cdot i)$ | $O(N \log N)$ |
| **Escalabilidade Big Data** | Sofre com $N > 20.000$ | Excelente para milhões | Boa para médio porte |

<!-- note
Este slide é perfeito para tirar dúvidas comparativas. Explique por que o K-Means domina Big Data, mas o Hierárquico domina a interpretabilidade e taxonomia.
Tempo estimado: 3 min
-->

---

<!-- _class: lead -->
# 🖥️ Demonstração Prática Interativa
### Abrindo os Simuladores ao Vivo

1. `dendrograma_interativo.html` (Canvas 2D + Slider de Corte)
2. `comparativo_linkage.html` (Ward vs Complete vs Average vs Single)
3. `comparativo_divisivo.html` (DIANA e Bisecting K-Means)

<!-- note
Transição para o navegador: abra os 3 arquivos HTML e faça os experimentos combinados na frente do público.
Tempo estimado: 5 min
-->

---

## 🎯 Conclusão e Principais Mensagens

1. **Estrutura Natural:** O Agrupamento Hierárquico não impõe partições artificiais; revela a taxonomia latente dos dados.
2. **Padronização:** Sem `StandardScaler`, a maior grandeza numérica domina a geometria.
3. **Escolha Consciente:**
   * Use **Ward** para negócios e clusters compactos;
   * Use **Average** para maior fidelidade métrica (CPCC);
   * Use **Single** com cautela devido ao *efeito chaining*.
4. **Validação Rigorosa:** Sempre reporte o **CPCC** e o **Score de Silhueta** para fundamentar a escolha do número de clusters.

---

<!-- _class: lead -->
# Perguntas & Discussão
### Obrigado!

**Repositório com códigos, testes e simuladores:**  
`https://github.com/joaol/agrupamento-hierarquico`

*Espaço aberto para dúvidas da plateia*
