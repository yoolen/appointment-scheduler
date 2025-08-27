# Makefile for development tasks

.PHONY: pylint mypy pyfix

# Python linting - format code and sort imports
pylint:
	@echo "🔧 Formatting Python code..."
	docker-compose exec backend black app/
	docker-compose exec backend isort app/
	@echo "✅ Python linting completed!"

# Type checking with mypy
mypy:
	@echo "🔍 Type checking with mypy..."
	docker-compose exec backend mypy app/
	@echo "✅ Type checking completed!"

# Run all Python fixes - formatting and type checking
pyfix: pylint mypy
	@echo "✅ All Python fixes completed!"