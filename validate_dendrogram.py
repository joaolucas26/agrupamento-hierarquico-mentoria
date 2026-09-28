"""
Script de Validação Matemática e Geração de Gráficos para Agrupamento Hierárquico
Autor: Material de Apoio para Palestra
Data: 2026

Este script realiza:
1. Comparação de métodos de ligação (Single, Complete, Average, Ward) via Coeficiente de Correlação Cofenética (CPCC).
2. Avaliação de cortes no dendrograma usando Silhueta, Davies-Bouldin e Calinski-Harabasz.
3. Demonstração do efeito Chaining (encadeamento) no Single Linkage.
4. Exportação de figuras de alta resolução (300 DPI) para uso em slides de apresentação.
"""

import os
import sys

# Garante suporte a UTF-8 no terminal Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram, cophenet, fcluster
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score



def generate_sample_data(n_samples=60, centers=3, random_state=42):
    """Gera dados sintéticos padronizados com múltiplos centros."""
    X, y_true = make_blobs(
        n_samples=n_samples,
        centers=centers,
        cluster_std=0.85,
        random_state=random_state
    )
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, y_true


def compute_cophenetic_metrics(X, metric='euclidean'):
    """
    Calcula o Coeficiente de Correlação Cofenética (CPCC) para os quatro principais métodos.
    Retorna dicionário com matrizes de ligação Z e scores CPCC.
    """
    methods = ['single', 'complete', 'average', 'ward']
    results = {}
    dists = pdist(X, metric=metric)

    for method in methods:
        Z = linkage(X, method=method, metric=metric)
        coph_corr, _ = cophenet(Z, dists)
        results[method] = {
            'linkage_matrix': Z,
            'cpcc': float(coph_corr)
        }
    return results


def evaluate_cut_thresholds(X, Z, k_range=range(2, 9)):
    """
    Avalia a qualidade dos agrupamentos variando o número de clusters k.
    Calcula Silhueta, Davies-Bouldin e Calinski-Harabasz.
    """
    metrics = {
        'k': [],
        'silhouette': [],
        'davies_bouldin': [],
        'calinski_harabasz': []
    }

    for k in k_range:
        labels = fcluster(Z, t=k, criterion='maxclust')
        if len(np.unique(labels)) > 1:
            metrics['k'].append(k)
            metrics['silhouette'].append(silhouette_score(X, labels))
            metrics['davies_bouldin'].append(davies_bouldin_score(X, labels))
            metrics['calinski_harabasz'].append(calinski_harabasz_score(X, labels))

    return metrics


def plot_comparative_dendrograms(X, results, output_file='dendrogram_comparativo.png'):
    """Gera visualização 2x2 comparando os 4 métodos de ligação e seus CPCCs."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor('#ffffff')

    method_titles = {
        'single': 'Single Linkage (Vizinho Mais Próximo)',
        'complete': 'Complete Linkage (Vizinho Mais Distante)',
        'average': 'Average Linkage (Média UPGMA)',
        'ward': "Ward's Method (Mínima Variância)"
    }

    for ax, (method, data) in zip(axes.flat, results.items()):
        Z = data['linkage_matrix']
        cpcc = data['cpcc']
        
        dendrogram(
            Z,
            ax=ax,
            truncate_mode='lastp',
            p=25,
            leaf_rotation=45,
            leaf_font_size=9,
            show_contracted=True,
            color_threshold=0.6 * np.max(Z[:, 2])
        )
        
        ax.set_title(
            f"{method_titles[method]}\nCPCC (Correlação Cofenética) = {cpcc:.3f}",
            fontsize=12,
            fontweight='bold',
            pad=10
        )
        ax.set_xlabel("Índices das Amostras / Subclusters agregados", fontsize=10)
        ax.set_ylabel("Distância / Dissimilaridade", fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.suptitle(
        "Comparativo de Métodos de Ligação e Preservação Estrutural (CPCC)",
        fontsize=15,
        fontweight='bold',
        y=0.99
    )
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Grafico gerado: {output_file}")


def plot_metrics_curves(metrics, output_file='validacao_metricas_corte.png'):
    """Gera curvas de Silhueta, Davies-Bouldin e Calinski-Harabasz variando k."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor('#ffffff')
    k = metrics['k']

    # 1. Silhueta (Maior é melhor)
    ax1 = axes[0]
    ax1.plot(k, metrics['silhouette'], marker='o', color='#2563eb', linewidth=2.5, markersize=8)
    best_k_sil = k[np.argmax(metrics['silhouette'])]
    ax1.axvline(best_k_sil, color='#dc2626', linestyle='--', alpha=0.7, label=f'Ótimo (k={best_k_sil})')
    ax1.set_title("Coeficiente de Silhueta\n(Maior é melhor ↑)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Número de Clusters (k)", fontsize=11)
    ax1.set_ylabel("Silhueta Média", fontsize=11)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='lower right')

    # 2. Davies-Bouldin (Menor é melhor)
    ax2 = axes[1]
    ax2.plot(k, metrics['davies_bouldin'], marker='s', color='#059669', linewidth=2.5, markersize=8)
    best_k_db = k[np.argmin(metrics['davies_bouldin'])]
    ax2.axvline(best_k_db, color='#dc2626', linestyle='--', alpha=0.7, label=f'Ótimo (k={best_k_db})')
    ax2.set_title("Índice Davies-Bouldin\n(Menor é melhor ↓)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Número de Clusters (k)", fontsize=11)
    ax2.set_ylabel("Índice DB", fontsize=11)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right')

    # 3. Calinski-Harabasz (Maior é melhor)
    ax3 = axes[2]
    ax3.plot(k, metrics['calinski_harabasz'], marker='^', color='#7c3aed', linewidth=2.5, markersize=8)
    best_k_ch = k[np.argmax(metrics['calinski_harabasz'])]
    ax3.axvline(best_k_ch, color='#dc2626', linestyle='--', alpha=0.7, label=f'Ótimo (k={best_k_ch})')
    ax3.set_title("Índice Calinski-Harabasz\n(Maior é melhor ↑)", fontsize=12, fontweight='bold')
    ax3.set_xlabel("Número de Clusters (k)", fontsize=11)
    ax3.set_ylabel("Índice CH", fontsize=11)
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend(loc='lower right')

    plt.suptitle("Validação Quantitativa do Ponto de Corte (k)", fontsize=15, fontweight='bold', y=1.03)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Grafico gerado: {output_file}")


def demonstrate_chaining_effect(output_file='efeito_chaining_comparativo.png'):
    """
    Demonstra visualmente o efeito Chaining (encadeamento por ponte de ruído)
    comparando Single Linkage vs Ward Linkage para corte k=2.
    """
    np.random.seed(42)
    # Grupo 1 (Esquerda)
    c1 = np.random.randn(35, 2) * 0.4 + np.array([-2.5, 0.0])
    # Grupo 2 (Direita)
    c2 = np.random.randn(35, 2) * 0.4 + np.array([2.5, 0.0])
    # Ponte de ruído conectando os dois
    bridge_x = np.linspace(-1.8, 1.8, 6)
    bridge_y = np.random.randn(6) * 0.05
    bridge = np.column_stack([bridge_x, bridge_y])

    X_bridge = np.vstack([c1, bridge, c2])

    # Single Linkage
    Z_single = linkage(X_bridge, method='single')
    labels_single = fcluster(Z_single, t=2, criterion='maxclust')

    # Ward Linkage
    Z_ward = linkage(X_bridge, method='ward')
    labels_ward = fcluster(Z_ward, t=2, criterion='maxclust')

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    fig.patch.set_facecolor('#ffffff')

    # Plot Single Linkage
    scatter1 = axes[0].scatter(
        X_bridge[:, 0], X_bridge[:, 1],
        c=labels_single, cmap='Set1', s=55, edgecolor='k', alpha=0.85
    )
    axes[0].set_title(
        "Single Linkage (k = 2)\nFalha pelo Efeito Chaining: Ponte une os dois grupos!",
        fontsize=12, fontweight='bold', color='#b91c1c'
    )
    axes[0].set_xlabel("Feature 1")
    axes[0].set_ylabel("Feature 2")
    axes[0].grid(True, linestyle='--', alpha=0.5)

    # Plot Ward Linkage
    scatter2 = axes[1].scatter(
        X_bridge[:, 0], X_bridge[:, 1],
        c=labels_ward, cmap='coolwarm', s=55, edgecolor='k', alpha=0.85
    )
    axes[1].set_title(
        "Ward's Method (k = 2)\nRobusto ao Ruído: Divide em dois aglomerados compactos",
        fontsize=12, fontweight='bold', color='#15803d'
    )
    axes[1].set_xlabel("Feature 1")
    axes[1].set_ylabel("Feature 2")
    axes[1].grid(True, linestyle='--', alpha=0.5)

    plt.suptitle("O Perigo do Efeito Chaining (Single vs. Ward)", fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Grafico gerado: {output_file}")


def main():
    print("=" * 65)
    print("   VALIDAÇÃO MATEMÁTICA DE AGRUPAMENTO HIERÁRQUICO")
    print("=" * 65)

    # 1. Gerar dados
    X, _ = generate_sample_data(n_samples=80, centers=3, random_state=42)
    print(f"\n[+] Dados gerados com sucesso: {X.shape[0]} amostras em {X.shape[1]} dimensões.")

    # 2. Avaliar CPCC
    print("\n[+] Calculando Coeficiente de Correlação Cofenética (CPCC)...")
    results = compute_cophenetic_metrics(X)

    print("\n" + "-" * 50)
    print(f"{'Método de Ligação':<20} | {'CPCC (Pearson r)':<18} | {'Avaliação':<12}")
    print("-" * 50)
    for method, data in results.items():
        cpcc = data['cpcc']
        if cpcc >= 0.85:
            eval_str = "Excelente (Alto)"
        elif cpcc >= 0.75:
            eval_str = "Bom (Aceitável)"
        else:
            eval_str = "Distorcido (Baixo)"
        print(f"{method.capitalize():<20} | {cpcc:.4f}{'':<12} | {eval_str:<12}")
    print("-" * 50)

    # 3. Avaliar Cortes para o Método Ward
    print("\n[+] Avaliando Métricas de Corte (k = 2 a 8) para Ward's Method...")
    Z_ward = results['ward']['linkage_matrix']
    metrics = evaluate_cut_thresholds(X, Z_ward, k_range=range(2, 9))

    print("\n" + "-" * 62)
    print(f"{'k':<6} | {'Silhueta (Maior)':<17} | {'Davies-Bouldin (Menor)':<22} | {'Calinski-Harabasz (Maior)'}")
    print("-" * 62)
    for i, k in enumerate(metrics['k']):
        print(
            f"{k:<6} | {metrics['silhouette'][i]:<17.4f} | "
            f"{metrics['davies_bouldin'][i]:<22.4f} | "
            f"{metrics['calinski_harabasz'][i]:.2f}"
        )
    print("-" * 62)

    # 4. Gerar Figuras para a Palestra
    print("\n[+] Gerando figuras de alta resolução para a apresentação...")
    plot_comparative_dendrograms(X, results, output_file='dendrogram_comparativo.png')
    plot_metrics_curves(metrics, output_file='validacao_metricas_corte.png')
    demonstrate_chaining_effect(output_file='efeito_chaining_comparativo.png')

    print("\n[SUCESSO] Todos os gráficos e validações foram concluídos com êxito!")
    print("Arquivos prontos para inserir nos slides:")
    print(" - dendrogram_comparativo.png")
    print(" - validacao_metricas_corte.png")
    print(" - efeito_chaining_comparativo.png")
    print("=" * 65)


if __name__ == '__main__':
    main()
