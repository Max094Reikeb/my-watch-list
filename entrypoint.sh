#!/usr/bin/env sh
set -e

echo "Waiting for Postgres..."
python - <<'PY'
import os, time, socket
host=os.getenv("POSTGRES_HOST","db-postgress")
port=int(os.getenv("POSTGRES_PORT","5432"))
for _ in range(60):
    try:
        s=socket.create_connection((host,port), timeout=2)
        s.close()
        print("Postgres is reachable")
        break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("Postgres not reachable")
PY

echo "Running migrations..."
python manage.py migrate --noinput

exec "$@"