#!/usr/bin/env bash
# rename-branches.sh
# Usage: run this from any machine with git installed and push/delete rights to the repository.
# It will create new branch names pointing at the same commits as the old codex/* branches,
# verify creation, and then delete the old codex/* remote branches.
# IMPORTANT: verify each verification step outputs the expected refs before the delete step runs.

set -euo pipefail

REMOTE="origin"

# mapping: old -> new
declare -A MAP=(
  ["codex/refactor-code-structure-and-logging"]="refactor/structure-logging"
  ["codex/refactor-scripts-for-user-configurable-options"]="refactor/scripts-configurable-options"
  ["codex/review-imports-and-update-dependencies"]="chore/update-deps-and-imports"
  ["codex/split-script-into-modules-and-add-cli"]="feat/modularize-add-cli"
  ["codex/update-readme.md-with-setup-and-troubleshooting-info"]="docs/readme-setup-troubleshooting"
)

echo "Fetching remote refs from $REMOTE..."
git fetch "$REMOTE" --prune

# 1) Create new remote branches from old remote refs
echo
echo "Creating new remote branches..."
for old in "${!MAP[@]}"; do
  new="${MAP[$old]}"
  echo "Creating $new from remote ref $REMOTE/$old..."
  git push "$REMOTE" "refs/remotes/$REMOTE/$old:refs/heads/$new"
done

# 2) Verify new branches exist
echo
echo "Verifying new branches exist on remote..."
missing=()
for old in "${!MAP[@]}"; do
  new="${MAP[$old]}"
  if git ls-remote --heads "$REMOTE" "$new" | grep -q "refs/heads/$new\$"; then
    echo "OK: $new exists on $REMOTE"
  else
    echo "MISSING: $new does NOT exist on $REMOTE"
    missing+=("$new")
  fi
done

if [ ${#missing[@]:-0} -ne 0 ]; then
  echo
  echo "Error: the following new branches are missing on $REMOTE:"
  for b in "${missing[@]}"; do echo " - $b"; done
  echo "Aborting before deleting old branches."
  exit 1
fi

# 3) Confirm before deletion
echo
echo "All new branches verified. About to delete the old codex/* remote branches."
read -p "Type DELETE to proceed with deleting old remote branches: " confirmation
if [ "$confirmation" != "DELETE" ]; then
  echo "Aborted by user. Old branches were not deleted."
  exit 0
fi

# 4) Delete old remote branches
echo
echo "Deleting old remote branches..."
for old in "${!MAP[@]}"; do
  echo "Deleting remote branch $old..."
  git push "$REMOTE" --delete "$old"
done

echo
echo "Done. New branch names on remote:"
for old in "${!MAP[@]}"; do
  echo " - ${MAP[$old]}"
done

echo
cat <<EOF
Next steps for collaborators (locally):
- If you have the old branch checked out locally:
  git fetch origin
  git branch -m codex/OLD-BRANCH-NAME NEW-BRANCH-NAME
  git branch -u origin/NEW-BRANCH-NAME NEW-BRANCH-NAME
  git remote prune origin

- To fetch and checkout a renamed branch:
  git fetch origin
  git checkout --track origin/NEW-BRANCH-NAME

Notes:
- This script requires push/delete permissions on the repository.
- Open PRs targeting old branch names may need retargeting on GitHub after the rename.
- If the repository has branch protection rules, you may need to update protections after the rename.
EOF
