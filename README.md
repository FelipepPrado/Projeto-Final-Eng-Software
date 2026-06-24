# 🎓 Sistema de Gestão Acadêmica — IFCE

Plataforma web para gestão de disciplinas, turmas, matrículas e atividades acadêmicas, desenvolvida com arquitetura de microsserviços. Professores podem criar turmas, matricular alunos e disparar atividades. Alunos acompanham e entregam suas tarefas por um portal dedicado.

---

## 🏗️ Arquitetura

O sistema é composto por 3 microsserviços independentes e um frontend React, todos orquestrados via Docker Compose.

```
Frontend (React + Vite)
        │
        ├──► auth-service      :8081  → Cadastro, login e busca de usuários
        ├──► academic-service  :8082  → Disciplinas, turmas e matrículas
        └──► assignment-service:8083  → Tarefas e entregas
```

| Serviço | Stack | Responsabilidade |
|---|---|---|
| `auth-service` | Python + Flask | Gerenciamento de usuários, autenticação e autorização |
| `academic-service` | Python + Flask | Gestão de disciplinas, turmas e matrículas |
| `assignment-service` | Python + Flask | Gerenciamento de atividades, entregas e controle de notas |
| `frontend-web` | React + Vite + Nginx | Interface do Professor e do Aluno |

### Comunicação entre serviços

```
HomeProfessor
  ├── Criar disciplina    ──► academic-service
  ├── Matricular aluno    ──► academic-service ──► auth-service (resolve matrícula → ID)
  └── Disparar tarefa     ──► assignment-service ──► academic-service (busca alunos da turma)

HomeAluno
  └── Ver tarefas/abas    ──► assignment-service ──► auth-service + academic-service
```

---

## 📁 Estrutura do Projeto

```
plataforma/
├── .github/
│   └── workflows/
│       └── pipeline.yml          # Pipeline CI/CD
├── docker-compose.yml
└── services/
    ├── auth-service/
    │   ├── app.py
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   └── test_auth_service.py
    ├── academic-service/
    │   ├── app.py
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   └── test_academic_service.py
    ├── assignment-service/
    │   ├── app.py
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   └── test_assignment_service.py
    └── frontend-web/
        ├── src/
        │   ├── App.jsx
        │   ├── Login.jsx
        │   ├── Cadastro.jsx
        │   ├── HomeProfessor.jsx
        │   └── HomeAluno.jsx
        ├── Dockerfile
        └── .env.example
```

---

## 🚀 Como Rodar Localmente

### Pré-requisitos

- [Docker](https://www.docker.com/) instalado
- [Git](https://git-scm.com/) instalado

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio/plataforma
```

### 2. Configure as variáveis de ambiente do frontend

Crie o arquivo `.env` dentro de `services/frontend-web/`:

```bash
cp services/frontend-web/.env.example services/frontend-web/.env
```

O conteúdo para rodar localmente:

```env
VITE_AUTH_API=http://localhost:8081
VITE_ACADEMIC_API=http://localhost:8082
VITE_ASSIGN_API=http://localhost:8083
```

### 3. Suba todos os serviços

```bash
docker compose up --build
```

### 4. Acesse a aplicação

| Serviço | URL |
|---|---|
| Frontend | http://localhost:8080 |
| Auth Service | http://localhost:8081/health |
| Academic Service | http://localhost:8082/health |
| Assignment Service | http://localhost:8083/health |

---

## 🧪 Testes

Cada microsserviço possui sua própria suíte de testes unitários com `pytest`. Os testes usam um banco SQLite isolado em memória e mockam as chamadas HTTP entre serviços.

### Rodar os testes manualmente

```bash
# Auth Service
cd plataforma/services/auth-service
pip install -r requirements.txt pytest
pytest test_auth_service.py -v

# Academic Service
cd plataforma/services/academic-service
pip install -r requirements.txt pytest
pytest test_academic_service.py -v

# Assignment Service
cd plataforma/services/assignment-service
pip install -r requirements.txt pytest
pytest test_assignment_service.py -v
```

---

## ⚙️ Pipeline CI/CD

O projeto utiliza **GitHub Actions** com um pipeline dividido em CI e CD.

### CI — Integração Contínua

Roda automaticamente em todo `push` ou `pull request` na branch `main`. Os 3 jobs de teste rodam em paralelo:

```
push na main
     │
     ├── test-auth-service       → lint + pytest
     ├── test-academic-service   → lint + pytest  
     └── test-assignment-service → lint + pytest
```

### CD — Deploy Contínuo

Só executa **após todos os testes passarem** e apenas em `push` direto na `main` (não em PRs). Dispara o redeploy automático de cada serviço no Render via Deploy Hooks.

```
testes passaram
     │
     └── deploy
           ├── Auth Service      → Render Deploy Hook
           ├── Academic Service  → Render Deploy Hook
           ├── Assignment Service→ Render Deploy Hook
           └── Frontend          → Render Deploy Hook
```

### Secrets necessários no GitHub

Configure em **Settings → Secrets and variables → Actions**:

| Secret | Descrição |
|---|---|
| `RENDER_DEPLOY_HOOK_AUTH` | Deploy Hook do auth-service no Render |
| `RENDER_DEPLOY_HOOK_ACADEMIC` | Deploy Hook do academic-service no Render |
| `RENDER_DEPLOY_HOOK_ASSIGNMENT` | Deploy Hook do assignment-service no Render |
| `RENDER_DEPLOY_HOOK_FRONTEND` | Deploy Hook do frontend no Render |

---

## 👥 Perfis de Acesso

**Professor**
- Criar disciplinas
- Matricular alunos pelo número de matrícula acadêmica
- Disparar atividades para toda a turma de uma vez

**Aluno**
- Visualizar tarefas organizadas por disciplina
- Marcar tarefas como entregues
- Acompanhar pendências por aba

---

## 🛠️ Tecnologias Utilizadas

- **Frontend:** React, Vite, Nginx
- **Backend:** Python, Flask, Flask-CORS, SQLite
- **Testes:** Pytest, unittest.mock
- **Infraestrutura:** Docker, Docker Compose
- **CI/CD:** GitHub Actions, Render
