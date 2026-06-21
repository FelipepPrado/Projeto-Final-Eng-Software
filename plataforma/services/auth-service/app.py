import sqlite3
from flask import Flask, jsonify, request 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('auth.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT UNIQUE,
            senha TEXT,
            tipo TEXT
        );
    ''')
    
    cur.execute('SELECT COUNT(*) FROM usuarios;')
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO usuarios (id, nome, email, senha, tipo) VALUES (1, 'Pedro', 'pedro@ifce.edu.br', 'senha123', 'ALUNO')")
    
    conn.commit()
    conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Auth Service conectado ao SQLite!"}), 200


# ==========================================
# 🚨 A ROTA DE LOGIN QUE ESTAVA FALTANDO!
# ==========================================
@app.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json()
    
    if not dados or not dados.get('email') or not dados.get('senha'):
        return jsonify({"erro": "E-mail e senha são obrigatórios"}), 400

    email = dados['email']
    senha = dados['senha']

    conn = get_db_connection()
    # Busca o usuário no banco
    usuario = conn.execute(
        'SELECT id, nome, email, tipo FROM usuarios WHERE email = ? AND senha = ?', 
        (email, senha)
    ).fetchone()
    conn.close()

    if usuario:
        return jsonify(dict(usuario)), 200
    else:
        return jsonify({"erro": "E-mail ou senha incorretos"}), 401


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if usuario:
        return jsonify(dict(usuario)), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404


@app.route('/api/users', methods=['POST'])
def create_user():
    dados = request.get_json()
    if not dados or not dados.get('nome') or not dados.get('email'):
        return jsonify({"erro": "Nome e email são obrigatórios"}), 400

    # Se o React enviar uma senha, usa ela. Se não enviar, adota 'senha123'
    senha_escolhida = dados.get('senha', 'senha123')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha, tipo) 
            VALUES (?, ?, ?, ?)
        ''', (dados['nome'], dados['email'], senha_escolhida, 'ALUNO'))
        conn.commit()
        novo_id = cursor.lastrowid
        return jsonify({"mensagem": "Usuário criado!", "id": novo_id, "nome": dados['nome'], "email": dados['email']}), 201
    except sqlite3.IntegrityError: 
        return jsonify({"erro": "Este e-mail já está cadastrado!"}), 409
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    init_db()
    # VOLTOU PARA A PORTA 5000 INTERNA DO DOCKER!
    app.run(host='0.0.0.0', port=5000)