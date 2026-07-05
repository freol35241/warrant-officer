#!/usr/bin/env bash
# Install warrant-officer into ~/.claude via symlinks.
# `git pull` in this clone is then the update mechanism.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$HOME/.claude/agents"
SKILLS_DIR="$HOME/.claude/skills"

mkdir -p "$AGENTS_DIR" "$SKILLS_DIR"

ln -sfn "$REPO_DIR/agents/warrant-officer.md" "$AGENTS_DIR/warrant-officer.md"
ln -sfn "$REPO_DIR/skills/claim-licensing" "$SKILLS_DIR/claim-licensing"

echo "Installed:"
echo "  $AGENTS_DIR/warrant-officer.md -> $REPO_DIR/agents/warrant-officer.md"
echo "  $SKILLS_DIR/claim-licensing -> $REPO_DIR/skills/claim-licensing"
echo
echo "Next: copy templates/CLAUDE.md into your project repo (or merge"
echo "section 5 and the pricing line into your existing CLAUDE.md)."
