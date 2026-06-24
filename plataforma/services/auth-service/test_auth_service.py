import os
import pytest
import json
import sqlite3

import app as auth_app

TEST_DB = '/tmp/test_pytest_auth.db'


@pytest.fixture
def client():
    auth_app.app.config['TESTING'] = True
    auth_app.DB_PATH = TEST_DB

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    with auth_app.app.app_context():
        auth_app.init_db()

        conn = sqlite3.connect(TEST_DB)
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (id, nome, email, senha, tipo, matricula) VALUES (1, 'Pedro', 'pedro@ifce.edu.br', 'senha123', 'ALUNO', '20261045050012')")
        cur.execute("INSERT INTO usuarios (id, nome, email, senha, tipo, matricula) VALUES (2, 'Prof. Raimundo', 'raimundo@ifce.edu.br', 'senha123', 'PROFESSOR', '1234567')")
        conn.commit()
        conn.close()

    with auth_app.app.test_client() as client:
        yield client

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


# ==========================================
# HEALTH CHECK
# ==========================================

def test_health_check(client):
    resposta = client.get('/health')
    assert resposta.status_code == 200
    # Novo auth-service retorna "Auth Service Operacional!"
    assert "Operacional" in json.loads(resposta.data)["status"]


# ==========================================
# BUSCA DE USUÁRIO POR ID
# ==========================================

def test_get_user_sucesso(client):
    resposta = client.get('/api/users/1')
    assert resposta.status_code == 200
    dados = json.loads(resposta.data)
    assert dados["nome"] == "Pedro"
    assert dados["tipo"] == "ALUNO"
    assert dados["matricula"] == "20261045050012"


def test_get_user_nao_encontrado(client):
    resposta = client.get('/api/users/999')
    assert resposta.status_code == 404


# ==========================================
# LOGIN
# ==========================================

def test_login_sucesso(client):
    payload = {"email": "pedro@ifce.edu.br", "senha": "senha123"}
    resposta = client.post('/api/login', json=payload)
    assert resposta.status_code == 200
    dados = json.loads(resposta.data)
    assert dados["nome"] == "Pedro"
    assert dados["tipo"] == "ALUNO"


def test_login_senha_incorreta(client):
    payload = {"email": "pedro@ifce.edu.br", "senha": "senha_errada"}
    resposta = client.post('/api/login', json=payload)
    assert resposta.status_code == 401
    assert "incorretos" in json.loads(resposta.data)["erro"]


def test_login_email_inexistente(client):
    payload = {"email": "fantasma@ifce.edu.br", "senha": "qualquer"}
    resposta = client.post('/api/login', json=payload)
    assert resposta.status_code == 401


# ==========================================
# CADASTRO
# ==========================================

def test_criar_usuario_aluno_sucesso(client):
    novo_user = {
        "nome": "Estudante Teste",
        "email": "novo@ifce.edu.br",
        "senha": "123",
        "tipo": "ALUNO",
        "matricula": "20269999"
    }
    resposta = client.post('/api/users', json=novo_user)
    assert resposta.status_code == 201
    dados = json.loads(resposta.data)
    assert dados["nome"] == "Estudante Teste"
    assert dados["matricula"] == "20269999"


def test_criar_usuario_professor_sem_matricula(client):
    # Professor pode cadastrar sem matrícula
    novo_prof = {
        "nome": "Prof. Ana",
        "email": "ana@ifce.edu.br",
        "senha": "123",
        "tipo": "PROFESSOR"
    }
    resposta = client.post('/api/users', json=novo_prof)
    assert resposta.status_code == 201


def test_criar_aluno_sem_matricula_deve_falhar(client):
    # Aluno sem matrícula deve ser rejeitado
    payload = {
        "nome": "Aluno Sem Matrícula",
        "email": "semmat@ifce.edu.br",
        "senha": "123",
        "tipo": "ALUNO"
    }
    resposta = client.post('/api/users', json=payload)
    assert resposta.status_code == 400


def test_proibir_email_duplicado(client):
    user_repetido = {
        "nome": "Clone do Pedro",
        "email": "pedro@ifce.edu.br",
        "senha": "123",
        "tipo": "ALUNO",
        "matricula": "99999999"
    }
    resposta = client.post('/api/users', json=user_repetido)
    assert resposta.status_code == 409


def test_criar_usuario_sem_campos_obrigatorios(client):
    resposta = client.post('/api/users', json={"nome": "Incompleto"})
    assert resposta.status_code == 400


# ==========================================
# BUSCA POR MATRÍCULA
# ==========================================

def test_buscar_por_matricula_aluno_sucesso(client):
    resposta = client.get('/api/users/matricula/20261045050012')
    assert resposta.status_code == 200
    dados = json.loads(resposta.data)
    assert dados["nome"] == "Pedro"
    assert dados["matricula"] == "20261045050012"


def test_buscar_matricula_de_professor_deve_retornar_404(client):
    # Rota de matrícula é restrita a alunos
    resposta = client.get('/api/users/matricula/1234567')
    assert resposta.status_code == 404


def test_buscar_matricula_inexistente(client):
    resposta = client.get('/api/users/matricula/00000000')
    assert resposta.status_code == 404