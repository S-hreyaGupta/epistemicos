.PHONY: help up down build build-api build-cli test fmt vet gate env-preflight migrate clean

help:
	@echo "EpistemicOS — common targets"
	@echo ""
	@echo "  make up          Start postgres via docker-compose"
	@echo "  make down        Stop docker-compose services"
	@echo "  make build       Build both binaries"
	@echo "  make build-api   Build only the API binary"
	@echo "  make build-cli   Build only the CLI binary"
	@echo "  make test        Go tests (lenient: an environment skip stays a skip)"
	@echo "  make gate        vet + gofmt + build + env-preflight + migrate + test;"
	@echo "                   REQUIRES a running database and will not start one"
	@echo "  make env-preflight  Fast check that the database and fixture prerequisites are met"
	@echo "  make migrate     Apply DB migrations"
	@echo "  make fmt         Format code"
	@echo "  make vet         Run go vet"
	@echo "  make clean       Remove build artifacts"

up:
	docker compose up -d postgres
	@echo "Waiting for postgres..."
	@until docker compose exec -T postgres pg_isready -U epistemicos -d epistemicos > /dev/null 2>&1; do sleep 1; done
	@echo "Postgres ready"

down:
	docker compose down

build: build-api build-cli

build-api:
	go build -o bin/epistemicos-api ./cmd/epistemicos-api

build-cli:
	go build -o bin/epistemicos-cli ./cmd/epistemicos-cli

# The banner is asserted from internal/platform/gate (built in 02-02) so it
# cannot be quietly dropped when someone tidies the Makefile — a banner
# nobody checks is a claim that cannot come back false (D-05).
test:
	@echo "make test is the lenient run: an environment skip stays a skip, so a suite that tested nothing still reports ok. make gate is the run that proves anything."
	go test ./... -count=1

# env-preflight reaches testenv.Pool's escalated path before migrate can run,
# so testenv — not store.RunMigrations — is the first to speak when the
# database is unreachable or EPISTEMIC_OS_DB_URL is unset (D-03). No -run
# filter: `go test -run` against a renamed test name exits 0 and reports ok,
# so having no test name in this Makefile means the vacuous-pass path does
# not exist, rather than being guarded against (D-04).
#
# This recipe must contribute no output of its own on the unreachable-
# database path — testenv's message must be the only text a developer sees
# (D-03). internal/platform/gate asserts that voicelessness; that assertion
# is built in 02-02, and this comment records why the constraint exists.
env-preflight:
	go test ./internal/platform/testenv/ -count=1

# The gate CI enforces. Run it before pushing. It demands a running
# PostgreSQL and never starts one — no `up` prerequisite, no `docker compose`
# invocation anywhere in this recipe or in the recipes it calls (D-01).
# env-preflight runs strictly before $(MAKE) migrate: that order is
# load-bearing, because without it store.RunMigrations becomes the first
# reporter for an unreachable database or an unset EPISTEMIC_OS_DB_URL, and
# its unaudited "new migrator: %w" text names neither in the terms GATE-01
# and GATE-02 require (D-03). The flag value below, make-gate, identifies the
# caller rather than merely signalling escalation is on; a target-scoped
# export distinguishes paths, not precedence — it overrides a stale value
# already exported in the caller's own environment (D-11).
gate: export EPISTEMIC_OS_TEST_REQUIRE_ENV = make-gate
gate: vet
	@unformatted=$$(gofmt -l .); \
	if [ -n "$$unformatted" ]; then \
		echo "unformatted files:"; echo "$$unformatted"; exit 1; \
	fi
	go build ./...
	$(MAKE) env-preflight
	$(MAKE) migrate
	$(MAKE) test

migrate:
	go run ./cmd/epistemicos-cli migrate up

fmt:
	go fmt ./...

vet:
	go vet ./...

clean:
	rm -rf bin/
