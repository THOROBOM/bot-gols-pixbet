# reports.py
import pandas as pd
from database import load_bets

# As funções de terminal foram removidas para focar na aplicação web.
# Podemos adicioná-las de volta se necessário.

def get_dashboard_data():
    """Calcula e retorna todas as métricas avançadas para o dashboard web."""
    bets = load_bets()
    if not bets:
        return None # Retorna None se não houver dados

    # Converte a lista de dicionários para um DataFrame do Pandas
    df = pd.DataFrame(bets)

    # Garante que as colunas numéricas sejam do tipo correto para cálculos
    df['Valor_Aposta'] = pd.to_numeric(df['Valor_Aposta'], errors='coerce').fillna(0)
    df['Lucro_Prejuizo'] = pd.to_numeric(df['Lucro_Prejuizo'], errors='coerce').fillna(0)
    df['Data_Hora_Aposta'] = pd.to_datetime(df['Data_Hora_Aposta'])
    
    # Ordena as apostas por data para o gráfico de evolução
    df = df.sort_values(by='Data_Hora_Aposta').reset_index(drop=True)

    # --- 1. Cálculo de Métricas Gerais ---
    total_apostas = len(df)
    total_investido = df['Valor_Aposta'].sum()
    lucro_total = df['Lucro_Prejuizo'].sum()
    roi = (lucro_total / total_investido * 100) if total_investido > 0 else 0
    
    greens = df[df['Resultado_Aposta'] == 'GREEN'].shape[0]
    reds = total_apostas - greens
    
    taxa_acerto = (greens / total_apostas * 100) if total_apostas > 0 else 0

    # --- 2. Análise por Campeonato ---
    stats_campeonato = df.groupby('Campeonato').agg(
        Total_Apostas=('ID', 'count'),
        Lucro_Prejuizo=('Lucro_Prejuizo', 'sum')
    ).reset_index().sort_values(by='Lucro_Prejuizo', ascending=False)

    # --- 3. Análise por Mercado ---
    stats_mercado = df.groupby('Mercado').agg(
        Total_Apostas=('ID', 'count'),
        Lucro_Prejuizo=('Lucro_Prejuizo', 'sum')
    ).reset_index().sort_values(by='Lucro_Prejuizo', ascending=False)
    
    # --- 4. Preparação dos Dados para o Gráfico de Evolução ---
    df['Saldo_Acumulado'] = df['Lucro_Prejuizo'].cumsum()
    
    # Formata a data para ser o "label" de cada ponto no gráfico
    chart_labels = df['Data_Hora_Aposta'].dt.strftime('%d/%m/%Y').tolist()
    chart_data = df['Saldo_Acumulado'].tolist()

    # Monta o dicionário final com todos os dados para o template
    return {
        'gerais': {
            'total_apostas': total_apostas,
            'total_investido': total_investido,
            'lucro_total': lucro_total,
            'roi': roi,
            'greens': greens,
            'reds': reds,
            'taxa_acerto': taxa_acerto
        },
        'por_campeonato': stats_campeonato.to_dict(orient='records'),
        'por_mercado': stats_mercado.to_dict(orient='records'),
        'grafico': {
            'labels': chart_labels,
            'data': chart_data
        }
    }