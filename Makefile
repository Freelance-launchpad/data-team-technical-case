#!/usr/bin/make --file

SHELL := bash
.SHELLFLAGS := -euo pipefail -c

.ONESHELL:

UID := $(shell id -u)
GID := $(shell id -g)

DOCKER_REPOSITORY := jump/data-platform



.PHONY: default
default: all


.PHONY: all
all: clean build refresh


##@ Build
.PHONY: build
build: ## Construit l'image Docker qui embarque la CLI, le projet DBT, etc.
	mkdir -p "./data"
	docker build \
		--build-arg "UID=$(UID)" \
		--build-arg "GID=$(GID)" \
		--file "./docker/Dockerfile" \
		--tag "$(DOCKER_REPOSITORY)" \
			"."



##@ Run
.PHONY: refresh
refresh: extract load transform export ## Lance successivement l'extraction, le chargement, les transformations et l'export des données


.PHONY: extract
extract: ## Lance l'extraction des données de l'App et du CRM sous forme de fichiers CSV
	mkdir -p "./data"
	docker run \
		--rm \
		--user "$(UID):$(GID)" \
		--volume "$(PWD)/data:/var/local/lib/data-platform" \
		--volume "$(PWD)/dbt:/usr/local/lib/data-platform/dbt" \
		"$(DOCKER_REPOSITORY)" \
			extract


.PHONY: load
load: # Charge les fichiers CSV extraits dans la couche Sources du Lakehouse
	mkdir -p "./data"
	docker run \
		--rm \
		--user "$(UID):$(GID)" \
		--volume "$(PWD)/data:/var/local/lib/data-platform" \
		--volume "$(PWD)/dbt:/usr/local/lib/data-platform/dbt" \
		"$(DOCKER_REPOSITORY)" \
			load


.PHONY: transform
transform: ## Intègre les données de la couche Sources dans les couches Staging, Intermediate et Marts 
	mkdir -p "./data"
	docker run \
		--rm \
		--user "$(UID):$(GID)" \
		--volume "$(PWD)/data:/var/local/lib/data-platform" \
		--volume "$(PWD)/dbt:/usr/local/lib/data-platform/dbt" \
		"$(DOCKER_REPOSITORY)" \
			transform

.PHONY: export
export: ## Export les analyses au format CSV 
	mkdir -p "./data"
	docker run \
		--rm \
		--user "$(UID):$(GID)" \
		--volume "$(PWD)/data:/var/local/lib/data-platform" \
		--volume "$(PWD)/dbt:/usr/local/lib/data-platform/dbt" \
		"$(DOCKER_REPOSITORY)" \
			export


.PHONY: query
query: ## Lance un REPL pour requêter le lakehouse (via DuckDB)
	mkdir -p "./data"
	docker run \
		--rm \
		--tty \
		--interactive \
		--user "$(UID):$(GID)" \
		--volume "$(PWD)/data:/var/local/lib/data-platform" \
		--volume "$(PWD)/dbt:/usr/local/lib/data-platform/dbt" \
		--entrypoint "/usr/local/bin/duckdb" \
		"$(DOCKER_REPOSITORY)" \
			"/var/local/lib/data-platform/lakehouse/lakehouse.duckdb" \
				-cmd 'USE intermediate; SHOW TABLES;'


.PHONY: compile-model
compile-model:
	docker run \
		--rm \
		--user "$(UID):$(GID)" \
		--volume "$(PWD)/data:/var/local/lib/data-platform" \
		--volume "$(PWD)/dbt:/usr/local/lib/data-platform/dbt" \
		--workdir "/usr/local/lib/data-platform/dbt" \
		--entrypoint "/usr/local/lib/data-platform/venv/bin/dbt" \
		"$(DOCKER_REPOSITORY)" \
			compile \
				--select="$(MODEL)" \
				--profile-dir


##@ Divers
.PHONY: help
help: ## Affiche l'aide
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


.PHONY: debug
debug: ## Lance un shell pour debuger l'image Docker
	mkdir -p "./data"
	docker run \
		--interactive \
		--tty \
		--rm \
		--entrypoint "/bin/bash" \
		--volume "$(PWD)/data:/var/local/lib/data-platform" \
		--volume "$(PWD)/dbt:/usr/local/lib/data-platform/dbt" \
		"$(DOCKER_REPOSITORY)"


.PHONY: clean
clean: ## Supprime le dossier ./data (dans lequel sont générés les différents fichiers)
	rm -rf "./data"