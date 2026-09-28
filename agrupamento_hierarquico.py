"""
Agrupamento Hierárquico - Script de Demonstração, Validação e Visualização
==========================================================================
Este script implementa e demonstra o pipeline completo de Agrupamento Hierárquico:
1. Geração e normalização de dados sintéticos com estrutura natural de clusters
2. Cálculo de matrizes de ligação para múltiplos métodos (Ward, Complete, Average, Single)
3. Avaliação da fidelidade do dendrograma via Coeficiente de Correlação Cofenética (CPCC)
4. Análise de métricas de validação intrínseca (Silhueta, Davies-Bouldin, Calinski-Harabasz)
5. Determinação do corte ideal (método do maior salto vertical e pico de silhueta)
6. Exportação de gráficos didáticos em alta resolução para apresentação
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, cophenet, fcluster
from scipy.spatial.distance import pdist, squareform
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

# Configuração de estilo para os gráficos
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8


def gerar_dados(n_samples=120, centers=4, cluster_std=0.85, random_state=42):
    """
    Gera dados sintéticos multivariados e aplica padronização Z-score.
    Retorna os dados brutos e padronizados com seus rótulos reais.
    """
    X_raw, y_real = make_blobs(
        n_samples=n_samples,
        centers=centers,
        cluster_std=cluster_std,
        random_state=random_state
    )
    # Padronização obrigatória em clustering baseado em distâncias
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    return X_raw, X_scaled, y_real


def calcular_correlacao_cofenetica(X, Z):
    """
    Calcula o Coeficiente de Correlação Cofenética (CPCC).
    Mede a correlação de Pearson entre as distâncias euclidianas originais
    e as distâncias representadas no dendrograma (distâncias cofenéticas).
    """
    cpcc, _ = cophenet(Z, pdist(X))
    return cpcc


def analisar_saltos_distancia(Z, top_n=5):
    """
    Analisa os maiores saltos (acelerações) entre fusões consecutivas no dendrograma.
    O maior salto frequentemente indica o ponto natural de corte.
    """
    distancias = Z[:, 2]
    saltos = np.diff(distancias)
    indices_ordenados = np.argsort(saltos)[::-1]
    
    resultados = []
    n = len(distancias) + 1
    for idx in indices_ordenados[:top_n]:
        k_clusters = n - (idx + 1)
        salto_valor = saltos[idx]
        altura_corte = (distancias[idx] + distancias[idx + 1]) / 2.0
        resultados.append({
            'k_clusters': k_clusters,
            'salto': salto_valor,
            'altura_corte': altura_corte,
            'posicao_fusao': idx
        })
    return resultados


def avaliar_metricas_por_k(X, Z, k_min=2, k_max=8):
    """
    Avalia a qualidade dos clusters obtidos ao cortar o dendrograma
    em diferentes números de clusters k.
    """
    metricas = {
        'k': [],
        'silhouette': [],
        'davies_bouldin': [],
        'calinski_harabasz': []
    }
    
    for k in range(k_min, k_max + 1):
        labels = fcluster(Z, t=k, criterion='maxclust')
        # Verifica se temos ao menos 2 clusters distintos
        if len(np.unique(labels)) > 1:
            metricas['k'].append(k)
            metricas['silhouette'].append(silhouette_score(X, labels))
            metricas['davies_bouldin'].append(davies_bouldin_score(X, labels))
            metricas['calinski_harabasz'].append(calinski_harabasz_score(X, labels))
            
    return metricas


def plotar_comparativo_metodos(X, metodos=['ward', 'complete', 'average', 'single'], output_path="comparativo_metodos_ligacao.png"):
    """
    Compara 4 métodos de ligação lado a lado:
    - Linha superior: Dendrograma com valor do CPCC
    - Linha inferior: Projeção 2D com coloração dos clusters (k=4)
    """
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    k_alvo = 4
    
    cores_clusters = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, metodo in enumerate(metodos):
        Z = linkage(X, method=metodo, metric='euclidean')
        cpcc = calcular_correlacao_cofenetica(X, Z)
        
        # 1. Dendrograma
        ax_dendro = axes[0, i]
        dendro = dendrogram(
            Z,
            ax=ax_dendro,
            truncate_mode='lastp',
            p=25,
            show_leaf_counts=True,
            leaf_rotation=90,
            leaf_font_size=8,
            color_threshold=Z[-(k_alvo - 1), 2] if k_alvo > 1 else 0
        )
        ax_dendro.set_title(f"Método: {metodo.capitalize()}\nCPCC = {cpcc:.4f}", fontsize=12, fontweight='bold')
        ax_dendro.set_xlabel("Índice da Amostra / (Tamanho do Cluster)")
        if i == 0:
            ax_dendro.set_ylabel("Distância de Fusão (Altura)")
            
        # 2. Scatter plot 2D com clusters resultantes
        ax_scatter = axes[1, i]
        labels = fcluster(Z, t=k_alvo, criterion='maxclust')
        sil = silhouette_score(X, labels)
        
        for c_idx, cluster_id in enumerate(np.unique(labels)):
            mask = labels == cluster_id
            ax_scatter.scatter(
                X[mask, 0], X[mask, 1],
                label=f"C{cluster_id}",
                color=cores_clusters[c_idx % len(cores_clusters)],
                alpha=0.75,
                edgecolors='none',
                s=40
            )
            
        ax_scatter.set_title(f"Clusters para k={k_alvo}\nSilhueta = {sil:.3f}", fontsize=11)
        ax_scatter.set_xlabel("Feature 1 (Padronizada)")
        if i == 0:
            ax_scatter.set_ylabel("Feature 2 (Padronizada)")
        ax_scatter.legend(loc='upper right', fontsize=8)
        
    plt.suptitle("Comparação de Métodos de Ligação no Agrupamento Hierárquico", fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Gráfico comparativo salvo em: {output_path}")


def plotar_analise_detalhada(X, Z_ward, k_escolhido=4, output_path="analise_detalhada_dendrograma.png"):
    """
    Gera um dashboard de diagnóstico detalhado com 3 painéis:
    1. Dendrograma com linha de corte horizontal evidente
    2. Espaço de características 2D com centróides e envelopes
    3. Gráficos de Silhueta e Salto de Distância por k
    """
    fig = plt.figure(figsize=(18, 6))
    
    # 1. Dendrograma com Linha de Corte
    ax1 = fig.add_subplot(1, 3, 1)
    altura_corte = Z_ward[-(k_escolhido - 1), 2]
    # Pega um valor ligeiramente abaixo para o threshold de cor
    threshold_valor = (Z_ward[-(k_escolhido - 1), 2] + Z_ward[-k_escolhido, 2]) / 2.0
    
    dendrogram(
        Z_ward,
        ax=ax1,
        truncate_mode='lastp',
        p=30,
        color_threshold=threshold_valor,
        leaf_rotation=90,
        leaf_font_size=8
    )
    ax1.axhline(y=threshold_valor, color='red', linestyle='--', linewidth=2, label=f"Corte: k={k_escolhido} (h={threshold_valor:.2f})")
    ax1.set_title(f"Dendrograma de Ward com Linha de Corte\n(k = {k_escolhido})", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Amostras agrupadas")
    ax1.set_ylabel("Distância de Ligação (Ward)")
    ax1.legend(loc='upper right')
    
    # 2. Visualização dos Clusters 2D
    ax2 = fig.add_subplot(1, 3, 2)
    labels = fcluster(Z_ward, t=k_escolhido, criterion='maxclust')
    cores = ['#2b5c8f', '#d95f02', '#7570b3', '#1b9e77', '#e7298a']
    
    for idx, c in enumerate(np.unique(labels)):
        pontos = X[labels == c]
        ax2.scatter(pontos[:, 0], pontos[:, 1], color=cores[idx % len(cores)], label=f'Cluster {c} ({len(pontos)} pts)', s=45, alpha=0.8)
        # Plota o centroide
        centroide = pontos.mean(axis=0)
        ax2.scatter(centroide[0], centroide[1], marker='X', color='black', s=120, edgecolors='white', linewidth=1.5)
        
    ax2.set_title(f"Partição 2D Resultante (k = {k_escolhido})\n(X marca o centróide)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Variável X1 (Padronizada)")
    ax2.set_ylabel("Variável X2 (Padronizada)")
    ax2.legend(loc='lower right', fontsize=9)
    
    # 3. Curva de Métricas de Validação (Silhueta vs k)
    ax3 = fig.add_subplot(1, 3, 3)
    metricas = avaliar_metricas_por_k(X, Z_ward, k_min=2, k_max=8)
    
    ax3.plot(metricas['k'], metricas['silhouette'], marker='o', linewidth=2.5, color='#1f77b4', label='Coeficiente de Silhueta')
    # Destaca o ponto ótimo
    best_idx = np.argmax(metricas['silhouette'])
    best_k = metricas['k'][best_idx]
    best_sil = metricas['silhouette'][best_idx]
    ax3.scatter([best_k], [best_sil], color='red', s=120, zorder=5, label=f'Pico em k={best_k} ({best_sil:.3f})')
    
    ax3.set_title("Critério de Seleção de k:\nCoeficiente de Silhueta", fontsize=12, fontweight='bold')
    ax3.set_xlabel("Número de Clusters (k)")
    ax3.set_ylabel("Score de Silhueta Médio")
    ax3.set_xticks(metricas['k'])
    ax3.legend(loc='lower left', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Painel detalhado salvo em: {output_path}")


def executar_pipeline():
    """
    Função principal que orquestra toda a execução e imprime o relatório no terminal.
    """
    print("=" * 70)
    print(" PIPELINE DE VALIDAÇÃO E ANÁLISE DE AGRUPAMENTO HIERÁRQUICO")
    print("=" * 70)
    
    # 1. Gerar dados
    print("\n1. Gerando conjunto de dados sintéticos...")
    _, X, y_real = gerar_dados(n_samples=120, centers=4, cluster_std=0.85, random_state=42)
    print(f"   - Total de amostras: {X.shape[0]}")
    print(f"   - Dimensões: {X.shape[1]}")
    print(f"   - Média após StandardScaler: {X.mean(axis=0).round(4)}")
    print(f"   - Desvio padrão após StandardScaler: {X.std(axis=0).round(4)}")
    
    # 2. Comparativo de Métodos de Ligação e CPCC
    print("\n2. Avaliando Coeficiente de Correlação Cofenética (CPCC) por método:")
    metodos = ['ward', 'complete', 'average', 'single']
    linkages = {}
    cpccs = {}
    
    for m in metodos:
        Z = linkage(X, method=m, metric='euclidean')
        linkages[m] = Z
        c = calcular_correlacao_cofenetica(X, Z)
        cpccs[m] = c
        qualidade = "Excelente (>0.85)" if c > 0.85 else ("Boa (0.75-0.85)" if c > 0.75 else "Razoável/Baixa (<0.75)")
        print(f"   * {m.capitalize():<10} -> CPCC = {c:.4f} ({qualidade})")
        
    melhor_metodo_cpcc = max(cpccs, key=cpccs.get)
    print(f"\n   >> Método com maior fidelidade métrica (maior CPCC): {melhor_metodo_cpcc.upper()}")
    
    # 3. Análise de Saltos no Método de Ward
    print("\n3. Análise de Maiores Saltos de Fusão (Método de Ward):")
    saltos = analisar_saltos_distancia(linkages['ward'], top_n=3)
    for s in saltos:
        print(f"   - Corte sugerido para k={s['k_clusters']}: Salto de distância = {s['salto']:.4f} (Altura = {s['altura_corte']:.2f})")
        
    # 4. Avaliação por Silhueta
    print("\n4. Avaliação de Métricas por k (Método de Ward):")
    metricas = avaliar_metricas_por_k(X, linkages['ward'], k_min=2, k_max=6)
    for k, sil, db, ch in zip(metricas['k'], metricas['silhouette'], metricas['davies_bouldin'], metricas['calinski_harabasz']):
        print(f"   - k = {k}: Silhueta = {sil:.4f} | Davies-Bouldin = {db:.4f} (menor=melhor) | Calinski-Harabasz = {ch:.1f} (maior=melhor)")
        
    best_k = metricas['k'][np.argmax(metricas['silhouette'])]
    print(f"\n   >> Número ótimo de clusters recomendado pela Silhueta: k = {best_k}")
    
    # 5. Gerar e salvar gráficos
    print("\n5. Gerando gráficos de alta resolução para apresentação...")
    dir_atual = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else "."
    caminho_comparativo = os.path.join(dir_atual, "comparativo_metodos_ligacao.png")
    caminho_detalhado = os.path.join(dir_atual, "analise_detalhada_dendrograma.png")
    
    plotar_comparativo_metodos(X, metodos=metodos, output_path=caminho_comparativo)
    plotar_analise_detalhada(X, linkages['ward'], k_escolhido=best_k, output_path=caminho_detalhado)
    
    print("\n" + "=" * 70)
    print(" PIPELINE CONCLUÍDO COM SUCESSO!")
    print(f" Arquivos gerados:")
    print(f" 1. {caminho_comparativo}")
    print(f" 2. {caminho_detalhado}")
    print("=" * 70)


if __name__ == "__main__":
    executar_pipeline()
