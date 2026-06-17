import pytest
import json
from unittest.mock import patch
from app import app, init_db

# Prepara o ambiente de testes e o banco SQLite em memória
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.app_context():
        init_db()
    with app.test_client() as client:
        yield client

# Teste 1: Health Check
def test_health_check(client):
    resposta = client.get('/health')
    assert resposta.status_code == 200
    
    dados = json.loads(resposta.data)
    assert dados["status"] == "Assignment Service conectado ao SQLite!"

# Teste 2: Simula sucesso na comunicação com o auth-service
@patch('app.requests.get')
def test_get_user_assignments_sucesso(mock_get, client):
    # Configura o "falso" auth-service para retornar Status 200 e os dados do Carlos
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "nome": "Carlos",
        "email": "carlos@ifce.edu.br"
    }

    resposta = client.get('/api/assignments/1')
    assert resposta.status_code == 200
    
    dados = json.loads(resposta.data)
    assert dados["aluno"] == "Carlos"
    # Verifica se ele puxou as tarefas do banco de dados local corretamente
    assert len(dados["tarefas"]) == 2
    assert dados["tarefas"][0]["disciplina"] == "DevOps"

# Teste 3: Simula falha quando o auth-service não encontra o usuário
@patch('app.requests.get')
def test_get_user_assignments_nao_encontrado(mock_get, client):
    # Configura o "falso" auth-service para retornar Status 404
    mock_get.return_value.status_code = 404

    resposta = client.get('/api/assignments/999')
    assert resposta.status_code == 404
    
    dados = json.loads(resposta.data)
    assert dados["erro"] == "Usuário não encontrado no Auth Service."