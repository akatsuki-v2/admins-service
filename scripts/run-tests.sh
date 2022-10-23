#!/usr/bin/env bash
set -eo pipefail

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

FULL_TEST_DB_NAME="${WRITE_DB_NAME}_test"
echo -e "\x1b[;93mRunning tests on '${FULL_TEST_DB_NAME}' database\x1b[m"

echo "Recreating database.."

echo "Dropping database ${FULL_TEST_DB_NAME}.."
execDBStatement "DROP DATABASE IF EXISTS ${FULL_TEST_DB_NAME}"

echo "Creating database ${FULL_TEST_DB_NAME}"
execDBStatement "CREATE DATABASE ${FULL_TEST_DB_NAME}"

# XXX:HACK: overwrite db names with test db names for runtime
export WRITE_DB_NAME=$FULL_TEST_DB_NAME
export READ_DB_NAME=$FULL_TEST_DB_NAME

echo "Running database migrations.."
/scripts/migrate-db.sh up

echo "Running database seeds.."
/scripts/seed-db.sh up

# make sure we're not running cache
find . -name "*.pyc" -delete
export PYTHONDONTWRITEBYTECODE=1

# use /srv/root as home
export PYTHONPATH=$PYTHONPATH:/srv/root
cd /srv/root

exec pytest tests/ \
    --cov-config=tests/coverage.ini \
    --cov=app \
    --cov-report=term \
    --cov-report=html:tests/htmlcov \
    --pdb -vv
