import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ========================================================================
# DETECTOR DE AMBIENTE (Local vs. Render)
# ========================================================================
if os.environ.get('RENDER'):
    DB_PATH = '/tmp/auth.db'
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'auth.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT    NOT NULL,
            email     TEXT    UNIQUE NOT NULL,
            senha     TEXT    NOT NULL,
            tipo      TEXT    NOT NULL DEFAULT 'ALUNO',
            matricula TEXT
        );
    ''')
    conn.commit()
    conn.close()


# ========================================================================
# HEALTH CHECK
# ========================================================================
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Auth Service Operacional!"}), 200


# ========================================================================
# CADASTRO
# ========================================================================
@app.route('/api/users', methods=['POST'])
def criar_usuario():
    dados = request.get_json()
    nome      = dados.get('nome', '').strip()
    email     = dados.get('email', '').strip()
    senha     = dados.get('senha', '').strip()
    tipo      = dados.get('tipo', 'ALUNO').upper()
    matricula = dados.get('matricula', '').strip() or None

    if not nome or not email or not senha:
        return jsonify({"erro": "Nome, e-mail e senha são obrigatórios."}), 400

    if tipo == 'ALUNO' and not matricula:
        return jsonify({"erro": "Matrícula é obrigatória para alunos."}), 400

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO usuarios (nome, email, senha, tipo, matricula) VALUES (?, ?, ?, ?, ?)',
            (nome, email, senha, tipo, matricula)
        )
        conn.commit()
        novo_id = cur.lastrowid
        return jsonify({
            "id": novo_id,
            "nome": nome,
            "email": email,
            "tipo": tipo,
            "matricula": matricula
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({"erro": "Este e-mail já está cadastrado."}), 409
    finally:
        conn.close()


# ========================================================================
# LOGIN
# ========================================================================
@app.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json()
    email = dados.get('email', '').strip()
    senha = dados.get('senha', '').strip()

    conn = get_db_connection()
    usuario = conn.execute(
        'SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha)
    ).fetchone()
    conn.close()

    if not usuario:
        return jsonify({"erro": "E-mail ou senha incorretos."}), 401

    return jsonify({
        "id":        usuario['id'],
        "nome":      usuario['nome'],
        "email":     usuario['email'],
        "tipo":      usuario['tipo'],
        "matricula": usuario['matricula']
    }), 200


# ========================================================================
# BUSCA POR ID (usado pelo assignment-service)
# ========================================================================
@app.route('/api/users/<int:user_id>', methods=['GET'])
def buscar_usuario_por_id(user_id):
    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado."}), 404

    return jsonify({
        "id":        usuario['id'],
        "nome":      usuario['nome'],
        "email":     usuario['email'],
        "tipo":      usuario['tipo'],
        "matricula": usuario['matricula']
    }), 200


# ========================================================================
# BUSCA POR MATRÍCULA (usado pelo academic-service para enroll)
# ========================================================================
@app.route('/api/users/matricula/<string:matricula>', methods=['GET'])
def buscar_por_matricula(matricula):
    conn = get_db_connection()
    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE matricula = ? AND tipo = 'ALUNO'", (matricula,)
    ).fetchone()
    conn.close()

    if not usuario:
        return jsonify({"erro": "Matrícula não encontrada ou não pertence a um aluno."}), 404

    return jsonify({
        "id":        usuario['id'],
        "nome":      usuario['nome'],
        "email":     usuario['email'],
        "matricula": usuario['matricula']
    }), 200


if __name__ == '__main__':
    init_db()
    porta = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=porta)