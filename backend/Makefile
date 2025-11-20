.PHONY: help install test coverage run docker-build docker-up docker-down docker-logs docker-test clean

help: ## Mostrar este menu de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ==================== Setup Local ====================

install: ## Instalar dependências Python
	pip install --upgrade pip
	pip install -r requirements.txt

create-user: ## Criar usuário padrão no banco de dados
	python create_default_user.py

run: ## Iniciar servidor local (desenvolvimento)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ==================== Testes ====================

test: ## Executar todos os testes
	pytest tests/ -v

test-cov: ## Executar testes com cobertura
	pytest tests/ -v --cov=app --cov-report=term-missing

test-html: ## Executar testes e gerar relatório HTML de cobertura
	pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "Relatório disponível em: htmlcov/index.html"

coverage: test-html ## Alias para test-html

# ==================== Docker ====================

docker-build: ## Build da imagem Docker
	docker-compose build

docker-up: ## Iniciar containers em background
	docker-compose up -d

docker-down: ## Parar e remover containers
	docker-compose down

docker-logs: ## Ver logs dos containers
	docker-compose logs -f backend

docker-restart: ## Reiniciar containers
	docker-compose restart

docker-test: ## Executar testes no Docker
	docker-compose run --rm backend pytest tests/ -v --cov=app --cov-report=term-missing

docker-create-user: ## Criar usuário padrão no Docker
	docker-compose exec backend python create_default_user.py

docker-shell: ## Abrir shell no container
	docker-compose exec backend bash

docker-clean: ## Remover containers, volumes e imagens
	docker-compose down -v --rmi local

# ==================== Limpeza ====================

clean: ## Limpar arquivos temporários e cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov .coverage coverage.xml

clean-db: ## Remover banco de dados SQLite
	rm -f assets.db data/assets.db

# ==================== Desenvolvimento ====================

dev: install create-user run ## Setup completo e iniciar servidor

docker-dev: docker-build docker-up docker-create-user ## Setup completo com Docker

lint: ## Verificar código com flake8 (se instalado)
	@command -v flake8 >/dev/null 2>&1 && flake8 app/ tests/ || echo "flake8 não instalado"

format: ## Formatar código com black (se instalado)
	@command -v black >/dev/null 2>&1 && black app/ tests/ || echo "black não instalado"

# ==================== Informações ====================

status: ## Verificar status dos containers
	docker-compose ps

logs-tail: ## Ver últimas 100 linhas dos logs
	docker-compose logs --tail=100 backend

db-shell: ## Abrir shell do SQLite (local)
	sqlite3 assets.db

docker-db-shell: ## Abrir shell do SQLite (Docker)
	docker-compose exec backend sqlite3 data/assets.db
