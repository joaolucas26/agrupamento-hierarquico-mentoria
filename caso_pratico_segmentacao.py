"""
Estudo de Caso Prático: Segmentação de Clientes no E-commerce (RFM)
==================================================================
Este script aplica o Agrupamento Hierárquico a um problema real de negócios:
A análise RFM (Recência, Frequência, Valor Monetário) para segmentação de clientes.

Etapas do Pipeline:
1. Geração de base sintética realista de clientes (distribuição com assimetria positiva).
2. Tratamento com Log-Transform e Padronização Z-score (StandardScaler).
3. Agrupamento Hierárquico com Método de Ward.
4. Validação formal: Coeficiente Cofenético (CPCC) e Curva de Silhueta.
5. Determinação do corte ideal k.
6. Perfilamento de Negócio (Personas: Champions, Fiéis, Novos, Em Risco).
7. Exportação de Visualização em Heatmap Clustermap e Gráfico de Radar de Perfis.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, dendrogram, cophenet, fcluster
from scipy.spatial.distance import pdist
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score

# Configuração estética
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'


def gerar_dados_clientes_rfm(n_clientes=250, random_state=42):
    """
    Gera um dataset realista de RFM contendo 4 personas latentes no e-commerce:
    1. VIP / Champions: Baixa recência, altíssima frequência e alto ticket.
    2. Fiéis Recorrentes: Média/baixa recência, frequência consistente, ticket moderado.
    3. Novos Promissores: Recência baixíssima (comprou ontem), baixa frequência (1 compra), ticket variado.
    4. Em Risco / Churn: Alta recência (não compra há meses), frequência variada, ticket baixo/médio.
    """
    np.random.seed(random_state)
    
    # 1. VIP (15% da base)
    n_vip = int(n_clientes * 0.15)
    rec_vip = np.random.exponential(scale=10, size=n_vip) + 2
    freq_vip = np.random.poisson(lam=18, size=n_vip) + 10
    mon_vip = np.random.normal(loc=3500, scale=600, size=n_vip)
    
    # 2. Fiéis (35% da base)
    n_fieis = int(n_clientes * 0.35)
    rec_fieis = np.random.exponential(scale=25, size=n_fieis) + 15
    freq_fieis = np.random.poisson(lam=8, size=n_fieis) + 4
    mon_fieis = np.random.normal(loc=1200, scale=250, size=n_fieis)
    
    # 3. Novos Promissores (20% da base)
    n_novos = int(n_clientes * 0.20)
    rec_novos = np.random.uniform(low=1, high=12, size=n_novos)
    freq_novos = np.random.choice([1, 2], size=n_novos, p=[0.75, 0.25])
    mon_novos = np.random.normal(loc=450, scale=120, size=n_novos)
    
    # 4. Em Risco / Churn (30% da base)
    n_churn = n_clientes - (n_vip + n_fieis + n_novos)
    rec_churn = np.random.uniform(low=90, high=365, size=n_churn)
    freq_churn = np.random.poisson(lam=2, size=n_churn) + 1
    mon_churn = np.random.normal(loc=300, scale=100, size=n_churn)
    
    # Concatenação
    recencia = np.clip(np.concatenate([rec_vip, rec_fieis, rec_novos, rec_churn]), 1, 365)
    frequencia = np.clip(np.concatenate([freq_vip, freq_fieis, freq_novos, freq_churn]), 1, 50)
    monetario = np.clip(np.concatenate([mon_vip, mon_fieis, mon_novos, mon_churn]), 50, 10000)
    
    df = pd.DataFrame({
        'Cliente_ID': [f'CLI_{i:04d}' for i in range(1, n_clientes + 1)],
        'Recencia_Dias': np.round(recencia, 1),
        'Frequencia_Compras': frequencia.astype(int),
        'Valor_Monetario_R$': np.round(monetario, 2)
    })
    return df


def preprocessar_dados(df):
    """
    Em dados financeiros e de contagem (Frequência e Monetário), a assimetria é forte.
    Aplicamos log1p e em seguida StandardScaler para normalizar variâncias.
    """
    features = ['Recencia_Dias', 'Frequencia_Compras', 'Valor_Monetario_R$']
    X_raw = df[features].values
    
    # 1. Transformação Logarítmica para atenuar assimetria positiva
    X_log = np.log1p(X_raw)
    
    # 2. Padronização Z-Score
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_log)
    
    return X_scaled, scaler


def executar_segmentacao(df, X_scaled):
    """
    Executa o agrupamento hierárquico com método de Ward,
    avalia CPCC e determina o k ótimo via análise de silhueta.
    """
    print("\n[1] Calculando Matriz de Ligação (Método de Ward)...")
    Z = linkage(X_scaled, method='ward', metric='euclidean')
    
    # Coeficiente de Correlação Cofenética
    cpcc, _ = cophenet(Z, pdist(X_scaled))
    print(f"    - Coeficiente de Correlação Cofenética (CPCC): {cpcc:.4f}")
    
    # Avaliação por Silhueta para escolha de k
    print("\n[2] Avaliando métricas para diferentes valores de k:")
    melhor_k = 2
    melhor_sil = -1
    silhuetas = {}
    
    for k in range(2, 7):
        labels_teste = fcluster(Z, t=k, criterion='maxclust')
        sil = silhouette_score(X_scaled, labels_teste)
        db = davies_bouldin_score(X_scaled, labels_teste)
        silhuetas[k] = sil
        print(f"    * k = {k}: Silhueta = {sil:.4f} | Davies-Bouldin = {db:.4f}")
        if sil > melhor_sil:
            melhor_sil = sil
            melhor_k = k
            
    print(f"\n    >> Número ótimo de clusters selecionado: k = {melhor_k} (Silhueta = {melhor_sil:.4f})")
    
    # Atribuição definitiva dos clusters
    clusters_finais = fcluster(Z, t=melhor_k, criterion='maxclust')
    df['Cluster'] = clusters_finais
    
    return Z, melhor_k, df


def perfilar_clusters(df):
    """
    Interpreta os resultados do ponto de vista de negócios e cria as Personas de marketing.
    """
    print("\n[3] Perfil Médio de Negócios por Cluster:")
    resumo = df.groupby('Cluster').agg({
        'Cliente_ID': 'count',
        'Recencia_Dias': 'mean',
        'Frequencia_Compras': 'mean',
        'Valor_Monetario_R$': 'mean'
    }).rename(columns={'Cliente_ID': 'Qtd_Clientes'})
    
    resumo['%_Base'] = np.round((resumo['Qtd_Clientes'] / len(df)) * 100, 1)
    
    # Classificação semântica automática baseada nas médias
    personas = {}
    for c_id in resumo.index:
        rec = resumo.loc[c_id, 'Recencia_Dias']
        freq = resumo.loc[c_id, 'Frequencia_Compras']
        val = resumo.loc[c_id, 'Valor_Monetario_R$']
        
        if val > 2500 and freq > 12:
            personas[c_id] = "Champions / Clientes VIP"
        elif rec > 90 and freq <= 3:
            personas[c_id] = "Em Risco / Churn Iminente"
        elif rec < 15 and freq <= 2:
            personas[c_id] = "Novos Promissores"
        else:
            personas[c_id] = "Clientes Fiéis / Recorrentes"
            
    resumo['Persona_Sugerida'] = [personas.get(c, f"Cluster {c}") for c in resumo.index]
    print(resumo[['Qtd_Clientes', '%_Base', 'Recencia_Dias', 'Frequencia_Compras', 'Valor_Monetario_R$', 'Persona_Sugerida']].to_string())
    
    return resumo


def gerar_graficos_apresentacao(df, X_scaled, Z, melhor_k, output_dir="."):
    """
    Gera duas figuras em alta resolução prontas para os slides:
    1. Clustermap (Heatmap com dendrogramas nas linhas e colunas)
    2. Diagnóstico RFM com dispersão 3D projetada e barras médias
    """
    # 1. Clustermap Hierárquico
    df_scaled_plot = pd.DataFrame(X_scaled, columns=['Recência', 'Frequência', 'Monetário'])
    
    # Paleta de cores para os clusters
    paleta = sns.color_palette("Set2", melhor_k)
    cluster_cores = [paleta[c - 1] for c in df['Cluster']]
    
    g = sns.clustermap(
        df_scaled_plot,
        row_linkage=Z,
        col_cluster=False,
        row_colors=cluster_cores,
        cmap='vlag',
        figsize=(10, 8),
        cbar_pos=(0.02, 0.8, 0.03, 0.15),
        dendrogram_ratio=(0.25, 0.05)
    )
    g.fig.suptitle("Heatmap Hierárquico com Dendrograma (Segmentação RFM)", fontsize=14, fontweight='bold', y=1.02)
    caminho_clustermap = os.path.join(output_dir, "estudo_caso_rfm_clustermap.png")
    g.savefig(caminho_clustermap, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n[4] Clustermap salvo em: {caminho_clustermap}")
    
    # 2. Painel de Diagnóstico de Negócios
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Gráfico A: Recência vs Monetário
    sns.scatterplot(
        data=df,
        x='Recencia_Dias',
        y='Valor_Monetario_R$',
        hue='Cluster',
        palette='Set2',
        s=60,
        ax=axes[0]
    )
    axes[0].set_title("Recência vs. Valor Gasto (R$)", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Dias sem comprar (Recência)")
    axes[0].set_ylabel("Valor Monetário Total (R$)")
    
    # Gráfico B: Frequência vs Monetário
    sns.scatterplot(
        data=df,
        x='Frequencia_Compras',
        y='Valor_Monetario_R$',
        hue='Cluster',
        palette='Set2',
        s=60,
        ax=axes[1]
    )
    axes[1].set_title("Frequência de Compras vs. Valor Gasto (R$)", fontsize=12, fontweight='bold')
    axes[1].set_xlabel("Número de Compras Realizadas")
    axes[1].set_ylabel("Valor Monetário Total (R$)")
    
    # Gráfico C: Dendrograma com Linha de Corte
    altura_corte = (Z[-(melhor_k - 1), 2] + Z[-melhor_k, 2]) / 2.0
    dendrogram(
        Z,
        ax=axes[2],
        truncate_mode='lastp',
        p=25,
        color_threshold=altura_corte,
        leaf_rotation=90,
        leaf_font_size=8
    )
    axes[2].axhline(y=altura_corte, color='red', linestyle='--', linewidth=2, label=f"Corte ótimo k={melhor_k}")
    axes[2].set_title("Dendrograma de Ward com Ponto de Corte", fontsize=12, fontweight='bold')
    axes[2].set_xlabel("Amostras agrupadas")
    axes[2].set_ylabel("Distância de Ward")
    axes[2].legend(loc='upper right')
    
    plt.tight_layout()
    caminho_perfis = os.path.join(output_dir, "estudo_caso_rfm_perfis.png")
    plt.savefig(caminho_perfis, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"    Painel de Perfis salvo em: {caminho_perfis}")


def main():
    print("=" * 75)
    print(" ESTUDO DE CASO REAL: SEGMENTAÇÃO DE CLIENTES (RFM) VIA CLUSTERING HIERÁRQUICO")
    print("=" * 75)
    
    # 1. Gerar Dados
    df = gerar_dados_clientes_rfm(n_clientes=250, random_state=42)
    print(f"Base de clientes gerada: {len(df)} registros.")
    print("Primeiras 3 linhas da base:")
    print(df.head(3).to_string(index=False))
    
    # 2. Pré-processamento
    X_scaled, _ = preprocessar_dados(df)
    
    # 3. Modelagem e Corte
    Z, melhor_k, df_clusterizado = executar_segmentacao(df, X_scaled)
    
    # 4. Perfilamento de Negócio
    perfilar_clusters(df_clusterizado)
    
    # 5. Gráficos
    dir_atual = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else "."
    gerar_graficos_apresentacao(df_clusterizado, X_scaled, Z, melhor_k, output_dir=dir_atual)
    
    print("\n" + "=" * 75)
    print(" ESTUDO DE CASO EXECUTADO COM SUCESSO! IMAGENS PRONTAS PARA A PALESTRA.")
    print("=" * 75)


if __name__ == '__main__':
    main()
