# Playbook da Demonstração Ao Vivo (Live Demo Playbook)
> **Roteiro Minuto a Minuto para Conduzir os Simuladores Interativos na Palestra**  
> *Autor: João / Duração Estimada da Demonstração: 8 a 10 minutos*

---

## 🎯 Objetivo da Demonstração Ao Vivo
Tirar o agrupamento hierárquico do papel e transformá-lo em uma experiência visual viva e inesquecível. Em vez de apenas mostrar fórmulas estáticas, você vai interagir com os dados em tempo real no navegador, provocando a audiência e demonstrando as forças e fraquezas de cada método.

---

## 💻 Preparação Prévia (Antes de Subir ao Palco)

1. **Abra 3 abas no seu navegador padrão (Chrome, Edge ou Firefox):**
   * **Aba 1:** [`dendrograma_interativo.html`](file:///c:/Users/joaol/ReposGit/agrupamento%20hierarquico/dendrograma_interativo.html)
   * **Aba 2:** [`comparativo_linkage.html`](file:///c:/Users/joaol/ReposGit/agrupamento%20hierarquico/comparativo_linkage.html)
   * **Aba 3:** [`comparativo_divisivo.html`](file:///c:/Users/joaol/ReposGit/agrupamento%20hierarquico/comparativo_divisivo.html)
2. **Ajuste o Zoom do Navegador:** Configure o zoom entre `110%` e `125%` (via `Ctrl + +`) para que a última fileira da plateia enxergue os textos e os eixos com nitidez.
3. **Desconecte o Wi-Fi se desejar:** Os arquivos rodam **100% offline**, garantindo zero risco de lentidão ou queda de internet.

---

## 🎬 Ato 1: O Simulador Livre (`dendrograma_interativo.html`)
*Tempo sugerido: 3 a 4 minutos*

### Passo 1: O Cenário Ideal e a Linha de Corte
1. Com a Aba 1 aberta, clique no botão azul **"3 Clusters Esféricos"** (Método padrão: **Ward**).
2. **O que falar:**
   > *"Observem a tela: temos 21 pontos divididos em três grupos visíveis no plano 2D à esquerda. À direita, o dendrograma foi construído calculando todas as distâncias de baixo para cima."*
3. Aponte para a linha vermelha tracejada no dendrograma.
4. **Interação com a Plateia:**
   * Mova o slider **"✂️ Linha de Corte (Altura)"** para cima: mostre o contador de clusters cair para $k=2$ e depois $k=1$.
   * Mova o slider para baixo: mostre os ramos se multiplicando em $k=4, 5, 8$ e os pontos no Canvas mudando de cor instantaneamente.
   * **Frase de impacto:** *"Vejam que eu não precisei rodar o modelo de novo! Uma vez construída a árvore, o número de clusters é apenas um corte na régua."*

### Passo 2: A Mágica do "Assistir Fusão" (Passo a Passo)
1. Clique no botão vermelho **"Limpar"**.
2. Dê **6 cliques rápidos no canvas** criando pontos à sua escolha (3 no canto superior esquerdo e 3 no canto inferior direito).
3. Clique em **"▶️ Assistir Fusão"**.
4. **O que falar enquanto a animação roda:**
   > *"Vejam a iteração gulosa acontecendo: a cada segundo, o algoritmo localiza os dois pontos mais próximos, desenha a linha de união no gráfico e sobe um novo galho no dendrograma. Isso se repete até restar apenas um grupo raiz."*

---

## 🎬 Ato 2: A Batalha dos Métodos de Ligação (`comparativo_linkage.html`)
*Tempo sugerido: 3 minutos*

### O "Momento Choque": Demonstrando o Efeito Chaining
1. Mude para a **Aba 2 (`comparativo_linkage.html`)**.
2. No menu suspenso de datasets, selecione **"Ponte de Ruído (Efeito Chaining)"**.
3. A tela exibirá simultaneamente os 4 métodos nos 4 quadrantes (**Single**, **Complete**, **Average** e **Ward**) aplicados **exatamente sobre os mesmos pontos**.
4. **O que falar apontando para o Single Linkage (Quadrante Superior Esquerdo):**
   > *"Olhem com atenção para o Single Linkage. Temos duas galáxias imensas separadas, mas com 3 pontinhos de ruído no meio do caminho. O que o Single Linkage fez? Ele usou os pontos de ruído como uma ponte e fundiu as duas galáxias em um único grupo gigante! Isso se chama Efeito Chaining."*
5. **O que falar apontando para o Ward e o Complete (Quadrantes Inferiores):**
   > *"Agora olhem para o Complete e para o Ward: eles ignoraram a ponte e preservaram os dois blocos principais intactos, porque exigem coesão global ou diâmetro restrito."*
6. Aponte para a métrica de **CPCC** no rodapé de cada quadrante:
   * Mostre que o **Average** frequentemente atinge o maior valor de CPCC ($r > 0.90$), confirmando que ele preserva com maestria a distância média dos pares originais.

---

## 🎬 Ato 3: O Paradoxo Top-Down (`comparativo_divisivo.html`)
*Tempo sugerido: 2 a 3 minutos*

### Demonstrando o Algoritmo DIANA e o Bisecting K-Means
1. Mude para a **Aba 3 (`comparativo_divisivo.html`)**.
2. **O que falar:**
   > *"Até aqui, vimos tudo subindo das folhas para a raiz. Mas e se quisermos fatiar os dados de cima para baixo, como um escultor talhando mármore?"*
3. Clique no botão **"⏭️ Próximo Passo"**:
   * Uma linha de corte corta o espaço de dados.
   * O cluster raiz é dividido em dois.
4. Explique o quadrante do **DIANA**:
   > *"No DIANA, aquele ponto vermelho destacado foi o primeiro a se amotinar: era o ponto com maior distância média para todos os outros. Ele fundou o grupo dissidente e começou a atrair os vizinhos mais insatisfeitos."*
5. Explique o quadrante do **Bisecting K-Means**:
   > *"Já no Bisecting K-Means, o algoritmo localizou o cluster com maior variância e aplicou um K-Means com k=2. Em apenas 2 passos, temos nossos clusters principais, sem precisar gastar memória calculando a árvore até o nível de cada folha."*

---

## 🛡️ Dicas de Ouro para Lidar com Imprevistos

* **Se alguém perguntar:** *"Posso clicar e adicionar 100 pontos ao vivo?"*  
  * **Resposta:** *"Claro! O algoritmo recalcula tudo em JavaScript puro no navegador em tempo real, sem enviar nada para servidor algum."*
* **Se você errar um clique ou criar pontos demais:**  
  * Não se preocupe: basta clicar no botão vermelho **"Limpar"** ou recarregar um dos presets com um único clique.
* **Fechamento triunfal da demonstração:**  
  * Volte para os slides com `Alt + Tab` exatamente no slide de **Conclusão**.
