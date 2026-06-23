import os
import pytest
import json
import sqlite3

# Importamos o módulo app inteiro para podermos "hackear" a variável DB_PATH dele
import app as auth_app 

# O UNIVERSO PARALELO: Banco exclusivo para os testes rodarem
TEST_DB = '/tmp/test_pytest_auth.db'

@pytest.fixture
def client():
    # 1. Trava o Flask no modo teste e redireciona o banco para o arquivo isolado
    auth_app.app.config['TESTING'] = True
    auth_app.DB_PATH = TEST_DB

    # Garante que não ficou lixo de um teste anterior que crachou
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    with auth_app.app.app_context():
        auth_app.init_db()  # Cria a tabela estritamente vazia
        
        # 2. INJEÇÃO DE MOCKS: Criamos os ratos de laboratório para esta sessão
        conn = sqlite3.connect(TEST_DB)
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (id, nome, email, senha, tipo, matricula) VALUES (1, 'Pedro', 'pedro@ifce.edu.br', 'senha123', 'ALUNO', '20261045050012')")
        cur.execute("INSERT INTO usuarios (id, nome, email, senha, tipo, matricula) VALUES (2, 'Prof. Raimundo', 'raimundo@ifce.edu.br', 'senha123', 'PROFESSOR', '1234567')")
        conn.commit()
        conn.close()

    with auth_app.app.test_client() as client:
        yield client

    # 3. TEARDOWN: Acabou o teste? Joga a fita no lixo.
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


# ==========================================
# 🧪 OS TESTES (Cobrindo Caminho Feliz e Triste)
# ==========================================

def test_health_check(client):
    resposta = client.get('/health')
    assert resposta.status_code == 200
    assert "conectado" in json.loads(resposta.data)["status"]


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


def test_login_sucesso(client):
    payload = {"email": "pedro@ifce.edu.br", "senha": "senha123"}
    resposta = client.post('/api/login', json=payload)
    assert resposta.status_code == 200
    assert json.loads(resposta.data)["nome"] == "Pedro"


def test_login_senha_incorreta(client):
    payload = {"email": "pedro@ifce.edu.br", "senha": "senha_errada"}
    resposta = client.post('/api/login', json=payload)
    assert resposta.status_code == 401
    assert "incorretos" in json.loads(resposta.data)["erro"]


def test_criar_usuario_sucesso(client):
    novo_user = {
        "nome": "Estudante Teste",
        "email": "novo@ifce.edu.br",
        "senha": "123",
        "tipo": "ALUNO",
        "matricula": "20269999"
    }
    resposta = client.post('/api/users', json=novo_user)
    assert resposta.status_code == 201
    assert json.loads(resposta.data)["mensagem"] == "Usuário criado!"


def test_proibir_email_duplicado(client):
    # Tenta cadastrar com o e-mail do Pedro que já foi injetado no Mock
    user_repetido = {"nome": "Clone do Pedro", "email": "pedro@ifce.edu.br"}
    resposta = client.post('/api/users', json=user_repetido)
    assert resposta.status_code == 409


def test_buscar_por_matricula_aluno_sucesso(client):
    resposta = client.get('/api/users/matricula/20261045050012')
    assert resposta.status_code == 200
    assert json.loads(resposta.data)["nome"] == "Pedro"


def test_buscar_matricula_de_professor_deve_retornar_404(client):
    # A matrícula 1234567 pertence ao Prof. Raimundo. A rota de matrícula é restrita a alunos!
    resposta = client.get('/api/users/matricula/1234567')
    assert resposta.status_code == 404