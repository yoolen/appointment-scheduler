# Makefile for development tasks

# Automatically ensure backend is running for exec commands
BACKEND_RUN = @docker compose up -d backend > /dev/null 2>&1; \
	echo "⏳ Ensuring backend is ready..."; \
	sleep 5; \
	docker compose exec --user 1000:1000 backend

.PHONY: black bootstrap isort mypy pyfix pylint update_requirements

# Python code formatting with black
black:
	@echo "🔧 Formatting Python code with black..."
	$(BACKEND_RUN) black app/
	@echo "✅ Code formatted!"

# Bootstrap development environment
bootstrap:
	@echo "🚀 Bootstrapping development environment..."
	$(BACKEND_RUN) pip install pip-tools
	$(MAKE) update_requirements
	$(BACKEND_RUN) pip install -r requirements.txt
	@echo "✅ Development environment ready!"

# Sort imports with isort
isort:
	@echo "🔧 Sorting imports with isort..."
	$(BACKEND_RUN) isort app/
	@echo "✅ Imports sorted!"

# Type checking with mypy
mypy:
	@echo "🔍 Type checking with mypy..."
	$(BACKEND_RUN) mypy app/
	@echo "✅ Type checking completed!"

# Run all Python fixes - formatting and type checking
pyfix: pylint mypy
	@echo "✅ All Python fixes completed!"

# Python linting - format code and sort imports
pylint:
	@echo "🔧 Formatting Python code..."
	$(MAKE) black
	$(BACKEND_RUN) pylint app/
	$(MAKE) isort
	@echo "✅ Python linting completed!"

python:
	@echo "🐍 Running Python shell..."
	$(BACKEND_RUN) python

# Compile requirements files using pip-tools
update_requirements:
	@echo "📦 Compiling requirements..."
	$(BACKEND_RUN) pip-compile \
		--cache-dir=~/.cache/pip \
		--resolver=backtracking \
		-Uvo requirements.txt requirements.in requirements-dev.in
	@echo "✅ Requirements compiled!"