# 🚀 Guia de Setup e Deploy - EyesOnAsset Backend

Este guia contém instruções completas para configurar, executar e testar o projeto em diferentes ambientes.

---

## 📋 Pré-requisitos

Escolha **uma** das opções abaixo:

### Opção 1: Docker (Recomendado)
- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 1.29+

### Opção 2: Python Local
- Python 3.10+
- pip (gerenciador de pacotes Python)
- SQLite (incluído no Python)

---

## 🐳 Método 1: Executar com Docker (Recomendado)

### 1. Build da Imagem

```bash
cd backend
docker-compose build
```

### 2. Iniciar o Servidor

```bash
docker-compose up
```

Ou em modo detached (background):

```bash
docker-compose up -d
```

### 3. Criar Usuário Padrão

```bash
docker-compose exec backend python create_default_user.py
```

### 4. Verificar se está rodando

Acesse: http://localhost:8000/docs

### 5. Ver Logs

```bash
docker-compose logs -f backend
```

### 6. Parar o Servidor

```bash
docker-compose down
```

### 7. Executar Testes no Docker

```bash
docker-compose run --rm backend-test
```

Ou sem usar o profile:

```bash
docker-compose run --rm backend pytest tests/ -v --cov=app
```

---

## 💻 Método 2: Executar Localmente (Sem Docker)

### 1. Criar Ambiente Virtual

```bash
cd backend

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Criar Usuário Padrão

```bash
python create_default_user.py
```

**Saída esperada:**
```
✓ Usuário padrão criado com sucesso!
  ID: <uuid>
  Username: eyesonasset
```

### 4. Iniciar o Servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Saída esperada:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 5. Verificar se está rodando

Acesse: http://localhost:8000/docs

---

## 🧪 Executar Testes

### Com Docker

```bash
# Executar todos os testes
docker-compose run --rm backend pytest tests/ -v

# Com cobertura
docker-compose run --rm backend pytest tests/ --cov=app --cov-report=term-missing

# Com relatório HTML
docker-compose run --rm backend pytest tests/ --cov=app --cov-report=html
```

### Localmente

```bash
# Ativar ambiente virtual primeiro
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Executar todos os testes
pytest

# Com verbosidade
pytest -v

# Com cobertura detalhada
pytest --cov=app --cov-report=term-missing --cov-report=html

# Executar testes específicos
pytest tests/test_models.py
pytest tests/test_api_users.py -v
pytest tests/test_auth.py::test_login_success

# Ver relatório HTML de cobertura
# Após executar com --cov-report=html
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Testes Esperados

```
✅ 127 testes passando
✅ 94% de cobertura
✅ Tempo: ~53 segundos
```

---

## 📡 Testando a API

### 1. Obter Token de Autenticação

```bash
curl -X POST http://localhost:8000/integrations/auth \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "login=eyesonasset&password=eyesonasset"
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 2. Salvar o Token

```bash
# Linux/Mac
export TOKEN="<seu-token-aqui>"

# Windows (CMD)
set TOKEN=<seu-token-aqui>

# Windows (PowerShell)
$TOKEN="<seu-token-aqui>"
```

### 3. Criar um Owner

```bash
curl -X POST http://localhost:8000/integrations/owner \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao.silva@empresa.com",
    "phone": "+55 11 98765-4321"
  }'
```

### 4. Listar Owners

```bash
curl http://localhost:8000/integrations/owners \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Criar um Asset

```bash
# Substitua <owner-id> pelo ID retornado no passo 3
curl -X POST http://localhost:8000/integrations/asset \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Notebook Dell Latitude",
    "category": "Eletrônicos",
    "owner": "<owner-id>"
  }'
```

### 6. Listar Assets

```bash
curl http://localhost:8000/integrations/assets \
  -H "Authorization: Bearer $TOKEN"
```

### 7. Criar Novo Usuário

```bash
curl -X POST http://localhost:8000/integrations/user \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "novousuario",
    "password": "senha123"
  }'
```

---

## 🌐 Acessar Documentação Interativa

### Swagger UI (Recomendado)

http://localhost:8000/docs

- Interface interativa
- Testar endpoints diretamente
- Ver schemas e exemplos
- Autenticação JWT integrada

### ReDoc

http://localhost:8000/redoc

- Documentação alternativa
- Mais legível para leitura
- Exportação para OpenAPI

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```ini
# Banco de dados
DATABASE_URL=sqlite:///./assets.db

# JWT (IMPORTANTE: Mude em produção!)
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Aplicação
APP_ENV=development
DEBUG=True
```

### Gerar SECRET_KEY Segura

```bash
# Linux/Mac
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Docker com Volume Persistente

O `docker-compose.yaml` já está configurado para persistir o banco de dados:

```yaml
volumes:
  - ./data:/app/data
```

O banco será salvo em `backend/data/assets.db`.

---

## 🐛 Troubleshooting

### Problema: "ModuleNotFoundError"

**Solução Docker:**
```bash
docker-compose build --no-cache
docker-compose up
```

**Solução Local:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Problema: "Port 8000 already in use"

**Solução:**
```bash
# Encontrar processo usando a porta
lsof -ti:8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Matar processo
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Ou mudar a porta no docker-compose.yaml
ports:
  - "8001:8000"  # Usar porta 8001 externa
```

### Problema: "Database is locked"

**Solução:**
```bash
# Parar todos os containers
docker-compose down

# Remover banco de dados
rm -f data/assets.db  # Linux/Mac
del data\assets.db  # Windows

# Recriar usuário padrão
docker-compose up -d
docker-compose exec backend python create_default_user.py
```

### Problema: "bcrypt compatibility error"

**Causa:** Versão incorreta do bcrypt

**Solução:**
```bash
pip uninstall bcrypt
pip install bcrypt==4.0.1
```

### Problema: "Testes falhando"

**Verificações:**
```bash
# 1. Verificar ambiente virtual ativado
which python  # Linux/Mac (deve mostrar caminho do venv)
where python  # Windows

# 2. Reinstalar dependências
pip install -r requirements.txt

# 3. Limpar cache
rm -rf __pycache__ .pytest_cache
find . -type d -name __pycache__ -exec rm -rf {} +  # Linux/Mac

# 4. Executar apenas 1 teste para debug
pytest tests/test_auth.py::test_login_success -v
```

---

## 📊 Verificações de Saúde

### Health Check Endpoint

```bash
curl http://localhost:8000/docs
```

Se retornar HTML, a aplicação está rodando.

### Verificar Logs Docker

```bash
docker-compose logs -f backend
```

### Verificar Banco de Dados

```bash
# Localmente
sqlite3 assets.db "SELECT * FROM users;"

# Docker
docker-compose exec backend sqlite3 data/assets.db "SELECT * FROM users;"
```

---

## 🔐 Segurança

### ⚠️ IMPORTANTE para Produção

1. **Mudar SECRET_KEY**
   ```bash
   openssl rand -hex 32
   ```

2. **Aumentar tempo de expiração do token**
   ```ini
   ACCESS_TOKEN_EXPIRE_MINUTES=60  # ou mais
   ```

3. **Usar HTTPS**
   - Configurar reverse proxy (nginx/traefik)
   - Certificado SSL/TLS

4. **Desabilitar hot-reload**
   ```yaml
   # docker-compose.yaml
   command: uvicorn app.main:app --host 0.0.0.0 --port 8000
   # Remover --reload
   ```

5. **Remover volume de código em produção**
   ```yaml
   # Comentar esta linha:
   # - ./app:/app/app
   ```

6. **Usar banco de dados robusto**
   - PostgreSQL
   - MySQL/MariaDB
   - Em vez de SQLite

---

## 🚀 Deploy em Produção

### Heroku

```bash
# Instalar Heroku CLI
heroku login

# Criar app
heroku create eyesonasset-api

# Configurar variáveis
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
heroku config:set DATABASE_URL=<postgres-url>

# Deploy
git push heroku main

# Criar usuário padrão
heroku run python create_default_user.py
```

### Railway

1. Conectar repositório GitHub
2. Configurar variáveis de ambiente
3. Deploy automático

### Render

1. Criar Web Service
2. Configurar build command: `pip install -r requirements.txt`
3. Configurar start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 📚 Recursos Adicionais

### Documentação

- [README.md](README.md) - Visão geral do projeto
- [NIVEL5_USERS.md](NIVEL5_USERS.md) - Detalhes do Nível 5

### Endpoints

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Suporte

- Criar issue no GitHub
- Consultar logs de erro
- Executar testes para debug

---

## ✅ Checklist de Verificação

Antes de considerar o setup completo, verifique:

- [ ] Docker instalado e rodando
- [ ] Build do container bem-sucedido
- [ ] Container iniciado (`docker-compose up`)
- [ ] Usuário padrão criado
- [ ] Swagger UI acessível (http://localhost:8000/docs)
- [ ] Login funcionando (eyesonasset/eyesonasset)
- [ ] Token JWT gerado
- [ ] CRUD de owners funcionando
- [ ] CRUD de assets funcionando
- [ ] CRUD de users funcionando
- [ ] 127 testes passando
- [ ] 94% de cobertura

---

## 🎯 Resumo dos Comandos

### Docker (Desenvolvimento)

```bash
# Setup inicial
docker-compose build
docker-compose up -d
docker-compose exec backend python create_default_user.py

# Uso diário
docker-compose up -d          # Iniciar
docker-compose logs -f        # Ver logs
docker-compose down           # Parar

# Testes
docker-compose run --rm backend pytest tests/ -v --cov=app

# Rebuild
docker-compose build --no-cache
```

### Local (Desenvolvimento)

```bash
# Setup inicial
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python create_default_user.py

# Uso diário
source venv/bin/activate      # Ativar venv
uvicorn app.main:app --reload # Iniciar
deactivate                    # Desativar venv

# Testes
pytest --cov=app --cov-report=html
```

---

**Documentação criada em:** 20/11/2024  
**Versão:** 1.0.0  
**Autor:** EyesOnAsset Team
