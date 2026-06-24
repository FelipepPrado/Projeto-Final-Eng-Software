import os
import sqlite3
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ========================================================================
# DETECTOR DE AMBIENTE
# ========================================================================
if os.environ.get('RENDER'):
    DB_PATH = '/tmp/assignment.db'
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'assignment.db')

AUTH_SERVICE_URL     = os.environ.get('AUTH_SERVICE_URL',     'http://localhost:8081')
ACADEMIC_SERVICE_URL = os.environ.get('ACADEMIC_SERVICE_URL', 'http://localhost:8082')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id    INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,
            disciplina    TEXT    NOT NULL,
            titulo        TEXT    NOT NULL,
            status        TEXT    NOT NULL DEFAULT 'Pendente'
        );
    ''')
    conn.commit()
    conn.close()


# ========================================================================
# HEALTH CHECK
# ========================================================================
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Assignment Service Operacional!"}), 200


# ========================================================================
# BROADCAST — Professor dispara tarefa para toda a turma
# ========================================================================
@app.route('/api/assignments/broadcast', methods=['POST'])
def broadcast_assignment():
    dados   = request.get_json()
    disc_id = dados.get('disciplina_id')
    titulo  = dados.get('titulo', '').strip()
    nome_disciplina = dados.get('disciplina_nome', '').strip()

    if not disc_id or not titulo or not nome_disciplina:
        return jsonify({"erro": "disciplina_id, disciplina_nome e titulo são obrigatórios."}), 400

    # 1. Busca a lista de alunos matriculados no academic-service
    try:
        url = f'{ACADEMIC_SERVICE_URL}/api/academic/subjects/{disc_id}/alunos'
        res = requests.get(url, timeout=5)

        if res.status_code == 404:
            return jsonify({"erro": "Disciplina não encontrada no Academic Service."}), 404
        elif res.status_code != 200:
            return jsonify({"erro": "Academic Service indisponível."}), 502

        lista_aluno_ids = res.json()  # [1, 2, 3, ...]

    except Exception as e:
        return jsonify({"erro": f"Falha de comunicação com Academic Service: {e}"}), 500

    if not lista_aluno_ids:
        return jsonify({"erro": "A turma está vazia. Matricule alunos primeiro!"}), 400

    # 2. Insere uma tarefa para cada aluno
    conn = get_db_connection()
    cur  = conn.cursor()
    for aluno_id in lista_aluno_ids:
        cur.execute('''
            INSERT INTO tarefas (usuario_id, disciplina_id, disciplina, titulo, status)
            VALUES (?, ?, ?, ?, 'Pendente')
        ''', (aluno_id, int(disc_id), nome_disciplina, titulo))

    conn.commit()
    conn.close()

    return jsonify({
        "mensagem": f"Atividade '{titulo}' disparada para {len(lista_aluno_ids)} aluno(s) de {nome_disciplina}!"
    }), 201


# ========================================================================
# PAINEL DO ALUNO — busca tarefas + disciplinas matriculadas
# ========================================================================
@app.route('/api/assignments/<int:user_id>', methods=['GET'])
def get_user_assignments(user_id):

    # 1. Valida o aluno no auth-service
    try:
        res_auth = requests.get(f'{AUTH_SERVICE_URL}/api/users/{user_id}', timeout=5)
        if res_auth.status_code == 404:
            return jsonify({"erro": "Usuário não encontrado."}), 404
        elif res_auth.status_code != 200:
            return jsonify({"erro": "Auth Service indisponível."}), 502
        dados_usuario = res_auth.json()
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    # 2. Busca as disciplinas em que o aluno está matriculado (academic-service)
    try:
        res_acad = requests.get(
            f'{ACADEMIC_SERVICE_URL}/api/academic/subjects/aluno/{user_id}', timeout=5
        )
        disciplinas_matriculadas = res_acad.json() if res_acad.ok else []
        # [ {"id": 1, "nome": "Algoritmos"}, ... ]
    except Exception:
        disciplinas_matriculadas = []

    # 3. Busca as tarefas do banco local
    conn = get_db_connection()
    tarefas = conn.execute(
        'SELECT id, disciplina_id, disciplina, titulo, status FROM tarefas WHERE usuario_id = ?',
        (user_id,)
    ).fetchall()
    conn.close()

    # 4. Monta a lista de abas (disciplinas matriculadas + disciplinas com tarefas, sem duplicar)
    nomes_matriculadas = {d['nome'] for d in disciplinas_matriculadas}
    nomes_com_tarefa   = {t['disciplina'] for t in tarefas}
    abas = sorted(nomes_matriculadas | nomes_com_tarefa)

    return jsonify({
        "aluno":       dados_usuario['nome'],
        "email":       dados_usuario['email'],
        "matricula":   dados_usuario.get('matricula', ''),
        "disciplinas": abas,
        "tarefas":     [dict(t) for t in tarefas]
    }), 200


# ========================================================================
# ATUALIZAR STATUS DA TAREFA (Aluno entrega a lição)
# ========================================================================
@app.route('/api/assignments/<int:tarefa_id>/status', methods=['PATCH'])
def update_status(tarefa_id):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE tarefas SET status = 'Entregue' WHERE id = ?", (tarefa_id,))
        conn.commit()
        return jsonify({"mensagem": "Tarefa marcada como entregue!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    init_db()
    porta = int(os.environ.get('PORT', 8083))
    app.run(host='0.0.0.0', port=porta)