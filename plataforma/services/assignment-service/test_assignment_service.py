import os
import pytest
import json
import sqlite3
from unittest.mock import patch

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

        conn = sqlite3.connect(TEST_DB)
        cur = conn.cursor()

        # Tarefa do Aluno ID 1 em Cálculo IV
        cur.execute("""
            INSERT INTO tarefas (id, usuario_id, disciplina_id, disciplina, titulo, status)
            VALUES (100, 1, 10, 'Cálculo IV', 'Resolver derivadas parciais', 'Pendente')
        """)

        conn.commit()
        conn.close()

    with assign_app.app.test_client() as client:
        yield client

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


# ==========================================
# HEALTH CHECK
# ==========================================

def test_health_check(client):
    resposta = client.get('/health')
    assert resposta.status_code == 200
    assert "Operacional" in json.loads(resposta.data)["status"]


# ==========================================
# PAINEL DO ALUNO
# ==========================================

@patch('app.requests.get')
def test_get_user_assignments_sucesso(mock_get, client):
    # Mock 1: auth-service retorna dados do aluno
    # Mock 2: academic-service retorna disciplinas matriculadas
    def side_effect(url, timeout=5):
        mock = MagicMock()
        if 'auth' in url or '8081' in url or f'/api/users/1' in url:
            mock.status_code = 200
            mock.ok = True
            mock.json.return_value = {
                "nome": "Pedro Miguel",
                "email": "pedro@ifce.edu.br",
                "matricula": "20261045050012"
            }
        else:
            # academic-service retorna disciplinas
            mock.status_code = 200
            mock.ok = True
            mock.json.return_value = [{"id": 10, "nome": "Cálculo IV"}]
        return mock

    mock_get.side_effect = side_effect

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
    mock_get.return_value.ok = False

    resposta = client.get('/api/assignments/999')
    assert resposta.status_code == 404
    assert "encontrado" in json.loads(resposta.data)["erro"]


# ==========================================
# BROADCAST DE TAREFA
# ==========================================

@patch('app.requests.get')
def test_broadcast_tarefa_para_turma(mock_get, client):
    # academic-service retorna lista de alunos da disciplina 10
    mock_get.return_value.status_code = 200
    mock_get.return_value.ok = True
    mock_get.return_value.json.return_value = [1, 2, 3]  # 3 alunos

    payload = {
        "disciplina_id": "10",
        "disciplina_nome": "Cálculo IV",
        "titulo": "Lista de Integrais Triplas"
    }
    resposta = client.post('/api/assignments/broadcast', json=payload)

    assert resposta.status_code == 201
    assert "3 aluno(s)" in json.loads(resposta.data)["mensagem"]


@patch('app.requests.get')
def test_broadcast_turma_vazia(mock_get, client):
    # academic-service retorna lista vazia
    mock_get.return_value.status_code = 200
    mock_get.return_value.ok = True
    mock_get.return_value.json.return_value = []

    payload = {
        "disciplina_id": "10",
        "disciplina_nome": "Cálculo IV",
        "titulo": "Tarefa Sem Alunos"
    }
    resposta = client.post('/api/assignments/broadcast', json=payload)
    assert resposta.status_code == 400


def test_broadcast_sem_campos_obrigatorios(client):
    resposta = client.post('/api/assignments/broadcast', json={"titulo": "Sem disciplina"})
    assert resposta.status_code == 400


# ==========================================
# ENTREGAR TAREFA
# ==========================================

def test_aluno_entregar_tarefa(client):
    resposta = client.patch('/api/assignments/100/status')
    assert resposta.status_code == 200

    # Confirma direto no banco que o status mudou
    conn = sqlite3.connect(TEST_DB)
    status = conn.execute("SELECT status FROM tarefas WHERE id = 100").fetchone()[0]
    conn.close()

    assert status == "Entregue"


def test_entregar_tarefa_inexistente(client):
    # Deve retornar 200 mesmo sem achar (UPDATE não lança erro no SQLite)
    # mas nenhuma linha é afetada — comportamento esperado documentado aqui
    resposta = client.patch('/api/assignments/999/status')
    assert resposta.status_code == 200


# ==========================================
# IMPORT NECESSÁRIO PARA O SIDE EFFECT
# ==========================================
from unittest.mock import MagicMock