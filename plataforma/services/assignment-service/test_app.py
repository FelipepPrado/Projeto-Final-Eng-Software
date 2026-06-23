import os
import pytest
import json
import sqlite3
from unittest.mock import patch, MagicMock

# Importa a aplicação como um módulo para podermos injetar o DB fake
import app as assign_app

TEST_DB = '/tmp/test_pytest_assign.db'

@pytest.fixture
def client():
    assign_app.app.config['TESTING'] = True
    assign_app.DB_PATH = TEST_DB

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    with assign_app.app.app_context():
        assign_app.init_db()
        
        # 🧪 PLANTANDO AS SEMENTES (Mock de dados relacionais)
        conn = sqlite3.connect(TEST_DB)
        cur = conn.cursor()
        
        # 1. Criamos a matéria "Cálculo IV" (ID 10) do Prof ID 2
        cur.execute("INSERT INTO disciplinas (id, nome, professor_id) VALUES (10, 'Cálculo IV', 2)")
        
        # 2. Matriculamos o Aluno ID 1 nessa matéria
        cur.execute("INSERT INTO matriculas (disciplina_id, aluno_id) VALUES (10, 1)")
        
        # 3. Passamos uma tarefa pendente para o Aluno ID 1
        cur.execute("INSERT INTO tarefas (id, usuario_id, disciplina, titulo, status) VALUES (100, 1, 'Cálculo IV', 'Resolver derivadas parciais', 'Pendente')")
        
        conn.commit()
        conn.close()

    with assign_app.app.test_client() as client:
        yield client

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


# ==========================================
# 🧪 TESTES DE ROTAS BÁSICAS
# ==========================================

def test_health_check(client):
    resposta = client.get('/health')
    assert resposta.status_code == 200
    assert "Operacional" in json.loads(resposta.data)["status"]


# ==========================================
# 🧪 TESTES COM MOCK DO AUTH SERVICE
# ==========================================

@patch('app.requests.get')
def test_get_user_assignments_sucesso(mock_get, client):
    # Simula o Auth Service respondendo que o Aluno 1 é o Pedro
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "nome": "Pedro Miguel",
        "email": "pedro@ifce.edu.br",
        "matricula": "20261045050012"
    }

    resposta = client.get('/api/assignments/1')
    assert resposta.status_code == 200
    
    dados = json.loads(resposta.data)
    assert dados["aluno"] == "Pedro Miguel"
    assert "Cálculo IV" in dados["disciplinas"]
    assert len(dados["tarefas"]) == 1
    assert dados["tarefas"][0]["status"] == "Pendente"


@patch('app.requests.get')
def test_get_user_assignments_aluno_inexistente(mock_get, client):
    mock_get.return_value.status_code = 404

    resposta = client.get('/api/assignments/999')
    assert resposta.status_code == 404
    
    # CORRIGIDO: Agora ele procura "encontrado" dentro de "Usuário não encontrado."
    assert "encontrado" in json.loads(resposta.data)["erro"]

# ==========================================
# 🧪 TESTES DO MOTOR DE TURMAS E LMS
# ==========================================

def test_criar_disciplina_sucesso(client):
    payload = {"nome": "Física Quântica", "professor_id": 2}
    resposta = client.post('/api/subjects', json=payload)
    assert resposta.status_code == 201
    assert "criada com sucesso" in json.loads(resposta.data)["mensagem"]


def test_proibir_criar_disciplina_com_nome_repetido(client):
    # Tenta recriar Cálculo IV, que já foi plantada na Fixture
    payload = {"nome": "Cálculo IV", "professor_id": 2}
    resposta = client.post('/api/subjects', json=payload)
    assert resposta.status_code == 409


@patch('app.requests.get')
def test_matricular_aluno_pela_matricula_com_sucesso(mock_get, client):
    # O professor digita a matrícula '2026999'. 
    # Simulamos o Auth Service traduzindo isso para o "Aluno ID 5 (Ana)"
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 5, "nome": "Ana Beatriz"}

    payload = {"disciplina_id": 10, "matricula": "2026999"}
    resposta = client.post('/api/subjects/enroll', json=payload)
    
    assert resposta.status_code == 201
    assert "Ana Beatriz" in json.loads(resposta.data)["mensagem"]


def test_broadcast_de_tarefa_para_a_turma(client):
    # Dispara uma tarefa para a disciplina 10 (Cálculo IV), onde o Aluno 1 está sentado
    payload = {"disciplina_id": 10, "titulo": "Lista de Integrais Triplas"}
    resposta = client.post('/api/assignments/broadcast', json=payload)
    
    assert resposta.status_code == 201
    assert "1 aluno(s)" in json.loads(resposta.data)["mensagem"]


def test_aluno_concluir_tarefa(client):
    # A tarefa 100 nasceu como 'Pendente' na Fixture. Vamos entregá-la!
    resposta = client.patch('/api/assignments/100/status')
    assert resposta.status_code == 200
    
    # Fazemos um SELECT direto no SQLite de teste para provar que a string mudou
    conn = sqlite3.connect(TEST_DB)
    status_banco = conn.execute("SELECT status FROM tarefas WHERE id = 100").fetchone()[0]
    conn.close()
    
    assert status_banco == "Entregue"