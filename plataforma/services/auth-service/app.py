import sqlite3
from flask import Flask, jsonify, request 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = '/tmp/auth.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # SQL ATUALIZADO: Ganhou a coluna "matricula" na penúltima linha
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT UNIQUE,
            senha TEXT,
            tipo TEXT,
            matricula TEXT
        );
    ''')
    conn.commit()
    conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Auth Service conectado!"}), 200


@app.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados or not dados.get('email') or not dados.get('senha'):
        return jsonify({"erro": "E-mail e senha são obrigatórios"}), 400

    conn = get_db_connection()
    # Puxa a matrícula na consulta do login também
    usuario = conn.execute(
        'SELECT id, nome, email, tipo, matricula FROM usuarios WHERE email = ? AND senha = ?', 
        (dados['email'], dados['senha'])
    ).fetchone()
    conn.close()

    if usuario:
        return jsonify(dict(usuario)), 200
    return jsonify({"erro": "E-mail ou senha incorretos"}), 401


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if usuario:
        return jsonify(dict(usuario)), 200
    return jsonify({"erro": "Usuário não encontrado"}), 404


@app.route('/api/users', methods=['POST'])
def create_user():
    dados = request.get_json()
    if not dados or not dados.get('nome') or not dados.get('email'):
        return jsonify({"erro": "Nome e email são obrigatórios"}), 400

    senha = dados.get('senha', 'senha123')
    tipo = dados.get('tipo', 'ALUNO').upper()
    if tipo not in ['ALUNO', 'PROFESSOR']:
        tipo = 'ALUNO'

    # Captura a matrícula. Se não vier nada, vira string vazia
    matricula = dados.get('matricula', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha, tipo, matricula) 
            VALUES (?, ?, ?, ?, ?)
        ''', (dados['nome'], dados['email'], senha, tipo, matricula))
        conn.commit()
        novo_id = cursor.lastrowid
        
        return jsonify({
            "mensagem": "Usuário criado!", 
            "id": novo_id, 
            "nome": dados['nome'], 
            "email": dados['email'],
            "tipo": tipo,
            "matricula": matricula
        }), 201

    except sqlite3.IntegrityError: 
        return jsonify({"erro": "Este e-mail já está cadastrado!"}), 409
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()


# ====================================================
# 🔍 NOVA ROTA: BUSCA DE USUÁRIO PELA MATRÍCULA
# ====================================================
@app.route('/api/users/matricula/<string:mat>', methods=['GET'])
def get_user_by_matricula(mat):
    conn = get_db_connection()
    # Só aceita devolver se o dono da matrícula for do tipo ALUNO
    usuario = conn.execute(
        'SELECT id, nome, email, tipo, matricula FROM usuarios WHERE matricula = ? AND tipo = "ALUNO"',
        (mat.strip(),)
    ).fetchone()
    conn.close()

    if usuario:
        return jsonify(dict(usuario)), 200
    
    return jsonify({"erro": "Nenhum Aluno encontrado com a matrícula informada."}), 404

if __name__ == '__main__':
    init_db()
    # Pega a porta do Render ou usa a 8081 se rodar no seu PC
    port = int(os.environ.get("PORT", 8081)) 
    app.run(host='0.0.0.0', port=port)