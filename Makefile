.PHONY: help install test test-unit test-integration test-docker test-docker-shell lint clean build generate \
	install-collections install-collection install-local uninstall-collections build-one clean-collections \
	release release-push

help:
	@echo "Cribl Ansible Collections - Development Commands"
	@echo ""
	@echo "Generation & Build:"
	@echo "  make generate              Generate modules from OpenAPI spec"
	@echo "  make build                 Build all collection tarballs"
	@echo "  make build-one COLLECTION=core  Build single collection"
	@echo "  make release VERSION=1.0.0 Create release locally"
	@echo "  make release-push VERSION=1.0.0  Create and push release to GitHub"
	@echo ""
	@echo "Installation:"
	@echo "  make install-collections   Install all collections to ~/.ansible/collections/"
	@echo "  make install-collection COLLECTION=core  Install single collection"
	@echo "  make install-local         Install to ./ansible_collections/ (local)"
	@echo "  make uninstall-collections Remove installed collections"
	@echo ""
	@echo "Testing:"
	@echo "  make test                  Run all tests"
	@echo "  make test-unit             Run unit tests only"
	@echo "  make test-integration      Run integration tests only"
	@echo "  make test-docker           Run Docker-based integration tests"
	@echo "  make test-docker-shell     Open shell in Docker test container"
	@echo ""
	@echo "Maintenance:"
	@echo "  make install               Install development dependencies"
	@echo "  make lint                  Run linters"
	@echo "  make clean                 Clean generated files and caches"
	@echo "  make clean-collections     Remove locally installed collections"

install:
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v -m unit

test-integration:
	pytest tests/integration/ -v -m integration

test-docker:
	@echo "Running Docker-based integration tests..."
	@cd tests/docker && bash run_tests.sh

test-docker-build:
	@echo "Building docker build container"
	docker build -t ansible-cribl:build .
	@echo "Building Docker test container..."
	@cd tests/docker && docker-compose build

test-docker-up:
	@echo "Starting Docker test container..."
	@cd tests/docker && docker-compose up -d
	@sleep 3
	@echo "Container is ready. Use 'make test-docker-shell' to access it."

test-docker-down:
	@echo "Stopping Docker test container..."
	@cd tests/docker && docker-compose down -v

test-docker-shell:
	@echo "Opening shell in Docker test container..."
	@cd tests/docker && docker-compose up -d
	@docker exec -it cribl-ansible-test /bin/bash

test-docker-playbook:
	@echo "Running playbook: $(PLAYBOOK)"
	@cd tests/docker && docker-compose up -d
	@docker exec cribl-ansible-test ansible-playbook -v /ansible/tests/docker/playbooks/$(PLAYBOOK)

test-coverage:
	pytest tests/ --cov=. --cov-report=html --cov-report=term

lint:
	flake8 scripts/ tests/
	ansible-lint build/ansible_collections/cribl/*/examples/*.yml || true

generate:
	python scripts/generate_modules.py

release:
	@echo "Usage: make release VERSION=1.0.0"
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION not specified"; \
		exit 1; \
	fi
	@./scripts/release.sh $(VERSION)

release-push:
	@echo "Usage: make release-push VERSION=1.0.0"
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION not specified"; \
		exit 1; \
	fi
	@./scripts/release.sh $(VERSION) --push

build:
	@echo "Building all collections..."
	@mkdir -p dist
	@for collection in core stream edge search lake; do \
		echo "Building cribl.$$collection..."; \
		if [ -d "build/ansible_collections/cribl/$$collection" ]; then \
			cd build/ansible_collections/cribl/$$collection && \
			ansible-galaxy collection build --output-path ../../../../dist --force && \
			cd ../../../..; \
		else \
			echo "  WARNING: Collection $$collection not found. Run 'make generate' first."; \
		fi \
	done
	@echo "All collections built successfully!"
	@echo "Tarballs are in: dist/"

build-one:
	@if [ -z "$(COLLECTION)" ]; then \
		echo "Error: COLLECTION not specified. Usage: make build-one COLLECTION=core"; \
		exit 1; \
	fi
	@echo "Building cribl.$(COLLECTION)..."
	@mkdir -p dist
	@cd build/ansible_collections/cribl/$(COLLECTION) && \
		ansible-galaxy collection build --output-path ../../../../dist --force
	@echo "Built: dist/cribl-$(COLLECTION)-*.tar.gz"

install-collections:
	@echo "Installing all collections from dist/ to user directory..."
	@if [ ! -d "dist" ] || [ -z "$$(ls -A dist/*.tar.gz 2>/dev/null)" ]; then \
		echo "Error: No collection tarballs found in dist/. Run 'make build' first."; \
		exit 1; \
	fi
	@for tarball in dist/cribl-*.tar.gz; do \
		echo "Installing $$tarball..."; \
		ansible-galaxy collection install $$tarball --force; \
	done
	@echo ""
	@echo "Collections installed successfully!"
	@echo "Location: ~/.ansible/collections/ansible_collections/cribl/"

install-collection:
	@if [ -z "$(COLLECTION)" ]; then \
		echo "Error: COLLECTION not specified. Usage: make install-collection COLLECTION=core"; \
		exit 1; \
	fi
	@echo "Installing cribl.$(COLLECTION)..."
	@ansible-galaxy collection install dist/cribl-$(COLLECTION)-*.tar.gz --force
	@echo "Installed: cribl.$(COLLECTION)"

install-local:
	@echo "Installing collections to local ansible_collections/ directory..."
	@mkdir -p ansible_collections/cribl
	@for collection in core stream edge search lake; do \
		if [ -d "build/ansible_collections/cribl/$$collection" ]; then \
			echo "Copying cribl.$$collection..."; \
			rm -rf ansible_collections/cribl/$$collection; \
			cp -r build/ansible_collections/cribl/$$collection ansible_collections/cribl/; \
		fi \
	done
	@echo ""
	@echo "Collections installed locally!"
	@echo "Location: ./ansible_collections/cribl/"
	@echo ""
	@echo "To use these collections, ensure your ansible.cfg has:"
	@echo "  [defaults]"
	@echo "  collections_paths = ./ansible_collections"

uninstall-collections:
	@echo "Uninstalling all Cribl collections..."
	@for collection in core stream edge search lake; do \
		echo "Uninstalling cribl.$$collection..."; \
		ansible-galaxy collection remove cribl.$$collection 2>/dev/null || true; \
	done
	@echo "Collections uninstalled!"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	rm -f .coverage 2>/dev/null || true
	rm -rf build/ 2>/dev/null || true
	rm -rf dist/ 2>/dev/null || true
	@echo "Cleanup complete!"

clean-collections:
	@echo "Removing locally installed collections..."
	rm -rf ansible_collections/ 2>/dev/null || true
	@echo "Local collections removed!"

format:
	black scripts/ tests/

check:
	@echo "Running syntax checks..."
	python -m py_compile scripts/generate_modules.py
	@echo "Syntax checks passed!"

