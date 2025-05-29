#!/bin/bash

# Exit immediately on errors
set -e

# Check for unstaged changes (files not added to staging)
if [[ -n $(git ls-files --others --exclude-standard) ]]; then
  echo "❌ Warning: You have unstaged (untracked) files. Commit aborted."
  git ls-files --others --exclude-standard
  exit 1
fi

# Create a timestamped commit message
DATE_STR=$(date +"%Y-%m-%d %H:%M:%S")

# Word list location
WORDLIST="/usr/share/dict/words"
if [[ ! -f $WORDLIST ]]; then
  echo "❌ Word list not found at $WORDLIST"
  exit 1
fi

# Filter word list to exclude words with apostrophes
CLEAN_WORDS=$(grep -v "'" "$WORDLIST")

# Pick two random words (lowercase)
WORD1=$(echo "$CLEAN_WORDS" | shuf -n 1 | tr '[:upper:]' '[:lower:]')
WORD2=$(echo "$CLEAN_WORDS" | shuf -n 1 | tr '[:upper:]' '[:lower:]')

# Final commit message
COMMIT_MSG="auto commit - $DATE_STR - $WORD1-$WORD2"

# Commit all staged and modified files
git add -A
git commit -am "$COMMIT_MSG"

# Push to current branch
git push

# Print the commit message with newlines
echo -e "\n✅ Commit message:\n$COMMIT_MSG\n"