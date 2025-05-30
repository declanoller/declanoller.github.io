#!/bin/bash

HOOK_NAMES=("pre-commit")  # Add more hook names here if needed
HOOKS_DIR="utils/hooks"

for HOOK_NAME in "${HOOK_NAMES[@]}"; do
  SRC_PATH="$HOOKS_DIR/$HOOK_NAME"
  DEST_PATH=".git/hooks/$HOOK_NAME"

  if [ ! -f "$SRC_PATH" ]; then
    echo "❌ Hook $SRC_PATH not found."
    continue
  fi

  echo "🔗 Linking $DEST_PATH -> $SRC_PATH"
  ln -sf "../../$SRC_PATH" "$DEST_PATH"
  chmod +x "$SRC_PATH"
done

echo "✅ All hooks set up."
