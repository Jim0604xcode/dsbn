#!/bin/bash
set -e
mkdir -p /app/path/to/remote/google


if [ -z "$GOOGLE_SERVICE_ACCOUNT_FILE_PATH" ]; then
  export GOOGLE_SERVICE_ACCOUNT_FILE_PATH="/app/path/to/remote/google/service-account.json"
fi


if [ -n "$GOOGLE_SERVICE_ACCOUNT_JSON" ]; then
  echo "$GOOGLE_SERVICE_ACCOUNT_JSON" > "$GOOGLE_SERVICE_ACCOUNT_FILE_PATH"
  echo "Created Google service account file: $GOOGLE_SERVICE_ACCOUNT_FILE_PATH"
fi

# 执行CMD
exec "$@" 