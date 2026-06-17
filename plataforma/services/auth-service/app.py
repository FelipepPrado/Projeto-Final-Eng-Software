import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

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
            email TEXT,
            tipo TEXT
        );
    ''')
    
    cur.execute('SELECT COUNT(*) FROM usuarios;')
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO usuarios (id, nome, email, tipo) VALUES (1, 'Carlos', 'carlos@ifce.edu.br', 'ALUNO')")
        cur.execute("INSERT INTO usuarios (id, nome, email, tipo) VALUES (2, 'Prof. Ana', 'ana@ifce.edu.br', 'PROFESSOR')")
    
    conn.commit()
    conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Auth Service conectado ao SQLite!"}), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if usuario:
        return jsonify(dict(usuario)), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8081)