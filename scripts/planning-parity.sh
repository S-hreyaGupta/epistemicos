#!/usr/bin/env bash
# scripts/planning-parity.sh — GOV-01's start check (D-13).
#
# Standalone, human-runnable comparison: does ROADMAP.md's requirement set for
# a given phase agree with REQUIREMENTS.md's traceability table for that same
# phase? Also validates that every requirement ID tagged in PROJECT.md exists
# in REQUIREMENTS.md's traceability table (D-15), so a typo there fails this
# check rather than producing a phantom close-sweep row that looks like
# coverage.
#
# Usage: bash scripts/planning-parity.sh <phase-number>
#   (or: make planning-parity PHASE=<phase-number>)
#
# Deliberately NOT part of `make gate`, and not reachable from it (D-13).
# Wiring this into the gate would make the gate fail on documentation drift,
# changing what a red gate means — in the one milestone whose entire purpose
# is that a red gate means exactly one thing. Run this by hand, whenever a
# phase's requirement set or a document's requirement-ID tags might have
# drifted from each other.
#
# No dependency on jq — verified absent from this host at planning time.
# Only POSIX/GNU tools verified present: bash, grep, sed, awk, sort, comm, tr.

set -u

ROADMAP=".planning/ROADMAP.md"
REQUIREMENTS=".planning/REQUIREMENTS.md"
PROJECT=".planning/PROJECT.md"

# --- Check 1: the argument ---------------------------------------------
# No default. A default would report agreement about a phase nobody asked
# about, which is exactly the shape of failure GOV-01 exists to remove.
PHASE="${1:-}"
if [ -z "$PHASE" ]; then
  echo "FAIL: missing required argument: phase number"
  echo "usage: bash scripts/planning-parity.sh <phase-number>"
  exit 1
fi

case "$PHASE" in
  ''|*[!0-9.]*)
    echo "FAIL: phase argument '$PHASE' is not a valid phase number (digits and an optional decimal point only)"
    exit 1
    ;;
esac

# --- Check 2: requirement-set parity (D-13) -----------------------------
#
# Set A: the requirement IDs on the **Requirements**: line inside ROADMAP's
# `### Phase <N>:` section (that heading up to, but not including, the next
# `### ` heading).
#
# Anchor the phase-number match so `2` cannot also match `21` or `2.1` — the
# digits must be followed by a colon, not by another digit or a decimal
# point.
FOUND=$(awk -v phase="$PHASE" '
  /^### Phase [0-9]+(\.[0-9]+)?:/ {
    line = $0
    sub(/^### Phase /, "", line)
    sub(/:.*/, "", line)
    if (line == phase) { print "yes"; exit }
  }
' "$ROADMAP")

ROADMAP_SECTION=$(awk -v phase="$PHASE" '
  BEGIN { insection = 0 }
  /^### / {
    if (insection) { exit }
    line = $0
    if (line ~ /^### Phase [0-9]+(\.[0-9]+)?:/) {
      num = line
      sub(/^### Phase /, "", num)
      sub(/:.*/, "", num)
      if (num == phase) { insection = 1 }
    }
    next
  }
  insection { print }
' "$ROADMAP")

REQ_LINE=$(printf '%s\n' "$ROADMAP_SECTION" | grep -m1 '^\*\*Requirements\*\*:')
# Requirement IDs are uppercase letters, a hyphen and exactly TWO digits, with
# word boundaries. No hard-coded prefix list, so a new prefix works the day it is
# introduced — but the two-digit width is load-bearing, not cosmetic: an
# unbounded [0-9]+ also matches SHA-256 in PROJECT.md, and the check then reports
# a hash algorithm as an unknown requirement. Two digits is the convention every
# other parser in this phase already uses and all 16 current IDs obey.
SET_A=$(printf '%s' "$REQ_LINE" | grep -woE '[A-Z]{2,}-[0-9]{2}' | sort -u)

# Set B: every row of REQUIREMENTS.md's `## Traceability` table whose Phase
# column names phase <N> — tolerating a trailing parenthetical (GOV-01's cell
# reads "Phase 2 (closure gate)") but not a longer phase number.
PHASE_RE=$(printf '%s' "$PHASE" | sed 's/\./\\./g')
SET_B=$(awk -v phase="$PHASE_RE" '
  BEGIN { insection = 0 }
  /^## Traceability/ { insection = 1; next }
  insection && /^## / { exit }
  insection && /^\|/ {
    line = $0
    n = split(line, f, "|")
    if (n < 3) next
    id = f[2]; gsub(/^[ \t]+|[ \t]+$/, "", id)
    ph = f[3]; gsub(/^[ \t]+|[ \t]+$/, "", ph)
    if (id !~ /^[A-Z]{2,}-[0-9][0-9]$/) next
    pat = "^Phase " phase "([^0-9.]|$)"
    if (ph ~ pat) print id
  }
' "$REQUIREMENTS" | sort -u)

ONLY_A=$(comm -23 <(printf '%s\n' "$SET_A") <(printf '%s\n' "$SET_B") | grep -v '^$')
ONLY_B=$(comm -13 <(printf '%s\n' "$SET_A") <(printf '%s\n' "$SET_B") | grep -v '^$')

# --- Check 3: PROJECT.md requirement-ID validity (D-15) -----------------
#
# Deliberately one-directional: this does not require every requirement to
# be tagged in PROJECT.md — most are not, and should not be. It only asserts
# that every ID PROJECT.md DOES tag is a real one, so a typo fails this check
# rather than producing a close-sweep row for a requirement that does not
# exist, which would read exactly like a checked one.
PROJECT_IDS=$(grep -woE '[A-Z]{2,}-[0-9]{2}' "$PROJECT" | sort -u)
ALL_IDS=$(awk '
  BEGIN { insection = 0 }
  /^## Traceability/ { insection = 1; next }
  insection && /^## / { exit }
  insection && /^\|/ {
    line = $0
    n = split(line, f, "|")
    if (n < 3) next
    id = f[2]; gsub(/^[ \t]+|[ \t]+$/, "", id)
    if (id ~ /^[A-Z]{2,}-[0-9][0-9]$/) print id
  }
' "$REQUIREMENTS" | sort -u)
INVALID_IDS=$(comm -23 <(printf '%s\n' "$PROJECT_IDS") <(printf '%s\n' "$ALL_IDS") | grep -v '^$')

# --- Report, sorted and deterministic, all failures rather than the first --
FAIL=0
OUTPUT=""

if [ "$FOUND" != "yes" ]; then
  FAIL=1
  OUTPUT="${OUTPUT}FAIL: no '### Phase ${PHASE}:' section found in ${ROADMAP} — an absent phase section is a failure, not an empty agreeing set
"
else
  if [ -n "$ONLY_A" ] || [ -n "$ONLY_B" ]; then
    FAIL=1
    OUTPUT="${OUTPUT}FAIL: phase ${PHASE} requirement sets disagree between ${ROADMAP} and ${REQUIREMENTS}
"
    if [ -n "$ONLY_A" ]; then
      OUTPUT="${OUTPUT}  In ROADMAP.md's Phase ${PHASE} but missing from REQUIREMENTS.md's traceability table:
$(printf '%s\n' "$ONLY_A" | sed 's/^/    /')
"
    fi
    if [ -n "$ONLY_B" ]; then
      OUTPUT="${OUTPUT}  In REQUIREMENTS.md's traceability table for Phase ${PHASE} but missing from ROADMAP.md:
$(printf '%s\n' "$ONLY_B" | sed 's/^/    /')
"
    fi
  fi
fi

if [ -n "$INVALID_IDS" ]; then
  FAIL=1
  OUTPUT="${OUTPUT}FAIL: PROJECT.md tags a requirement ID absent from REQUIREMENTS.md's traceability table:
$(printf '%s\n' "$INVALID_IDS" | sed 's/^/    /')
"
fi

if [ "$FAIL" -eq 0 ]; then
  UNION_COUNT=$(printf '%s\n%s\n' "$SET_A" "$SET_B" | grep -v '^$' | sort -u | wc -l | tr -d ' ')
  echo "OK: phase ${PHASE} — ${UNION_COUNT} requirement IDs compared between ROADMAP.md and REQUIREMENTS.md, and they agree. PROJECT.md's requirement-ID tags are all valid."
  exit 0
fi

printf '%s' "$OUTPUT"
exit 1
