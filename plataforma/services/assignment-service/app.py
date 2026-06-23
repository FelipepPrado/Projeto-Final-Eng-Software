import os
import sqlite3
import requests
from flask import Flask, jsonify, request 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = '/tmp/assignment.db'
AUTH_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:8081')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH) 
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Tabela de Tarefas Individuais dos alunos
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            disciplina TEXT,
            titulo TEXT,
            status TEXT
        );
    ''')

    # 2. NOVA: Tabela de Disciplinas que os professores criam
    cur.execute('''
        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            professor_id INTEGER
        );
    ''')

    # 3. NOVA: Tabela de Vínculo (Quem está matriculado em qual matéria)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS matriculas (
            disciplina_id INTEGER,
            aluno_id INTEGER,
            PRIMARY KEY (disciplina_id, aluno_id)
        );
    ''')
    
    conn.commit()
    conn.close()


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Assignment Service 2.0 (Turmas) Operacional!"}), 200


# ==========================================
# 📚 NOVAS ROTAS DE GESTÃO DE TURMAS
# ==========================================

# A. Professor cria uma nova disciplina
@app.route('/api/subjects', methods=['POST'])
def create_subject():
    dados = request.get_json()
    nome = dados.get('nome', '').strip()
    prof_id = dados.get('professor_id')

    if not nome or not prof_id:
        return jsonify({"erro": "Nome da matéria e ID do professor são obrigatórios"}), 400

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO disciplinas (nome, professor_id) VALUES (?, ?)', (nome, prof_id))
        conn.commit()
        return jsonify({"mensagem": f"Disciplina '{nome}' criada com sucesso!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"erro": f"A disciplina '{nome}' já existe no sistema."}), 409
    finally:
        conn.close()


# B. React pede a lista de disciplinas daquele professor específico pro Dropdown
@app.route('/api/subjects/professor/<int:prof_id>', methods=['GET'])
def get_professor_subjects(prof_id):
    conn = get_db_connection()
    disciplinas = conn.execute('SELECT * FROM disciplinas WHERE professor_id = ?', (prof_id,)).fetchall()
    conn.close()
    return jsonify([dict(d) for d in disciplinas]), 200


# C. Professor vincula um Aluno à Disciplina usando a MATRÍCULA
@app.route('/api/subjects/enroll', methods=['POST'])
def enroll_student():
    dados = request.get_json()
    disc_id = dados.get('disciplina_id')
    matricula_digitada = dados.get('matricula', '').strip()

    if not disc_id or not matricula_digitada:
        return jsonify({"erro": "Selecione a disciplina e digite a Matrícula do aluno."}), 400

    # 1. RESOLUÇÃO DE IDENTIDADE: Pergunta pro Auth Service qual é o ID real dessa matrícula
    try:
        url_consulta = f'{AUTH_URL}/api/users/matricula/{matricula_digitada}'
        res = requests.get(url_consulta, timeout=4)
        
        if res.status_code == 404:
            return jsonify({"erro": f"A matrícula '{matricula_digitada}' não existe ou pertence a um Docente."}), 404
        elif res.status_code != 200:
            return jsonify({"erro": "Serviço de alunos indisponível no momento."}), 502
            
        aluno_encontrado = res.json()
        aluno_id_real = aluno_encontrado['id']
        nome_do_aluno = aluno_encontrado['nome']

    except Exception as e:
        return jsonify({"erro": f"Falha de comunicação interna: {e}"}), 500

    # 2. Sabendo o ID real, efetiva a matrícula na tabela relacional:
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO matriculas (disciplina_id, aluno_id) VALUES (?, ?)', (int(disc_id), int(aluno_id_real)))
        conn.commit()
        
        # Devolve uma mensagem super amigável pro ecrã do professor:
        return jsonify({
            "mensagem": f"Sucesso! O aluno {nome_do_aluno} foi matriculado na turma."
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({"erro": f"O aluno {nome_do_aluno} já está matriculado nesta matéria!"}), 409
    finally:
        conn.close()


# D. O DISPARO EM MASSA (Broadcast)
@app.route('/api/assignments/broadcast', methods=['POST'])
def broadcast_assignment():
    dados = request.get_json()
    disc_id = dados.get('disciplina_id')
    titulo = dados.get('titulo')

    if not disc_id or not titulo:
        return jsonify({"erro": "Selecione a disciplina e digite a tarefa."}), 400

    conn = get_db_connection()
    
    # Pega o nome da matéria
    disc = conn.execute('SELECT nome FROM disciplinas WHERE id = ?', (disc_id,)).fetchone()
    if not disc:
        return jsonify({"erro": "Disciplina inexistente."}), 404
    nome_disciplina = disc['nome']

    # Puxa a lista de todos os alunos sentados nessa sala
    alunos = conn.execute('SELECT aluno_id FROM matriculas WHERE disciplina_id = ?', (disc_id,)).fetchall()
    
    if not alunos:
        return jsonify({"erro": f"A turma de '{nome_disciplina}' está vazia. Matricule algum aluno primeiro!"}), 400

    # Tira a fotocópia para cada aluno
    cursor = conn.cursor()
    for aluno in alunos:
        cursor.execute('''
            INSERT INTO tarefas (usuario_id, disciplina, titulo, status) 
            VALUES (?, ?, ?, 'Pendente')
        ''', (aluno['aluno_id'], nome_disciplina, titulo))
    
    conn.commit()
    total_afetados = len(alunos)
    conn.close()

    return jsonify({"mensagem": f"Atividade disparada para {total_afetados} aluno(s) da turma de {nome_disciplina}!"}), 201


# [Mantido intacto para a tela do Aluno continuar funcionando]
@app.route('/api/assignments/<int:user_id>', methods=['GET'])
def get_user_assignments(user_id):
    url_auth = f'{AUTH_URL}/api/users/{user_id}'
    
    try:
        resposta_auth = requests.get(url_auth, timeout=5)
        
        if resposta_auth.status_code == 200:
            dados_usuario = resposta_auth.json()
            
            conn = get_db_connection()
            
            # 1. Puxa as lições
            tarefas = conn.execute(
                'SELECT id, disciplina, titulo, status FROM tarefas WHERE usuario_id = ?', 
                (user_id,)
            ).fetchall()
            
            # 2. Puxa as matérias em que ele foi matriculado oficialmente pelo professor
            matriculas = conn.execute('''
                SELECT d.nome FROM matriculas m
                JOIN disciplinas d ON m.disciplina_id = d.id
                WHERE m.aluno_id = ?
            ''', (user_id,)).fetchall()
            
            conn.close()
            
            # Junta as matérias oficiais + as matérias das lições (pra evitar que uma lição antiga suma)
            lista_mat = [m['nome'] for m in matriculas]
            lista_tar = [t['disciplina'] for t in tarefas]
            disciplinas_do_aluno = sorted(list(set(lista_mat + lista_tar)))
            
            return jsonify({
                "aluno": dados_usuario["nome"],
                "email": dados_usuario["email"],
                "matricula": dados_usuario.get("matricula", "Sem Matrícula"),
                "disciplinas": disciplinas_do_aluno, # <--- ENVIANDO A LISTA DE ABAS AQUI!
                "tarefas": [dict(t) for t in tarefas]
            }), 200
            
        elif resposta_auth.status_code == 404:
            return jsonify({"erro": "Usuário não encontrado."}), 404
            
        return jsonify({"erro": "Erro de Gateway"}), 502

    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/assignments/<int:tarefa_id>/status', methods=['PATCH'])
def update_status(tarefa_id):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE tarefas SET status = 'Entregue' WHERE id = ?", (tarefa_id,))
        conn.commit()
        return jsonify({"mensagem": "Status atualizado!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8083)