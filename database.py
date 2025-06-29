# database.py
import csv
import os
from config import CSV_FILE, COLUMNS # Importa as configurações!

def initialize_csv():
    """Inicializa o arquivo CSV com os cabeçalhos se ele não existir."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(COLUMNS)
        print(f"Arquivo '{CSV_FILE}' criado com os cabeçalhos.")

def load_bets():
    """Carrega todas as apostas do CSV para uma lista de dicionários."""
    if not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0:
        return []
    bets = []
    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                for col in COLUMNS:
                    row.setdefault(col, '')
                bets.append(row)
    except Exception as e:
        print(f"Erro ao carregar apostas do CSV: {e}")
        return []
    return bets

def save_bets(bets_list):
    """Salva a lista de apostas de volta no CSV."""
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(bets_list)
    except Exception as e:
        print(f"Erro ao salvar apostas no CSV: {e}")