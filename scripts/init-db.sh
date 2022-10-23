#!/usr/bin/env bash
set -euo pipefail

execDBStatement() {
  if [[ "$DB_USE_SSL" == "true" ]]; then
    EXTRA_PARAMS="--ssl"
  else
    EXTRA_PARAMS=""
  fi

  mysql \
  --host=$WRITE_DB_HOST \
  --port=$WRITE_DB_PORT \
  --user=$WRITE_DB_USER \
  --password=$WRITE_DB_PASS \
  $EXTRA_PARAMS \
  --execute="$1"

  # postgres version
  # echo "$1" | PGPASSWORD=$WRITE_DB_PASS psql \
  # --host=$WRITE_DB_HOST \
  # --port=$WRITE_DB_PORT \
  # --username=$WRITE_DB_USER \
  # --dbname=postgres

}

FULL_DB_NAME="${WRITE_DB_NAME}"

if [[ "$APP_COMPONENT" == "tests" ]]; then
  FULL_DB_NAME="${WRITE_DB_NAME}_test"
fi

execDBStatement "CREATE DATABASE IF NOT EXISTS ${FULL_DB_NAME}"
