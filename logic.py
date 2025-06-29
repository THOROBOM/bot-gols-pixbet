# logic.py (Refatorado para Abstração)
from datetime import datetime
from database import load_bets, save_bets
from config import TAXA_LUCRO_GREEN

# ===================================================================
# == LÓGICA DE NEGÓCIO PURA (SEM INPUT/PRINT) ==
# == Essas funções podem ser usadas por qualquer interface (terminal, web, etc) ==
# ===================================================================

def get_next_id(bets):
    """Calcula o próximo ID disponível."""
    if not bets:
        return 1
    valid_ids = [int(b['ID']) for b in bets if b.get('ID') and b['ID'].isdigit()]
    return max(valid_ids) + 1 if valid_ids else 1

def determine_actual_outcome(market, gols_casa, gols_fora):
    """Determina o resultado (GREEN/RED) para mercados de gols."""
    market_lower = market.lower().strip()
    total_gols = int(gols_casa) + int(gols_fora)

    if "over" in market_lower:
        try:
            line = float(market_lower.split("over")[1].strip().split(" ")[0])
            return "GREEN" if total_gols > line else "RED"
        except (ValueError, IndexError):
            return "UNKNOWN"
    elif "under" in market_lower:
        try:
            line = float(market_lower.split("under")[1].strip().split(" ")[0])
            return "GREEN" if total_gols < line else "RED"
        except (ValueError, IndexError):
            return "UNKNOWN"
    return "UNKNOWN"

def calculate_profit_loss(valor_aposta, resultado_aposta):
    """Calcula o lucro ou prejuízo com base no resultado."""
    valor_aposta = float(valor_aposta)
    if resultado_aposta.upper() == 'GREEN':
        return valor_aposta * TAXA_LUCRO_GREEN
    elif resultado_aposta.upper() == 'RED':
        return -valor_aposta
    return 0.0

def register_new_bet(bet_data):
    """
    Registra uma nova aposta, determinando o resultado automaticamente.
    """
    bets = load_bets()
    
    # Determina o resultado automaticamente se for um mercado conhecido
    resultado_automatico = determine_actual_outcome(
        bet_data.get('mercado', ''),
        bet_data.get('gols_casa', 0),
        bet_data.get('gols_fora', 0)
    )
    
    # Usa o resultado automático se encontrado, senão usa o que veio do form (se houver)
    resultado_final = resultado_automatico if resultado_automatico != "UNKNOWN" else bet_data.get('resultado_aposta', 'N/A').upper()

    new_bet = {
        'ID': str(get_next_id(bets)),
        'Data_Hora_Aposta': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Valor_Aposta': f"{float(bet_data.get('valor_aposta', 0)):.2f}",
        'Campeonato': bet_data.get('campeonato', ''),
        'Dia_Jogo': bet_data.get('dia_jogo', ''),
        'Time_Casa': bet_data.get('time_casa', ''),
        'Time_Fora': bet_data.get('time_fora', ''),
        'Mercado': bet_data.get('mercado', ''),
        'Gols_Casa': str(bet_data.get('gols_casa', 0)),
        'Gols_Fora': str(bet_data.get('gols_fora', 0)),
        'Resultado_Aposta': resultado_final
    }
    
    lucro_prejuizo = calculate_profit_loss(new_bet['Valor_Aposta'], new_bet['Resultado_Aposta'])
    new_bet['Lucro_Prejuizo'] = f"{lucro_prejuizo:.2f}"
    
    bets.append(new_bet)
    save_bets(bets)
    return new_bet

def get_all_bets(sort_by='ID', order='desc'):
    """
    Retorna todas as apostas do banco de dados, com opção de ordenação.
    """
    bets = load_bets()
    
    # Define a chave de ordenação e se precisa converter para float
    is_numeric = sort_by in ['Valor_Aposta', 'Lucro_Prejuizo']
    
    # Define a direção da ordenação
    reverse_order = (order == 'desc')

    # Ordena a lista de apostas
    try:
        if is_numeric:
            bets.sort(key=lambda x: float(x.get(sort_by, 0)), reverse=reverse_order)
        else:
            # Para o ID, tratamos como número para ordenar corretamente
            if sort_by == 'ID':
                 bets.sort(key=lambda x: int(x.get(sort_by, 0)), reverse=reverse_order)
            else:
                 bets.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse_order)
    except (ValueError, TypeError):
        # Em caso de erro (ex: dado mal formatado), retorna a lista sem ordenar
        pass

    return bets

def search_bets(query):
    """Filtra as apostas com base em um termo de pesquisa."""
    if not query:
        return get_all_bets()
        
    all_bets = get_all_bets()
    query = query.lower().strip()
    
    filtered_bets = [
        bet for bet in all_bets if
        query in bet.get('Campeonato', '').lower() or
        query in bet.get('Time_Casa', '').lower() or
        query in bet.get('Time_Fora', '').lower() or
        query in bet.get('Mercado', '').lower()
    ]
    
    return filtered_bets

def get_bet_by_id(bet_id):
    """Encontra e retorna uma aposta pelo seu ID."""
    bets = load_bets()
    for bet in bets:
        if str(bet.get('ID')) == str(bet_id):
            return bet
    return None

def update_bet(bet_id, update_data):
    """
    Atualiza uma aposta existente, recalculando o resultado automaticamente.
    """
    bets = load_bets()
    bet_to_update = None
    for bet in bets:
        if str(bet.get('ID')) == str(bet_id):
            bet_to_update = bet
            break
            
    if not bet_to_update:
        return None
        
    for key, value in update_data.items():
        if key in bet_to_update and value is not None:
            bet_to_update[key] = value

    # Recalcula o resultado automaticamente
    resultado_automatico = determine_actual_outcome(
        bet_to_update.get('Mercado', ''),
        bet_to_update.get('Gols_Casa', 0),
        bet_to_update.get('Gols_Fora', 0)
    )
    
    resultado_final = resultado_automatico if resultado_automatico != "UNKNOWN" else bet_to_update.get('Resultado_Aposta', 'N/A').upper()
    bet_to_update['Resultado_Aposta'] = resultado_final
            
    # Recalcula o lucro/prejuízo
    lucro_prejuizo = calculate_profit_loss(bet_to_update['Valor_Aposta'], bet_to_update['Resultado_Aposta'])
    bet_to_update['Lucro_Prejuizo'] = f"{lucro_prejuizo:.2f}"
        
    save_bets(bets)
    return bet_to_update

def delete_bet_by_id(bet_id):
    """

    Deleta uma aposta pelo seu ID.
    Retorna True se a exclusão foi bem-sucedida, False caso contrário.
    """
    bets = load_bets()
    updated_bets = [bet for bet in bets if str(bet.get('ID')) != str(bet_id)]
    
    if len(updated_bets) < len(bets):
        save_bets(updated_bets)
        return True
        
    return False