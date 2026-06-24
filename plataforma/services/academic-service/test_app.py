import os
import pytest
import json
import sqlite3
from unittest.mock import patch, MagicMock

import app as academic_app

TEST_DB = '/tmp/test_pytest_academic.db'


@pytest.fixture
def client():
    academic_app.app.config['TESTING'] = True
    academic_app.DB_PATH = TEST_DB

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    with academic_app.app.app_context():
        academic_app.init_db()

        conn = sqlite3.connect(TEST_DB)
        cur = conn.cursor()

        # Professor ID 2 já tem uma disciplina criada
        cur.execute("INSERT INTO disciplinas (id, nome, professor_id) VALUES (10, 'Cálculo IV', 2)")

        # Aluno ID 1 já está matriculado nessa disciplina
        cur.execute("INSERT INTO matriculas (disciplina_id, aluno_id) VALUES (10, 1)")

        conn.commit()
        conn.close()

    with academic_app.app.test_client() as client:
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
# DISCIPLINAS
# ==========================================

def test_criar_disciplina_sucesso(client):
    payload = {"nome": "Física Quântica", "professor_id": 2}
    resposta = client.post('/api/academic/subjects', json=payload)
    assert resposta.status_code == 201
    dados = json.loads(resposta.data)
    assert dados["nome"] == "Física Quântica"
    assert dados["professor_id"] == 2


def test_criar_disciplina_sem_campos_obrigatorios(client):
    resposta = client.post('/api/academic/subjects', json={"nome": "Sem Professor"})
    assert resposta.status_code == 400


def test_proibir_disciplina_duplicada_mesmo_professor(client):
    # Cálculo IV já foi criado pelo Prof 2 na fixture
    payload = {"nome": "Cálculo IV", "professor_id": 2}
    resposta = client.post('/api/academic/subjects', json=payload)
    assert resposta.status_code == 409


def test_mesmo_nome_professor_diferente_permitido(client):
    # Outro professor pode ter uma disciplina com o mesmo nome
    payload = {"nome": "Cálculo IV", "professor_id": 99}
    resposta = client.post('/api/academic/subjects', json=payload)
    assert resposta.status_code == 201


def test_listar_disciplinas_do_professor(client):
    resposta = client.get('/api/academic/subjects/professor/2')
    assert resposta.status_code == 200
    dados = json.loads(resposta.data)
    assert len(dados) == 1
    assert dados[0]["nome"] == "Cálculo IV"


def test_listar_disciplinas_professor_sem_turmas(client):
    resposta = client.get('/api/academic/subjects/professor/999')
    assert resposta.status_code == 200
    assert json.loads(resposta.data) == []


def test_listar_disciplinas_do_aluno(client):
    # Aluno 1 está matriculado em Cálculo IV
    resposta = client.get('/api/academic/subjects/aluno/1')
    assert resposta.status_code == 200
    dados = json.loads(resposta.data)
    assert len(dados) == 1
    assert dados[0]["nome"] == "Cálculo IV"


def test_listar_disciplinas_aluno_sem_matriculas(client):
    resposta = client.get('/api/academic/subjects/aluno/999')
    assert resposta.status_code == 200
    assert json.loads(resposta.data) == []


# ==========================================
# MATRÍCULAS
# ==========================================

@patch('app.requests.get')
def test_matricular_aluno_sucesso(mock_get, client):
    # auth-service resolve a matrícula para o Aluno ID 5 (Ana Beatriz)
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 5, "nome": "Ana Beatriz"}

    payload = {"disciplina_id": 10, "matricula": "2026999"}
    resposta = client.post('/api/academic/enroll', json=payload)

    assert resposta.status_code == 201
    assert "Ana Beatriz" in json.loads(resposta.data)["mensagem"]


@patch('app.requests.get')
def test_matricular_aluno_ja_matriculado(mock_get, client):
    # Aluno ID 1 já está na fixture matriculado em Cálculo IV
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 1, "nome": "Pedro"}

    payload = {"disciplina_id": 10, "matricula": "20261045050012"}
    resposta = client.post('/api/academic/enroll', json=payload)

    assert resposta.status_code == 409
    assert "Pedro" in json.loads(resposta.data)["erro"]


@patch('app.requests.get')
def test_matricular_com_matricula_inexistente(mock_get, client):
    # auth-service não acha a matrícula digitada
    mock_get.return_value.status_code = 404

    payload = {"disciplina_id": 10, "matricula": "0000000"}
    resposta = client.post('/api/academic/enroll', json=payload)

    assert resposta.status_code == 404


@patch('app.requests.get')
def test_matricular_em_disciplina_inexistente(mock_get, client):
    # auth-service resolve o aluno, mas a disciplina 999 não existe
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 5, "nome": "Ana Beatriz"}

    payload = {"disciplina_id": 999, "matricula": "2026999"}
    resposta = client.post('/api/academic/enroll', json=payload)

    assert resposta.status_code == 404


def test_matricular_sem_campos_obrigatorios(client):
    resposta = client.post('/api/academic/enroll', json={"disciplina_id": 10})
    assert resposta.status_code == 400


# ==========================================
# LISTAR ALUNOS DA DISCIPLINA (usado pelo assignment-service)
# ==========================================

def test_listar_alunos_da_disciplina(client):
    resposta = client.get('/api/academic/subjects/10/alunos')
    assert resposta.status_code == 200
    alunos = json.loads(resposta.data)
    assert 1 in alunos  # Aluno ID 1 está matriculado na fixture


def test_listar_alunos_disciplina_vazia(client):
    # Cria uma disciplina sem alunos e verifica que retorna lista vazia
    conn = sqlite3.connect(TEST_DB)
    conn.execute("INSERT INTO disciplinas (id, nome, professor_id) VALUES (20, 'Vazia', 2)")
    conn.commit()
    conn.close()

    resposta = client.get('/api/academic/subjects/20/alunos')
    assert resposta.status_code == 200
    assert json.loads(resposta.data) == []