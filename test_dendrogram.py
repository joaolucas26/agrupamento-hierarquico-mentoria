"""
Suíte de Testes Automatizados para Agrupamento Hierárquico e Dendrogramas
Autor: Material de Apoio para Palestra
Data: 2026

Executar via terminal:
    pytest test_dendrogram.py -v
"""

import pytest
import numpy as np
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, cophenet, fcluster
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from validate_dendrogram import generate_sample_data, compute_cophenetic_metrics, evaluate_cut_thresholds


@pytest.fixture
def sample_blobs():
    """Fixture com 50 amostras em 2D com 3 grupos bem separados."""
    X, y = generate_sample_data(n_samples=50, centers=3, random_state=42)
    return X, y


def test_linkage_matrix_dimensions(sample_blobs):
    """
    Propriedade Teórica:
    Para N observações, a matriz de fusão Z deve ter exatamente (N - 1) linhas e 4 colunas:
    [idx_cluster_1, idx_cluster_2, distancia, tamanho_do_novo_cluster].
    """
    X, _ = sample_blobs
    n = X.shape[0]

    for method in ['single', 'complete', 'average', 'ward']:
        Z = linkage(X, method=method)
        assert Z.shape == (n - 1, 4), f"A matriz Z para {method} deve ter shape ({n - 1}, 4)."
        # O cluster final (última linha) deve conter todas as N observações
        assert int(Z[-1, 3]) == n, f"O cluster final deve conter exatamente {n} observações."


def test_monotonic_heights_property(sample_blobs):
    """
    Propriedade Teórica (Ultra-métrica):
    Em Single, Complete, Average e Ward, as alturas de fusão (coluna 2 de Z)
    devem ser monotonicamente não-decrescentes: Z[i, 2] <= Z[i+1, 2].
    """
    X, _ = sample_blobs

    for method in ['single', 'complete', 'average', 'ward']:
        Z = linkage(X, method=method)
        heights = Z[:, 2]
        # Verifica se cada altura é maior ou igual à anterior (com tolerância numérica float)
        diffs = np.diff(heights)
        assert np.all(diffs >= -1e-12), f"Inversão de altura detectada no método {method}!"


def test_cophenetic_correlation_bounds(sample_blobs):
    """
    Propriedade Teórica:
    O Coeficiente de Correlação Cofenética (CPCC) deve estar no intervalo [-1, 1].
    Para dados com clusters nítidos, deve ser significativamente positivo (> 0.60).
    """
    X, _ = sample_blobs
    results = compute_cophenetic_metrics(X)

    for method, data in results.items():
        cpcc = data['cpcc']
        assert -1.0 <= cpcc <= 1.0, f"CPCC fora dos limites para {method}: {cpcc}"
        assert cpcc > 0.60, f"CPCC anomalamente baixo ({cpcc:.3f}) para dados nítidos em {method}"


def test_fcluster_cut_exact_k(sample_blobs):
    """
    Validação do Ponto de Corte:
    O corte com critério 'maxclust' para t=k deve retornar exatamente k rótulos distintos.
    """
    X, _ = sample_blobs
    Z = linkage(X, method='ward')

    for target_k in [2, 3, 4, 5]:
        labels = fcluster(Z, t=target_k, criterion='maxclust')
        unique_labels = np.unique(labels)
        assert len(unique_labels) == target_k, (
            f"Esperado {target_k} clusters, mas obteve {len(unique_labels)}."
        )


def test_chaining_effect_detection():
    """
    Demonstração da Fraqueza do Single Linkage:
    1. Fusão prematura: dois grupos distantes se fundem a uma altura muito baixa no Single Linkage
       devido à ponte de pontos intermediários (altura < 0.8), enquanto no Complete Linkage a fusão ocorre em altura alta (> 5.0).
    2. Com um outlier, Single Linkage prefere fundir os dois grupos gigantes pela ponte antes de fundir o outlier,
       gerando um cluster gigante e um singleton em k=2.
    """
    np.random.seed(42)
    # Dois grupos com 30 pontos cada
    g1 = np.random.randn(30, 2) * 0.3 + np.array([-3.0, 0.0])
    g2 = np.random.randn(30, 2) * 0.3 + np.array([3.0, 0.0])
    # Ponte estreita conectando
    bridge = np.column_stack([np.linspace(-2.2, 2.2, 8), np.random.randn(8) * 0.02])
    # Ponto periférico levemente afastado
    outlier = np.array([[0.0, 5.0]])
    X_bridge = np.vstack([g1, bridge, g2, outlier])

    Z_single = linkage(X_bridge, method='single')
    Z_ward = linkage(X_bridge, method='ward')
    Z_complete = linkage(X_bridge, method='complete')

    # Validação 1: Altura da fusão entre os dois grupos principais é drasticamente menor no Single
    # No Single, a ponte permite a união dos grupos por distâncias locais minúsculas
    bridge_max_step = np.max(np.diff(bridge[:, 0]))
    assert Z_single[-2, 2] < 1.0, "No Single Linkage a fusão dos dois blocos ocorre em altura baixa pela ponte."
    assert Z_complete[-1, 2] > 5.0, "No Complete Linkage a distância máxima entre blocos opostos é alta."

    # Validação 2: No corte k=2, Single Linkage agrupa ambos os blocos via ponte e deixa o outlier isolado (singleton)
    labels_single = fcluster(Z_single, t=2, criterion='maxclust')
    labels_ward = fcluster(Z_ward, t=2, criterion='maxclust')

    sizes_single = [np.sum(labels_single == 1), np.sum(labels_single == 2)]
    min_single = min(sizes_single)

    sizes_ward = [np.sum(labels_ward == 1), np.sum(labels_ward == 2)]
    min_ward = min(sizes_ward)

    # Single Linkage deixa 1 ponto isolado (singleton) pois a ponte encadeou tudo
    assert min_single == 1, f"Single Linkage deveria sofrer chaining e isolar o outlier em k=2 (obteve {min_single})."
    # Ward preserva grupos balanceados (ambos com dezenas de amostras)
    assert min_ward >= 28, f"Ward deveria manter clusters equilibrados (obteve {min_ward})."



def test_standardization_impact():
    """
    Armadilha da Palestra:
    Sem padronização, uma feature com variância 1000x maior monopoliza as distâncias.
    """
    np.random.seed(42)
    # Feature 1: pequena amplitude (0 a 1)
    f1 = np.random.uniform(0, 1, 40)
    # Feature 2: enorme amplitude (0 a 10.000)
    f2 = np.random.uniform(0, 10000, 40)
    X_raw = np.column_stack([f1, f2])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    dists_raw = pdist(X_raw)
    dists_scaled = pdist(X_scaled)

    # A correlação entre as distâncias nos dados brutos e a feature 2 isolada será quase 1.0,
    # demonstrando que a feature 1 foi completamente ignorada
    f2_dists = pdist(X_raw[:, 1].reshape(-1, 1))
    corr_f2 = np.corrcoef(dists_raw, f2_dists)[0, 1]

    assert corr_f2 > 0.999, "A variável de grande escala deve dominar totalmente a distância não-padronizada."
    
    # Com padronização, a influência é balanceada
    corr_scaled_f2 = np.corrcoef(dists_scaled, f2_dists)[0, 1]
    assert corr_scaled_f2 < 0.90, "A padronização deve restaurar o equilíbrio entre as variáveis."
