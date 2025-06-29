from flask import Flask, render_template, request, redirect, url_for, flash
from reports import get_dashboard_data
from logic import register_new_bet, get_all_bets, get_bet_by_id, update_bet, delete_bet_by_id, search_bets # Adicione search_bets aqui

# Inicializa a aplicação Flask
app = Flask(__name__)
# Adiciona uma chave secreta, necessária para as flash messages
app.secret_key = 'sua_chave_secreta_pode_ser_qualquer_coisa'

@app.route('/')
def index():
    """Página principal que exibe apostas com filtro, busca e ordenação."""
    query = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'ID') # Padrão é ordenar por ID
    order = request.args.get('order', 'desc') # Padrão é descendente

    if query:
        bets_to_display = search_bets(query) # A ordenação da busca pode ser um próximo passo
    else:
        bets_to_display = get_all_bets(sort_by=sort_by, order=order)
    
    # Inverte a ordem para o próximo clique no link
    next_order = 'desc' if order == 'asc' else 'asc'
        
    return render_template('index.html', 
                           bets=bets_to_display, 
                           search_query=query,
                           sort_by=sort_by,
                           next_order=next_order)

@app.route('/add', methods=['POST'])
def add_bet():
    """Rota que recebe os dados do formulário e registra uma nova aposta."""
    bet_data = request.form.to_dict()
    register_new_bet(bet_data)
    # Adiciona uma mensagem de sucesso
    flash('Aposta registrada com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<bet_id>')
def delete_bet(bet_id):
    """Rota para deletar uma aposta."""
    delete_bet_by_id(bet_id)
    # Adiciona uma mensagem de alerta/sucesso
    flash(f'Aposta ID {bet_id} foi excluída.', 'warning')
    return redirect(url_for('index'))

@app.route('/edit/<bet_id>')
def edit_bet(bet_id):
    """Mostra o formulário de edição para uma aposta específica."""
    bet = get_bet_by_id(bet_id)
    if bet:
        return render_template('edit.html', bet=bet)
    flash(f'Aposta ID {bet_id} não encontrada.', 'error')
    return redirect(url_for('index'))

@app.route('/update/<bet_id>', methods=['POST'])
def update_bet_route(bet_id):
    """Recebe os dados do formulário de edição e atualiza a aposta."""
    update_data = request.form.to_dict()
    update_bet(bet_id, update_data)
    # Adiciona uma mensagem de sucesso
    flash(f'Aposta ID {bet_id} atualizada com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Rota que busca os dados e renderiza o template do dashboard."""
    dashboard_data = get_dashboard_data()
    return render_template('dashboard.html', data=dashboard_data)

# Bloco para executar o servidor quando o script é chamado diretamente
if __name__ == '__main__':
    app.run(debug=True)