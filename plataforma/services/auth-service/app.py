from flask import Flask, jsonify

app = Flask(__name__)

# Endpoint básico para o Health Check (útil para testes e observabilidade no futuro)
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Auth Service funcionando perfeitamente!"}), 200

# Endpoint REST que o academic-service vai consumir depois
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Simulando um banco de dados temporário para a Sprint 2
    banco_de_usuarios = {
        1: {"id": 1, "nome": "Carlos", "email": "carlos@ifce.edu.br", "tipo": "ALUNO"},
        2: {"id": 2, "nome": "Prof. Ana", "email": "ana@ifce.edu.br", "tipo": "PROFESSOR"}
    }
    
    usuario = banco_de_usuarios.get(user_id)
    
    if usuario:
        return jsonify(usuario), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404

if __name__ == '__main__':
    # Roda na porta 8081, que é a mesma que mapeamos no docker-compose
    app.run(host='0.0.0.0', port=8081)