#!/bin/sh
# Run from the repository root. Keep backup files outside the public web root.
set -eu
backup_dir=${1:?Usage: sh deploy/backup.sh /absolute/private/backup-directory}
mkdir -p "$backup_dir"
chmod 700 "$backup_dir"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup_file="$backup_dir/ieltsqa-$stamp.dump"
umask 077
if docker compose exec -T db pg_dump -U ieltsqa -Fc ieltsqa > "$backup_file.tmp"; then
  mv "$backup_file.tmp" "$backup_file"
  printf 'Backup saved: %s\n' "$backup_file"
else
  rm -f "$backup_file.tmp"
  exit 1
fi
