# Kit de Palestra: Agrupamento Hierárquico e Dendrogramas

Este repositório contém todo o material didático, scripts de validação matemática e ferramenta interativa para a sua palestra sobre **Agrupamento Hierárquico (Hierarchical Clustering)**.

---

## 📁 Estrutura dos Arquivos

| Arquivo | Descrição |
| :--- | :--- |
| 📊 [`SLIDES_PALESTRA.md`](SLIDES_PALESTRA.md) | **Slide Deck Pronto para Apresentação**: 25 slides formatados para Marp/HTML com notas do orador (*Speaker Notes*) minuto a minuto, cronometrado para 45 minutos. |
| 📄 [`AGRUPAMENTO_HIERARQUICO.md`](AGRUPAMENTO_HIERARQUICO.md) | **Roteiro teórico completo da palestra**: Teoria formal, passo a passo matemático, fórmula de Lance-Williams, métodos de ligação (*Ward, Complete, Average, Single*), leitura do dendrograma e validação. |
| 📄 [`ESTRATEGIA_DIVISIVA_TOP_DOWN.md`](ESTRATEGIA_DIVISIVA_TOP_DOWN.md) | **Guia da Estratégia Top-Down (Divisiva)**: A analogia de esculpir mármore, o desafio da explosão combinatória $2^{N-1}-1$, algoritmo DIANA (*Splinter Group*) com cálculo passo a passo resolvido à mão e Bisecting K-Means. |
| 🎬 [`LIVE_DEMO_PLAYBOOK.md`](LIVE_DEMO_PLAYBOOK.md) | **Playbook de Demonstração Ao Vivo**: Roteiro de 8 a 10 min explicando o que clicar e falar em cada aba interativa para criar momentos de impacto com a audiência. |
| ❓ [`FAQ_TECNICO_PALESTRA.md`](FAQ_TECNICO_PALESTRA.md) | **FAQ e Guia de Defesa**: As 6 perguntas mais difíceis da plateia técnica (Big Data, dados mistos de Gower, fenômeno de inversões, etc.) com respostas prontas. |
| 🛒 [`caso_pratico_segmentacao.py`](caso_pratico_segmentacao.py) | **Estudo de Caso Prático de Negócios (RFM)**: Segmentação real de e-commerce com Recência, Frequência e Monetário, gerando heatmap hierárquico (`clustermap`) e perfis de personas. |
| 🌐 [`dendrograma_interativo.html`](dendrograma_interativo.html) | **Simulador Interativo Livre**: Ferramenta visual com adição de pontos com o mouse, dendrograma dinâmico em SVG, linha de corte arrastável e animação de fusão passo a passo. |
| 🌐 [`comparativo_linkage.html`](comparativo_linkage.html) | **Comparativo de Linkage com Dados Fixados**: Painel em 4 quadrantes sincronizados comparando Single, Complete, Average e Ward simultaneamente sobre os mesmos pontos. |
| 🌐 [`comparativo_divisivo.html`](comparativo_divisivo.html) | **Comparativo Top-Down (Estratégia Divisiva)**: Painel em 4 quadrantes sincronizados comparando DIANA, Bisecting K-Means, Furthest-Pair e PDDP com avanço de passos. |
| 🐍 [`validate_dendrogram.py`](validate_dendrogram.py) | **Script de Validação Matemática e Gráficos**: Varre cortes de $k$, calcula CPCC, Silhueta, Davies-Bouldin e gera gráficos em alta definição. |
| 🧪 [`test_dendrograma.py`](test_dendrograma.py) | **Suíte de Testes Automatizados**: Valida axiomas matemáticos (Desigualdade Ultramétrica, monotonia, limites do CPCC e recuperação de clusters). |
| 📦 [`requirements.txt`](requirements.txt) | Lista de bibliotecas Python necessárias (`numpy`, `scipy`, `matplotlib`, `scikit-learn`, `pandas`, `seaborn`). |


---

## 🚀 Como Utilizar

### 1. Utilizando a Ferramenta Interativa na Palestra (`dendrograma_interativo.html`)
Basta dar um duplo clique no arquivo `dendrograma_interativo.html` para abri-lo em qualquer navegador (Google Chrome, Microsoft Edge, Firefox, Safari).
- **Sem servidor nem internet**: O arquivo funciona 100% offline.
- **Na apresentação**:
  1. Comece no preset **"3 Clusters Esféricos"** com o método **Ward** para mostrar a linha de corte e a relação direta com os clusters 2D.
  2. Mude para **"Efeito Chaining (Ponte)"** e alterne entre **Single Linkage** e **Complete Linkage** para chocar a plateia mostrando como um ponto intermediário une grupos distintos no Single Linkage.
  3. Clique em **"▶️ Assistir Fusão"** para mostrar didaticamente os pontos sendo unidos iteração por iteração.
  4. Mostre a métrica de **Correlação Cofenética (CPCC)** no rodapé variando de acordo com a ligação.

### 2. Executando os Scripts em Python

Para instalar as dependências em um ambiente virtual:
```bash
python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

Para gerar os gráficos comparativos e relatórios:
```bash
python agrupamento_hierarquico.py
```
Isso gerará as imagens:
- `comparativo_metodos_ligacao.png`: Visão lado a lado dos 4 métodos de ligação.
- `analise_detalhada_dendrograma.png`: Diagnóstico com dendrograma de corte, scatter 2D e curva de silhueta.

Para rodar os testes de validação matemática:
```bash
python test_dendrograma.py
```
ou via `pytest`:
```bash
pytest test_dendrograma.py -v
```

---

## 🎯 Destaques Conceituais para Enfatizar na Palestra

1. **A Filosofia:** Não impomos $k$ a priori; construímos toda a árvore de relações e decidimos a escala de observação a posteriori.
2. **A Padronização:** Distâncias geométricas exigem variáveis na mesma escala (`StandardScaler`).
3. **A Altura do Dendrograma:** O eixo Y mede a distância de fusão; o eixo X é apenas uma ordenação estética das folhas.
4. **O Efeito Chaining:** Single Linkage sofre com pontes de ruído entre clusters.
5. **A Validação Cofenética:** O dendrograma não é apenas um desenho; ele induz um espaço métrico ultramétrico ($d(x, z) \le \max(d(x, y), d(y, z))$) cuja fidelidade é medida pelo CPCC ($r > 0.85$).
