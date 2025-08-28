# Makefile for development tasks

# Automatically ensure backend is running for exec commands
BACKEND_RUN = @if ! docker compose ps backend | grep -q "running"; then \
	echo "🔄 Backend service not running, starting it..."; \
	docker compose up -d backend; \
	echo "⏳ Waiting for backend service to be ready..."; \
	sleep 10; \
fi; docker compose exec backend

.PHONY: pylint mypy pyfix bootstrap update_requirements

# Python linting - format code and sort imports
pylint:
	@echo "🔧 Formatting Python code..."
	$(BACKEND_RUN) black app/
	$(BACKEND_RUN) pylint app/
	$(BACKEND_RUN) isort app/
	@echo "✅ Python linting completed!"

# Type checking with mypy
mypy:
	@echo "🔍 Type checking with mypy..."
	$(BACKEND_RUN) mypy app/
	@echo "✅ Type checking completed!"

# Run all Python fixes - formatting and type checking
pyfix: pylint mypy
	@echo "✅ All Python fixes completed!"

# Bootstrap development environment
bootstrap:
	@echo "🚀 Bootstrapping development environment..."
	$(BACKEND_RUN) pip install pip-tools
	$(MAKE) update_requirements
	$(BACKEND_RUN) pip install -r requirements.txt
	@echo "✅ Development environment ready!"

# Compile requirements files using pip-tools
update_requirements:
	@echo "📦 Compiling requirements..."
	$(BACKEND_RUN) pip-compile \
		--cache-dir=~/.cache/pip \
		--resolver=backtracking \
		-Uvo requirements.txt requirements.in requirements-dev.in
	@echo "✅ Requirements compiled!"