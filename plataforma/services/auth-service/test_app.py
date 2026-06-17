import pytest
import json
from app import app, init_db

# Fixture: Prepara o ambiente antes de executar os testes
@pytest.fixture
def client():
    # Configura o Flask para o modo de testes
    app.config['TESTING'] = True
    
    # Inicializa o banco SQLite em memória com os dados iniciais
    with app.app_context():
        init_db()
        
    # Cria um cliente para simular as requisições HTTP
    with app.test_client() as client:
        yield client

# Teste 1: Verifica se o Health Check retorna 200 OK
def test_health_check(client):
    resposta = client.get('/health')
    assert resposta.status_code == 200
    
    dados = json.loads(resposta.data)
    assert dados["status"] == "Auth Service conectado ao SQLite!"

# Teste 2: Verifica a busca por um utilizador existente (Carlos, ID 1)
def test_get_user_sucesso(client):
    resposta = client.get('/api/users/1')
    assert resposta.status_code == 200
    
    dados = json.loads(resposta.data)
    assert dados["nome"] == "Carlos"
    assert dados["tipo"] == "ALUNO"

# Teste 3: Verifica o comportamento para um utilizador inexistente (Erro 404)
def test_get_user_nao_encontrado(client):
    resposta = client.get('/api/users/999')
    assert resposta.status_code == 404
    
    dados = json.loads(resposta.data)
    assert dados["erro"] == "Usuário não encontrado"