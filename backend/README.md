# EyesOnAsset API - Backend

API REST para gestão de ativos físicos e seus responsáveis, desenvolvida com FastAPI e SQLAlchemy.

![Tests](https://img.shields.io/badge/tests-127%20passed-success)
![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688)
![JWT](https://img.shields.io/badge/auth-JWT-orange)
![Security](https://img.shields.io/badge/security-bcrypt-red)

## ✨ Features

- ✅ **Validação com Pydantic**: Schemas robustos com validação automática
- ✅ **Persistência com SQLAlchemy**: ORM moderno com suporte a CASCADE DELETE
- ✅ **Testes Unitários**: 127 testes com 94% de cobertura
- ✅ **Autenticação JWT**: Proteção de rotas com tokens JWT (HS256)
- ✅ **Usuários com bcrypt**: Hash seguro de senhas com bcrypt
- ✅ **CRUD Completo**: Operações para owners, assets e users
- ✅ **Docker Ready**: Containerização completa com Docker Compose
- 🔄 **Documentação automática**: Swagger UI e ReDoc
- 🔄 **API RESTful**: Endpoints padronizados e intuitivos

## 📋 Requisitos

### Opção 1: Docker (Recomendado)
- Docker 20.10+
- Docker Compose 1.29+

### Opção 2: Python Local
- Python 3.10+
- SQLite (incluído no Python)

## 🚀 Quick Start

### Com Docker (Recomendado)

```bash
# 1. Build da imagem
cd backend
docker-compose build

# 2. Iniciar servidor
docker-compose up -d

# 3. Criar usuário padrão
docker-compose exec backend python create_default_user.py

# 4. Acessar documentação
# http://localhost:8000/docs
```

### Sem Docker

```bash
# 1. Criar ambiente virtual
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Criar usuário padrão
python create_default_user.py

# 4. Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**📖 Para instruções detalhadas, consulte [SETUP.md](SETUP.md)**

## 📚 Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗄️ Estrutura do Banco de Dados

O sistema utiliza SQLite com as seguintes tabelas:

### Tabela: `users` (Usuários)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | VARCHAR(36) | UUID gerado automaticamente |
| username | VARCHAR(140) | Nome de usuário (obrigatório, único) |
| hashed_password | VARCHAR | Hash bcrypt da senha (obrigatório) |

### Tabela: `owners` (Responsáveis)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | VARCHAR(36) | UUID gerado automaticamente |
| name | VARCHAR(140) | Nome completo (obrigatório) |
| email | VARCHAR(140) | Email corporativo (obrigatório, único) |
| phone | VARCHAR(20) | Telefone (obrigatório) |

### Tabela: `assets` (Ativos)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | VARCHAR(36) | UUID gerado automaticamente |
| name | VARCHAR(140) | Nome do ativo (obrigatório) |
| category | VARCHAR(60) | Categoria do ativo (obrigatório) |
| owner | VARCHAR(36) | FK para owners.id (CASCADE DELETE) |

## 🛣️ Rotas da API

### 🔐 Autenticação

Todas as rotas da API (exceto a rota de autenticação) requerem um token JWT válido no header `Authorization`.

#### POST /integrations/auth
Endpoint de autenticação que retorna um token JWT.

**Credenciais padrão:**
- Username: `eyesonasset`
- Password: `eyesonasset`

**Request Body (form-data):**
```
login: eyesonasset
password: eyesonasset
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 60
}
```

**Response (401 - Credenciais inválidas):**
```json
{
  "detail": "Credenciais inválidas"
}
```

**⚠️ Importante:**
- O token expira em **60 segundos (1 minuto)**
- Use o token no header: `Authorization: Bearer {token}`
- Credenciais fixas: `login=eyesonasset`, `password=eyesonasset`

**Exemplo de uso com curl:**
```bash
# 1. Obter o token
curl -X POST "http://localhost:8000/integrations/auth" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "login=eyesonasset&password=eyesonasset"

# 2. Usar o token nas requisições
curl -X GET "http://localhost:8000/integrations/owners" \
  -H "Authorization: Bearer {seu-token-aqui}"
```

**Exemplo com Python:**
```python
import requests

# 1. Autenticar
response = requests.post(
    "http://localhost:8000/integrations/auth",
    data={"login": "eyesonasset", "password": "eyesonasset"}
)
token = response.json()["access_token"]

# 2. Usar o token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/integrations/owners",
    headers=headers
)
```

### Owners (Responsáveis)

**⚠️ Todas as rotas abaixo requerem autenticação JWT**

#### POST /integrations/owner
Cria um novo responsável.

**Request Body:**
```json
{
  "name": "João da Silva",
  "email": "joao.silva@empresa.com",
  "phone": "+55 11 98765-4321"
}
```

**Response (201):**
```json
{
  "id": "uuid-gerado-automaticamente",
  "name": "João da Silva",
  "email": "joao.silva@empresa.com",
  "phone": "+55 11 98765-4321"
}
```

#### GET /integrations/owner/{owner_id}
Busca um responsável por ID.

**Response (200):**
```json
{
  "id": "uuid-do-owner",
  "name": "João da Silva",
  "email": "joao.silva@empresa.com",
  "phone": "+55 11 98765-4321"
}
```

#### GET /integrations/owners
Lista todos os responsáveis (com paginação).

**Query Parameters:**
- `skip`: Número de registros a pular (padrão: 0)
- `limit`: Número máximo de registros (padrão: 100)

#### PUT /integrations/owner/{owner_id}
Atualiza um responsável existente.

**Request Body (campos opcionais):**
```json
{
  "name": "João da Silva Jr.",
  "phone": "+55 11 99999-9999"
}
```

#### DELETE /integrations/owner/{owner_id}
Deleta um responsável e todos os seus ativos (CASCADE DELETE).

**Response:** 204 No Content

⚠️ **ATENÇÃO**: Esta operação também deletará todos os ativos associados a este responsável.

### Assets (Ativos)

**⚠️ Todas as rotas abaixo requerem autenticação JWT**

#### POST /integrations/asset
Cria um novo ativo.

**Request Body:**
```json
{
  "name": "Aeronave Boeing 737",
  "category": "Aeronave",
  "owner": "uuid-do-owner"
}
```

**Response (201):**
```json
{
  "id": "uuid-gerado-automaticamente",
  "name": "Aeronave Boeing 737",
  "category": "Aeronave",
  "owner": "uuid-do-owner"
}
```

#### GET /integrations/asset/{asset_id}
Busca um ativo por ID.

#### GET /integrations/assets
Lista todos os ativos (com paginação).

**Query Parameters:**
- `skip`: Número de registros a pular (padrão: 0)
- `limit`: Número máximo de registros (padrão: 100)

#### PUT /integrations/asset/{asset_id}
Atualiza um ativo existente.

**Request Body (campos opcionais):**
```json
{
  "name": "Aeronave Boeing 777",
  "category": "Aeronave Comercial"
}
```

#### DELETE /integrations/asset/{asset_id}
Deleta um ativo.

**Response:** 204 No Content

## ✅ Funcionalidades Implementadas

### Nível 1 - Validação ✓
- [x] Validação completa de dados com Pydantic
- [x] Mensagens de erro claras e específicas
- [x] Validação de tipos (UUID, strings com limites)
- [x] Campos obrigatórios
- [x] Validação de email

### Nível 2 - Persistência ✓
- [x] Integração com SQLAlchemy
- [x] Banco de dados SQLite
- [x] IDs gerados automaticamente (UUID)
- [x] CRUD completo para Assets
- [x] CRUD completo para Owners
- [x] Relacionamento entre tabelas (Foreign Key)
- [x] **CASCADE DELETE**: Deletar owner deleta automaticamente seus assets
- [x] Validação de email único
- [x] Paginação em listagens

### Nível 3 - Testes ✓
- [x] **127 testes unitários** com pytest
- [x] **94% de cobertura** de código
- [x] Testes para modelos (SQLAlchemy)
- [x] Testes para schemas (Pydantic)
- [x] Testes para serviços (lógica de negócio)
- [x] Testes para rotas da API (integração)
- [x] Testes de autenticação JWT
- [x] Testes de usuários e bcrypt
- [x] Fixtures compartilhadas (conftest.py)
- [x] Banco de dados em memória para testes
- [x] Relatório de cobertura HTML
- [x] Isolamento entre testes

### Nível 4 - Autenticação JWT ✓
- [x] **Autenticação via token JWT** (HS256)
- [x] **Proteção de todas as rotas** (exceto /auth)
- [x] **Expiração de tokens** (1 minuto)
- [x] **18 testes de autenticação**
- [x] Validação de tokens inválidos/expirados
- [x] Middleware de autenticação personalizado
- [x] Headers Authorization com Bearer token
- [x] Mensagens de erro adequadas (401/403)

### Nível 5 - Usuários ✓
- [x] **Entidade User** com hash bcrypt
- [x] **Autenticação via banco de dados**
- [x] **CRUD completo de usuários**
- [x] **34 novos testes** (service + API)
- [x] Hash seguro de senhas (bcrypt)
- [x] Validação de username único
- [x] Endpoint de gerenciamento de usuários
- [x] Script de criação de usuário padrão

### Nível 6 - Infraestrutura e Documentação ✓
- [x] **Dockerfile** otimizado para produção
- [x] **docker-compose.yaml** com hot reload
- [x] **Documentação completa** de setup e deploy
- [x] **.dockerignore** para builds eficientes
- [x] **.env.example** com variáveis de ambiente
- [x] **Health checks** configurados
- [x] **Volume persistente** para banco de dados
- [x] **Guia de troubleshooting** completo

## 🧪 Testes

### Executar todos os testes

```bash
# No diretório backend
pytest
```

### Executar testes com cobertura detalhada

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

Após executar, abra `htmlcov/index.html` no navegador para visualizar o relatório detalhado de cobertura.

### Executar testes específicos

```bash
# Apenas testes de modelos
pytest tests/test_models.py

# Apenas testes de schemas
pytest tests/test_schemas.py

# Apenas testes de serviços
pytest tests/test_services.py

# Apenas testes de API
pytest tests/test_api_owners.py tests/test_api_assets.py

# Um teste específico
pytest tests/test_models.py::TestOwnerModel::test_create_owner
```

### Estrutura dos Testes

```
tests/
├── conftest.py              # Fixtures compartilhadas (cria user padrão)
├── test_models.py           # Testes dos modelos SQLAlchemy (11 testes)
├── test_schemas.py          # Testes dos schemas Pydantic (14 testes)
├── test_services.py         # Testes da camada de serviço (19 testes)
├── test_user_service.py     # Testes do UserService (16 testes)
├── test_api_owners.py       # Testes das rotas de owners (15 testes)
├── test_api_assets.py       # Testes das rotas de assets (16 testes)
├── test_api_users.py        # Testes das rotas de users (18 testes)
└── test_auth.py             # Testes de autenticação JWT (18 testes)
```

### Cobertura de Testes

**Total: 127 testes | 94% de cobertura**

| Módulo | Cobertura | Detalhes |
|--------|-----------|----------|
| **Models** | 90-100% | Modelos SQLAlchemy (User, Owner, Asset) |
| **Services** | 93-100% | Lógica de negócio (CRUD + Auth) |
| **API Routes** | 96-100% | Endpoints REST |
| **Security** | 94% | JWT + bcrypt |
| **Schemas** | 82-100% | Validação Pydantic |
| **Database** | 100% | Configuração e sessões |

### O que é testado

#### ✅ Modelos (test_models.py)
- Criação de registros
- Geração automática de UUIDs
- Validação de campos obrigatórios
- Constraint de email único
- CASCADE DELETE (deletar owner deleta assets)
- Foreign key constraints
- Representação string (`__repr__`)

#### ✅ Schemas (test_schemas.py)
- Validação de dados de entrada
- Validação de email
- Limites de caracteres (name: 140, category: 60)
- Campos obrigatórios
- Atualização parcial (campos opcionais)
- Schemas de resposta com ID

#### ✅ Services (test_services.py)
- CRUD completo (Create, Read, Update, Delete)
- Paginação (skip/limit)
- Email único para owners
- Validação de owner existente ao criar asset
- Retorno None para registros não encontrados

#### ✅ API - Owners (test_api_owners.py)
- `POST /integrations/owner` - Criar owner
- `GET /integrations/owner/{id}` - Buscar owner
- `GET /integrations/owners` - Listar owners com paginação
- `PUT /integrations/owner/{id}` - Atualizar owner
- `DELETE /integrations/owner/{id}` - Deletar owner (CASCADE)
- Validações de email duplicado
- Códigos HTTP corretos (201, 200, 204, 404, 400, 422)

#### ✅ API - Assets (test_api_assets.py)
- `POST /integrations/asset` - Criar asset
- `GET /integrations/asset/{id}` - Buscar asset
- `GET /integrations/assets` - Listar assets com paginação
- `PUT /integrations/asset/{id}` - Atualizar asset
- `DELETE /integrations/asset/{id}` - Deletar asset
- Validação de owner existente
- Validação de limites de caracteres
- Relacionamento com owner

### Fixtures Disponíveis

```python
# Sessão de banco de dados em memória (isolada para cada teste)
# Cria automaticamente o usuário padrão (eyesonasset/eyesonasset)
def test_example(db_session):
    ...

# Cliente de teste da API
def test_example(client):
    response = client.get("/integrations/owners")
    ...

# Headers com token JWT válido
def test_example(auth_headers):
    response = client.post("/integrations/owner", json=data, headers=auth_headers)
    ...

# Owner já criado no banco
def test_example(created_owner):
    owner_id = created_owner["id"]
    ...

# Asset já criado no banco (com owner)
def test_example(created_asset):
    asset_id = created_asset["id"]
    ...
```

## 🚀 Quick Start

### Rodar testes do Nível 1
```bash
python test_nivel1.py
```

### Rodar testes do Nível 2
```bash
python test_nivel2.py
```

### Rodar testes do Nível 3 (Testes Unitários)
```bash
pytest
```

## 🏗️ Estrutura do Projeto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicação principal FastAPI
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py         # Autenticação JWT
│   │       ├── users.py        # Rotas de usuários (CRUD)
│   │       ├── assets.py       # Rotas de assets
│   │       └── owners.py       # Rotas de owners
│   ├── core/
│   │   ├── auth.py            # Middleware JWT
│   │   ├── config.py          # Configurações da aplicação
│   │   └── security.py        # JWT + bcrypt utilities
│   ├── db/
│   │   ├── base.py            # Configuração do SQLAlchemy
│   │   ├── sessions.py        # Dependency de sessão do DB
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── user.py        # Modelo User
│   │       ├── asset.py       # Modelo Asset
│   │       └── owner.py       # Modelo Owner
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py           # Schemas de autenticação
│   │   ├── user.py           # Schemas Pydantic de User
│   │   ├── asset.py          # Schemas Pydantic de Asset
│   │   └── owner.py          # Schemas Pydantic de Owner
│   └── services/
│       ├── user_service.py   # Lógica de negócio de Users
│       ├── asset_service.py  # Lógica de negócio de Assets
│       └── owner_service.py  # Lógica de negócio de Owners
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Fixtures compartilhadas
│   ├── test_auth.py          # Testes de autenticação (18 testes)
│   ├── test_models.py        # Testes dos modelos (11 testes)
│   ├── test_schemas.py       # Testes dos schemas (14 testes)
│   ├── test_services.py      # Testes dos serviços (19 testes)
│   ├── test_user_service.py  # Testes UserService (16 testes)
│   ├── test_api_users.py     # Testes API users (18 testes)
│   ├── test_api_owners.py    # Testes API owners (15 testes)
│   └── test_api_assets.py    # Testes API assets (16 testes)
├── Dockerfile                # Imagem Docker da aplicação
├── docker-compose.yaml       # Orquestração de containers
├── .dockerignore            # Arquivos ignorados no build
├── .env.example             # Exemplo de variáveis de ambiente
├── pytest.ini               # Configuração do pytest
├── requirements.txt         # Dependências Python
├── create_default_user.py   # Script de criação do usuário padrão
├── SETUP.md                 # Guia completo de setup e deploy
└── assets.db               # Banco de dados SQLite (gerado automaticamente)
```

## 🐳 Docker

### Comandos Principais

```bash
# Build e iniciar
docker-compose up --build -d

# Ver logs
docker-compose logs -f backend

# Executar comandos no container
docker-compose exec backend python create_default_user.py

# Parar containers
docker-compose down

# Executar testes
docker-compose run --rm backend pytest tests/ -v --cov=app
```

### Estrutura Docker

- **Dockerfile**: Imagem base Python 3.10-slim com otimizações
- **docker-compose.yaml**: Serviços backend + testes
- **Volume persistente**: Banco de dados mantido em `./data`
- **Hot reload**: Código sincronizado para desenvolvimento
- **Health checks**: Monitoramento automático de saúde

## 🔍 Detalhes Técnicos

### Cascade Delete
O sistema implementa CASCADE DELETE através de:

1. **Modelo Owner** (`app/db/models/owner.py`):
```python
assets = relationship(
    "Asset",
    back_populates="owner_rel",
    cascade="all, delete-orphan",
    passive_deletes=True
)
```

2. **Modelo Asset** (`app/db/models/asset.py`):
```python
owner = Column(
    String(36), 
    ForeignKey("owners.id", ondelete="CASCADE"), 
    nullable=False
)
```

Isso garante que ao deletar um Owner, todos os seus Assets sejam automaticamente deletados.

### Validações
- Email único (constraint no banco + validação na camada de serviço)
- Owner deve existir ao criar/atualizar Asset
- Todos os campos obrigatórios validados
- Limites de caracteres respeitados

## 📝 Próximos Passos

- [ ] Nível 4: Autenticação JWT
- [ ] Nível 5: Usuários e login via banco
- [ ] Nível 6: Docker e documentação completa

---

## 📊 Estatísticas do Projeto

- **Linhas de código**: ~1.500
- **Testes**: 75
- **Cobertura**: 91%
- **Endpoints**: 10 (5 owners + 5 assets)
- **Modelos**: 3 (Owner, Asset, User)
- **Tempo de execução dos testes**: ~1.6s
