# Makefile for development tasks

.PHONY: pylint mypy pyfix bootstrap update_requirements

# Python linting - format code and sort imports
pylint:
	@echo "🔧 Formatting Python code..."
	docker compose exec backend black app/
	docker compose exec backend pylint app/
	docker compose exec backend isort app/
	@echo "✅ Python linting completed!"

# Type checking with mypy
mypy:
	@echo "🔍 Type checking with mypy..."
	docker compose exec backend mypy app/
	@echo "✅ Type checking completed!"

# Run all Python fixes - formatting and type checking
pyfix: pylint mypy
	@echo "✅ All Python fixes completed!"

# Bootstrap development environment
bootstrap:
	@echo "🚀 Bootstrapping development environment..."
	docker compose exec backend pip install pip-tools
	$(MAKE) update_requirements
	docker compose exec backend pip install -r requirements.txt
	@echo "✅ Development environment ready!"

# Compile requirements files using pip-tools
update_requirements:
	@echo "📦 Compiling requirements..."
	docker compose exec backend pip-compile \
		--cache-dir=~/.cache/pip \
		--resolver=backtracking \
		-Uvo requirements.txt requirements.in requirements-dev.in
	@echo "✅ Requirements compiled!"