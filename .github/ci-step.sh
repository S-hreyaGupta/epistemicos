#!/usr/bin/env bash
# Run one CI command and make its failure readable without a GitHub account.
#
# Why this exists. On 18 September the execution-layer job had been red for
# twelve consecutive runs and nobody could say why: this repository asks for a
# sign-in to show step logs, so the only thing visible was
#
#     Process completed with exit code 2
#
# which names neither the script nor the reason. Local runs all passed,
# including in pristine clones at the same commits, so the failure lived
# somewhere only the runner could see, and the runner would not say.
#
# The job summary and error annotations render on the run page without an
# account. So a failing command's output goes to both, and the exit code is
# still the command's own — this wrapper decides nothing and hides nothing.
#
# Invoked as `bash .github/ci-step.sh "<label>" <command...>`, deliberately
# with an explicit bash so a lost executable bit cannot turn a real failure
# into a confusing one.

set -uo pipefail

label="${1:?usage: ci-step.sh <label> <command...>}"
shift

out="$(mktemp)"
"$@" > "$out" 2>&1
code=$?

# Always echo the output, so the signed-in view is unchanged.
cat "$out"

if [ "$code" -ne 0 ]; then
    {
        echo "### FAILED — ${label}"
        echo
        echo "\`$*\` exited ${code}"
        echo
        echo '```text'
        tail -n 60 "$out"
        echo '```'
        echo
    } >> "${GITHUB_STEP_SUMMARY:-/dev/null}"

    # Annotations are visible without an account but are one line and capped,
    # so this carries the tail rather than the whole run.
    # %0A is how a workflow command carries a newline. An earlier version piped
    # through `tr '\n' '\x1b'`, which substituted a literal x and ran the lines
    # together — the annotation is the part that is readable without an
    # account, so getting it wrong would have defeated the point of the file.
    printf '::error title=%s exited %s::%s\n' \
        "$label" "$code" \
        "$(tail -n 12 "$out" | awk '{printf "%s%%0A", $0}' | cut -c1-800)"
fi

exit "$code"
