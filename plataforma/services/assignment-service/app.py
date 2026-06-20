import sqlite3
import requests
from flask import Flask, jsonify, request 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('assignment.db') 
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            disciplina TEXT,
            titulo TEXT,
            status TEXT
        );
    ''')
    
    cur.execute('SELECT COUNT(*) FROM tarefas;')
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO tarefas (usuario_id, disciplina, titulo, status) VALUES (1, 'DevOps', 'Projeto Final Sprint 2', 'Pendente')")
        cur.execute("INSERT INTO tarefas (usuario_id, disciplina, titulo, status) VALUES (1, 'Física Aplicada', 'Cálculos Eletromagnetismo', 'Entregue')")
    
    conn.commit()
    conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Assignment Service conectado ao SQLite!"}), 200

@app.route('/api/assignments/<int:user_id>', methods=['GET'])
def get_user_assignments(user_id):
    url_auth = f'http://auth-service:8081/api/users/{user_id}'
    
    try:
        resposta_auth = requests.get(url_auth)
        
        if resposta_auth.status_code == 200:
            dados_usuario = resposta_auth.json()
            
            conn = get_db_connection()
            tarefas = conn.execute('SELECT id,disciplina, titulo, status FROM tarefas WHERE usuario_id = ?', (user_id,)).fetchall()
            conn.close()
            
            return jsonify({
                "aluno": dados_usuario["nome"],
                "email": dados_usuario["email"],
                "tarefas": [dict(t) for t in tarefas]
            }), 200
            
        elif resposta_auth.status_code == 404:
            return jsonify({"erro": "Usuário não encontrado no Auth Service."}), 404
            
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": "Falha na comunicação com o Auth Service", "detalhes": str(e)}), 500


@app.route('/api/assignments', methods=['POST'])
def create_assignment():
    dados = request.get_json()
    
    if not dados or not dados.get('aluno_id') or not dados.get('disciplina') or not dados.get('titulo'):
        return jsonify({"erro": "Faltam campos obrigatórios"}), 400

    conn = get_db_connection() 
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO tarefas (usuario_id, disciplina, titulo, status) 
            VALUES (?, ?, ?, 'Pendente')
        ''', (dados['aluno_id'], dados['disciplina'], dados['titulo']))
        conn.commit()
        return jsonify({"mensagem": "Tarefa adicionada com sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/assignments/<int:tarefa_id>/status', methods=['PATCH'])
def update_status(tarefa_id):
    conn = get_db_connection()
    conn.execute("UPDATE tarefas SET status = 'Entregue' WHERE id = ?", (tarefa_id,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Status atualizado!"}), 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8083)