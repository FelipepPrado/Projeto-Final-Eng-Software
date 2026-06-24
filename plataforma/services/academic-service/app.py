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
    DB_PATH = '/tmp/academic.db'
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'academic.db')

AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:8081')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Disciplinas pertencem a um professor
    cur.execute('''
        CREATE TABLE IF NOT EXISTS disciplinas (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nome         TEXT    NOT NULL,
            professor_id INTEGER NOT NULL,
            UNIQUE(nome, professor_id)
        );
    ''')

    # Matrículas: vínculo aluno <-> disciplina
    cur.execute('''
        CREATE TABLE IF NOT EXISTS matriculas (
            disciplina_id INTEGER NOT NULL,
            aluno_id      INTEGER NOT NULL,
            PRIMARY KEY (disciplina_id, aluno_id)
        );
    ''')

    conn.commit()
    conn.close()


# ========================================================================
# HEALTH CHECK
# ========================================================================
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Academic Service Operacional!"}), 200


# ========================================================================
# DISCIPLINAS
# ========================================================================

# Professor cria uma disciplina
@app.route('/api/academic/subjects', methods=['POST'])
def criar_disciplina():
    dados = request.get_json()
    nome       = dados.get('nome', '').strip()
    prof_id    = dados.get('professor_id')

    if not nome or not prof_id:
        return jsonify({"erro": "Nome da disciplina e ID do professor são obrigatórios."}), 400

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO disciplinas (nome, professor_id) VALUES (?, ?)',
            (nome, prof_id)
        )
        conn.commit()
        novo_id = cur.lastrowid
        return jsonify({"id": novo_id, "nome": nome, "professor_id": prof_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({"erro": f"A disciplina '{nome}' já existe para este professor."}), 409
    finally:
        conn.close()


# Lista as disciplinas de um professor (para popular o dropdown no frontend)
@app.route('/api/academic/subjects/professor/<int:prof_id>', methods=['GET'])
def listar_disciplinas_professor(prof_id):
    conn = get_db_connection()
    disciplinas = conn.execute(
        'SELECT * FROM disciplinas WHERE professor_id = ?', (prof_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(d) for d in disciplinas]), 200


# Lista as disciplinas em que um aluno está matriculado (para as abas do HomeAluno)
@app.route('/api/academic/subjects/aluno/<int:aluno_id>', methods=['GET'])
def listar_disciplinas_aluno(aluno_id):
    conn = get_db_connection()
    disciplinas = conn.execute('''
        SELECT d.id, d.nome FROM disciplinas d
        INNER JOIN matriculas m ON m.disciplina_id = d.id
        WHERE m.aluno_id = ?
    ''', (aluno_id,)).fetchall()
    conn.close()
    return jsonify([dict(d) for d in disciplinas]), 200


# ========================================================================
# MATRÍCULAS
# ========================================================================

# Professor matricula um aluno usando a matrícula acadêmica dele
@app.route('/api/academic/enroll', methods=['POST'])
def matricular_aluno():
    dados         = request.get_json()
    disc_id       = dados.get('disciplina_id')
    matricula_str = dados.get('matricula', '').strip()

    if not disc_id or not matricula_str:
        return jsonify({"erro": "Selecione a disciplina e informe a matrícula do aluno."}), 400

    # 1. Resolve a matrícula → ID real no auth-service
    try:
        url = f'{AUTH_SERVICE_URL}/api/users/matricula/{matricula_str}'
        res = requests.get(url, timeout=4)

        if res.status_code == 404:
            return jsonify({"erro": f"Matrícula '{matricula_str}' não encontrada ou não pertence a um aluno."}), 404
        elif res.status_code != 200:
            return jsonify({"erro": "Auth Service indisponível."}), 502

        aluno = res.json()
        aluno_id   = aluno['id']
        aluno_nome = aluno['nome']

    except Exception as e:
        return jsonify({"erro": f"Falha de comunicação com Auth Service: {e}"}), 500

    # 2. Verifica se a disciplina existe
    conn = get_db_connection()
    disc = conn.execute('SELECT id FROM disciplinas WHERE id = ?', (disc_id,)).fetchone()
    if not disc:
        conn.close()
        return jsonify({"erro": "Disciplina não encontrada."}), 404

    # 3. Efetiva a matrícula
    try:
        conn.execute(
            'INSERT INTO matriculas (disciplina_id, aluno_id) VALUES (?, ?)',
            (int(disc_id), int(aluno_id))
        )
        conn.commit()
        return jsonify({"mensagem": f"Aluno {aluno_nome} matriculado com sucesso!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"erro": f"{aluno_nome} já está matriculado nesta disciplina."}), 409
    finally:
        conn.close()


# Lista os alunos de uma disciplina (usado pelo assignment-service no broadcast)
@app.route('/api/academic/subjects/<int:disc_id>/alunos', methods=['GET'])
def listar_alunos_da_disciplina(disc_id):
    conn = get_db_connection()
    alunos = conn.execute(
        'SELECT aluno_id FROM matriculas WHERE disciplina_id = ?', (disc_id,)
    ).fetchall()
    conn.close()
    return jsonify([row['aluno_id'] for row in alunos]), 200


if __name__ == '__main__':
    init_db()
    porta = int(os.environ.get('PORT', 8082))
    app.run(host='0.0.0.0', port=porta)