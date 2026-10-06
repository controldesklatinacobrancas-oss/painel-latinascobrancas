import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, abort

# --- Configuracoes ---
app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Mapeamento de Agentes para Supervisoras ---
AGENTES_POR_SUPERVISORA = {
    "tatiane": {
        "nome": "Tatiane Lima",
        "agentes": [
            "Ana Carla-LT", "Bruna Jadna-LT", "Maria Lizete-LT", "Kaoane Domingos-LT",
            "Maria Eduarda-LT", "Luana Bueno-LT", "Paula Oliveira-LT", "Ana Rocha-Juridico",
            "Juliana Pereira-LT", "Raquel Vieira-LT", "Jhonny Souza-LT", "Ariane Wackerhage-LT",
            "Heloisa Candido-LT", "Eliane Luz-LT", "Amanda Santos-LT", "Jessica Alves-LT",
            "Haline Goncalves-LT", "Lilian Souza-LT",
            "Kauana Neri-LT"
        ]
    },
    "luciene": {
        "nome": "Luciene",
        "agentes": [
            "Yago Sampaio-LG", "Nicoly Maciel-LG", "Cleitiane Pereira-LG", "Nycole Batista-LG",
            "Gabriela Santos-LG", "Maria Nortok-LG", "Rebeca Melo-LG", "Leticia Bremen-LG",
            "Maria Leite-LT", "Fabiola Soares-LT"
        ]
    }
}

# --- Armazenamento em memoria ---
eventos_em_memoria = []

# --- Rotas ---
@app.route('/')
def index():
    links = "".join([
        f'<li><a href="/{chave}">{dados["nome"]}</a></li>'
        for chave, dados in AGENTES_POR_SUPERVISORA.items()
    ])
    return render_template('index.html', links=links)

@app.route('/<supervisora_chave>')
def painel_supervisora(supervisora_chave):
    supervisora = AGENTES_POR_SUPERVISORA.get(supervisora_chave)
    if not supervisora:
        abort(404, description="Supervisora nao encontrada.")

    eventos_filtrados = [
        e for e in eventos_em_memoria if e['nome'] in supervisora['agentes']
    ]
    eventos_filtrados.sort(key=lambda x: x.get('hora_despausa', ''), reverse=True)

    return render_template(
        'painel.html',
        nome_supervisora=supervisora['nome'],
        eventos=eventos_filtrados
    )

@app.route('/publicar', methods=['POST'])
def publicar_evento():
    dados = request.get_json()
    if not dados or not all(k in dados for k in ('nome', 'motivo', 'tempo_segundos')):
        return jsonify({"error": "Dados invalidos"}), 400

    # Aceita os campos novos, com fallback pra eventos antigos
    hora_pausa = dados.get('hora_pausa', '—')
    hora_despausa = dados.get('hora_despausa', datetime.now().strftime('%d/%m/%Y - %H:%M:%S'))

    novo_evento = {
        'nome': dados['nome'],
        'motivo': dados['motivo'],
        'tempo_segundos': int(dados['tempo_segundos']),
        'hora_pausa': hora_pausa,
        'hora_despausa': hora_despausa,
    }

    eventos_em_memoria.append(novo_evento)

    if len(eventos_em_memoria) > 500:
        eventos_em_memoria.pop(0)

    print(f"Evento recebido: {novo_evento}")
    return jsonify({"status": "sucesso"}), 201

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "eventos": len(eventos_em_memoria),
        "hora": datetime.now().strftime('%d/%m/%Y - %H:%M:%S')
    })

# --- Execucao ---
if __name__ == '__main__':
    porta = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=porta,
        threaded=True,
        debug=False,
        use_reloader=False
    )
