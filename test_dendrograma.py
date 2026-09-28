"""
Suíte de Testes Automatizados para Validação de Dendrogramas e Agrupamento Hierárquico
======================================================================================
Este arquivo contém testes unitários e matemáticos rigorosos para validar as propriedades
fundamentais de um dendrograma e do algoritmo aglomerativo:

1. Estrutura e dimensões da matriz de ligação Z ((N-1, 4))
2. Monotonia das alturas de fusão (não-inversão)
3. Satisfação da Desigualdade Ultramétrica nas distâncias cofenéticas:
      d_coph(x, z) <= max( d_coph(x, y), d_coph(y, z) )
4. Validade e limites do Coeficiente de Correlação Cofenética (CPCC)
5. Partição exata do espaço ao realizar cortes horizontais (fcluster)
6. Recuperação de clusters canônicos (Adjusted Rand Index = 1.0)
7. Validação da conservação de massa (tamanho do cluster raiz == N)

Pode ser executado com:
    python test_dendrograma.py
ou
    pytest test_dendrograma.py -v
"""

import unittest
import numpy as np
from scipy.cluster.hierarchy import linkage, cophenet, fcluster, to_tree
from scipy.spatial.distance import pdist, squareform
from sklearn.datasets import make_blobs
from sklearn.metrics import adjusted_rand_score


class TestDendrogramaEHierarquia(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Prepara datasets de teste controlados para as validações."""
        np.random.seed(42)
        # 1. Dataset com 30 pontos em 3 clusters bem separados
        cls.X_separado, cls.y_separado = make_blobs(
            n_samples=30,
            centers=[[-5, -5], [0, 5], [6, -2]],
            cluster_std=0.4,
            random_state=42
        )
        cls.n_samples = cls.X_separado.shape[0]
        
        # 2. Pequeno conjunto manual de 5 pontos 1D para verificação exata
        cls.X_pequeno = np.array([[1.0], [2.0], [4.5], [8.0], [9.0]])

    def test_01_estrutura_matriz_ligacao(self):
        """Valida se a matriz de ligação Z tem o formato exato (N-1, 4) e tipos corretos."""
        Z = linkage(self.X_separado, method='ward')
        
        # Dimensões esperadas: N-1 linhas e 4 colunas
        self.assertEqual(Z.shape, (self.n_samples - 1, 4), 
                         "A matriz Z deve ter formato (N-1, 4).")
        
        # O último cluster criado deve conter exatamente N amostras
        self.assertEqual(int(Z[-1, 3]), self.n_samples, 
                         "O nó raiz deve conter a soma de todas as amostras N.")
        
        # IDs dos clusters formados devem ser válidos (>= 0 e < 2*N - 1)
        todos_indices = np.concatenate([Z[:, 0], Z[:, 1]])
        self.assertTrue(np.all(todos_indices >= 0), "Índices de clusters não podem ser negativos.")
        self.assertTrue(np.all(todos_indices < 2 * self.n_samples - 1), "Índices ultrapassaram o limite da árvore.")

    def test_02_monotonia_das_alturas(self):
        """
        Valida a propriedade de Monotonia:
        Nos métodos Ward, Complete, Average e Single, as alturas de fusão
        devem ser não-decrescentes (h_{i} <= h_{i+1}).
        """
        metodos = ['ward', 'complete', 'average', 'single']
        for metodo in metodos:
            with self.subTest(metodo=metodo):
                Z = linkage(self.X_separado, method=metodo)
                alturas = Z[:, 2]
                
                # Verifica se a diferença consecutiva é sempre >= -1e-9 (tolerância numérica)
                diferencas = np.diff(alturas)
                self.assertTrue(
                    np.all(diferencas >= -1e-9),
                    f"Método '{metodo}' violou a monotonia das alturas! Inversão detectada."
                )

    def test_03_desigualdade_ultrametrica(self):
        """
        TEOREMA FUNDAMENTAL DO DENDROGRAMA:
        A matriz de distâncias cofenéticas induzida por um dendrograma
        DEVE ser um espaço ultramétrico estrito:
            d_coph(x, z) <= max( d_coph(x, y), d_coph(y, z) ) + epsilon
        para quaisquer três pontos x, y, z.
        """
        Z = linkage(self.X_separado, method='average')
        _, coph_dists = cophenet(Z, pdist(self.X_separado))
        
        # Transforma o vetor condensado em matriz quadrada N x N
        matriz_coph = squareform(coph_dists)
        n = matriz_coph.shape[0]
        
        # Testar para uma amostra representativa de tripletos (i, j, k)
        tolerancia = 1e-7
        violacoes = 0
        amostras_testadas = 0
        
        for i in range(min(n, 15)):
            for j in range(i + 1, min(n, 15)):
                for k in range(j + 1, min(n, 15)):
                    d_ij = matriz_coph[i, j]
                    d_jk = matriz_coph[j, k]
                    d_ik = matriz_coph[i, k]
                    
                    # Checa as 3 permutações da desigualdade ultramétrica
                    cond1 = d_ik <= max(d_ij, d_jk) + tolerancia
                    cond2 = d_ij <= max(d_ik, d_jk) + tolerancia
                    cond3 = d_jk <= max(d_ij, d_ik) + tolerancia
                    
                    if not (cond1 and cond2 and cond3):
                        violacoes += 1
                    amostras_testadas += 1
                    
        self.assertEqual(violacoes, 0, 
                         f"Houve {violacoes} violações da desigualdade ultramétrica no dendrograma!")

    def test_04_limites_correlacao_cofenetica_cpcc(self):
        """Valida se o CPCC está dentro do intervalo [-1, 1] e se Average Linkage tem alta fidelidade."""
        Z_avg = linkage(self.X_separado, method='average')
        Z_ward = linkage(self.X_separado, method='ward')
        
        cpcc_avg, _ = cophenet(Z_avg, pdist(self.X_separado))
        cpcc_ward, _ = cophenet(Z_ward, pdist(self.X_separado))
        
        # CPCC é coeficiente de Pearson: deve estar em [-1, 1]
        self.assertTrue(-1.0 <= cpcc_avg <= 1.0, "CPCC de Average fora do intervalo [-1, 1]")
        self.assertTrue(-1.0 <= cpcc_ward <= 1.0, "CPCC de Ward fora do intervalo [-1, 1]")
        
        # Em clusters bem definidos, CPCC deve ser significativamente positivo
        self.assertGreater(cpcc_avg, 0.70, "CPCC do Average Linkage deveria ser alto (>0.70) para dados em clusters.")

    def test_05_coerencia_de_corte_fcluster(self):
        """
        Valida que ao cortar a árvore solicitando k clusters (criterion='maxclust'),
        o número retornado de rótulos únicos seja EXATAMENTE k.
        """
        Z = linkage(self.X_separado, method='ward')
        
        for k_desejado in [2, 3, 4, 5, 8]:
            with self.subTest(k=k_desejado):
                labels = fcluster(Z, t=k_desejado, criterion='maxclust')
                n_clusters_obtidos = len(np.unique(labels))
                self.assertEqual(
                    n_clusters_obtidos, k_desejado,
                    f"Esperado {k_desejado} clusters, mas fcluster retornou {n_clusters_obtidos}."
                )
                # Verifica que todas as amostras foram associadas a um cluster
                self.assertEqual(len(labels), self.n_samples, "Tamanho dos rótulos não bate com o número de amostras.")

    def test_06_recuperacao_clusters_canonicos(self):
        """
        Valida que o agrupamento hierárquico (Ward) recupera perfeitamente (ARI = 1.0)
        os clusters sintéticos bem separados.
        """
        Z = linkage(self.X_separado, method='ward')
        labels = fcluster(Z, t=3, criterion='maxclust')
        
        ari = adjusted_rand_score(self.y_separado, labels)
        self.assertAlmostEqual(ari, 1.0, places=5, 
                               msg=f"O agrupamento deveria ter recuperado 100% dos clusters (ARI={ari:.4f}).")

    def test_07_pequeno_exemplo_analitico(self):
        """
        Validação analítica com pontos 1D simples: [1.0, 2.0, 4.5, 8.0, 9.0]
        - A primeira fusão DEVE ser entre 1.0 e 2.0 (distância = 1.0)
          ou entre 8.0 e 9.0 (distância = 1.0).
        """
        Z = linkage(self.X_pequeno, method='single')
        primeira_dist = Z[0, 2]
        self.assertAlmostEqual(primeira_dist, 1.0, places=4,
                               msg=f"A menor distância inicial deveria ser 1.0, obtido {primeira_dist}.")


def executar_testes_com_relatorio():
    """Executa a suíte de testes e imprime um relatório amigável no terminal."""
    print("=" * 70)
    print(" EXECUTANDO BATERIA DE TESTES DE VALIDAÇÃO DO DENDROGRAMA")
    print("=" * 70)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDendrogramaEHierarquia)
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    print("\n" + "=" * 70)
    if resultado.wasSuccessful():
        print(" [SUCESSO] Todos os testes passaram com êxito!")
        print(" O dendrograma atende rigorosamente a todos os axiomas matemáticos:")
        print("   - Dimensão e conservação de massa do nó raiz;")
        print("   - Monotonia das distâncias de fusão;")
        print("   - Satisfação da desigualdade ultramétrica;")
        print("   - Consistência dos cortes de partição e correlação cofenética.")
    else:
        print(f" [FALHA] {len(resultado.failures)} falhas e {len(resultado.errors)} erros encontrados.")
    print("=" * 70)
    return resultado.wasSuccessful()


if __name__ == '__main__':
    executar_testes_com_relatorio()
