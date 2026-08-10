.PHONY: help up down build build-api build-cli test fmt vet gate migrate clean

help:
	@echo "EpistemicOS — common targets"
	@echo ""
	@echo "  make up          Start postgres via docker-compose"
	@echo "  make down        Stop docker-compose services"
	@echo "  make build       Build both binaries"
	@echo "  make build-api   Build only the API binary"
	@echo "  make build-cli   Build only the CLI binary"
	@echo "  make test        Go tests"
	@echo "  make gate        Full static gate: vet + gofmt + build + test"
	@echo "  make migrate     Apply DB migrations"
	@echo "  make fmt         Format code"
	@echo "  make vet         Run go vet"
	@echo "  make clean       Remove build artifacts"

up:
	docker compose up -d postgres
	@echo "Waiting for postgres..."
	@until docker compose exec -T postgres pg_isready -U paperly -d paperly > /dev/null 2>&1; do sleep 1; done
	@echo "Postgres ready"

down:
	docker compose down

build: build-api build-cli

build-api:
	go build -o bin/epistemicos-api ./cmd/epistemicos-api

build-cli:
	go build -o bin/epistemicos-cli ./cmd/epistemicos-cli

test:
	go test ./... -count=1

# The gate CI enforces. Run it before pushing.
gate: vet
	@unformatted=$$(gofmt -l .); \
	if [ -n "$$unformatted" ]; then \
		echo "unformatted files:"; echo "$$unformatted"; exit 1; \
	fi
	go build ./...
	go test ./... -count=1

migrate:
	go run ./cmd/epistemicos-cli migrate up

fmt:
	go fmt ./...

vet:
	go vet ./...

clean:
	rm -rf bin/
