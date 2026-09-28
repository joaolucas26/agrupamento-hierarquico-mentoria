# Kit de Palestra: Agrupamento Hierárquico e Dendrogramas

Este repositório contém todo o material didático, scripts de validação matemática e ferramenta interativa para a sua palestra sobre **Agrupamento Hierárquico (Hierarchical Clustering)**.

---

## 📁 Estrutura dos Arquivos

| Arquivo | Descrição |
| :--- | :--- |
| 📄 [`AGRUPAMENTO_HIERARQUICO.md`](AGRUPAMENTO_HIERARQUICO.md) | **Roteiro completo da palestra**: Teoria formal, passo a passo matemático, fórmula de Lance-Williams, exemplo numérico manual resolvido, métodos de ligação (*Ward, Complete, Average, Single*), leitura do dendrograma, validação com CPCC e Silhueta, armadilhas comuns, roteiro sugerido de 45 min e Speaker Notes slide a slide. |
| 🌐 [`dendrograma_interativo.html`](dendrograma_interativo.html) | **Simulador Interativo Livre**: Ferramenta visual com adição de pontos com o mouse, alternância Top-Down vs Bottom-Up, dendrograma dinâmico e matriz de distâncias que se altera em tempo real com controle de avançar/voltar passos. |
| 🌐 [`comparativo_linkage.html`](comparativo_linkage.html) | **Comparativo de Linkage com Dados Fixados**: Painel em 4 quadrantes sincronizados comparando Single, Complete, Average e Ward simultaneamente no mesmo conjunto de pontos, com 5 datasets canônicos (Ponte/Chaining, 5 Pontos A-E, Outlier, Meias-Luas, Desbalanceado). |
| 🌐 [`comparativo_divisivo.html`](comparativo_divisivo.html) | **Comparativo Top-Down (Estratégia Divisiva)**: Painel em 4 quadrantes sincronizados comparando DIANA (*Splinter Group*), Bisecting K-Means, Furthest-Pair (*2-Medoids*) e PCA Hyperplane Split (*PDDP*), com visualização das fronteiras ativas e avanço passo a passo. |
| 🐍 [`validate_dendrogram.py`](validate_dendrogram.py) | **Script de Validação Matemática e Gráficos**: Varre cortes de $k$, calcula CPCC, Silhueta, Davies-Bouldin, Calinski-Harabasz e gera figuras em alta resolução (`dendrogram_comparativo.png`, `validacao_metricas_corte.png`, `efeito_chaining_comparativo.png`). |
| 🧪 [`test_dendrogram.py`](test_dendrogram.py) | **Suíte de Testes Automatizados (Pytest)**: Valida dimensões da matriz de ligação, monotonia das alturas, limites do CPCC, partições exatas em $k$, detecção do efeito chaining e impacto da padronização. |
| 🐍 [`agrupamento_hierarquico.py`](agrupamento_hierarquico.py) | Script complementar de demonstração e visualização com Scipy/Sklearn. |
| 🧪 [`test_dendrograma.py`](test_dendrograma.py) | Testes unitários adicionais cobrindo desigualdade ultramétrica e recuperação de partições canônicas. |
| 📦 [`requirements.txt`](requirements.txt) | Lista de bibliotecas Python necessárias (`numpy`, `scipy`, `matplotlib`, `scikit-learn`, `seaborn`). |


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
