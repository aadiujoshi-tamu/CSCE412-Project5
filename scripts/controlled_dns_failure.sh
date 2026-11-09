#!/usr/bin/env bash
set -euo pipefail

# A reversible demonstration for the course. It removes only this project's
# apex CloudFront aliases, after saving the exact records needed to restore them.
config_file="config/project.json"
domain=$(jq -r '.domain' "$config_file")
zone_id=$(jq -r '.zone_id' "$config_file")
backup_file="/private/tmp/csce412-route53-alias-backup.json"

prepare() {
  aws route53 list-resource-record-sets \
    --hosted-zone-id "$zone_id" \
    --query "ResourceRecordSets[?Name=='${domain}.'] | [?Type=='A' || Type=='AAAA']" \
    --output json > "$backup_file"
  test "$(jq 'length' "$backup_file")" -eq 2
  jq -n --slurpfile records "$backup_file" '{Changes: ($records[0] | map({Action:"DELETE",ResourceRecordSet:.}))}' > /private/tmp/csce412-delete-aliases.json
  jq -n --slurpfile records "$backup_file" '{Changes: ($records[0] | map({Action:"UPSERT",ResourceRecordSet:.}))}' > /private/tmp/csce412-restore-aliases.json
  echo "Prepared controlled DNS failure. Backup: $backup_file"
  echo "Review /private/tmp/csce412-delete-aliases.json before starting."
}

start() {
  [[ "${2:-}" == "--approve-failure" ]] || { echo "Use: $0 start --approve-failure"; exit 2; }
  test -f "$backup_file" || { echo "Run '$0 prepare' first."; exit 2; }
  aws route53 change-resource-record-sets --hosted-zone-id "$zone_id" --change-batch file:///private/tmp/csce412-delete-aliases.json
  echo "Failure introduced. Run scripts/verify.sh and preserve that evidence."
}

restore() {
  [[ "${2:-}" == "--approve-restore" ]] || { echo "Use: $0 restore --approve-restore"; exit 2; }
  test -f "$backup_file" || { echo "No backup exists. Refusing to restore unknown records."; exit 2; }
  aws route53 change-resource-record-sets --hosted-zone-id "$zone_id" --change-batch file:///private/tmp/csce412-restore-aliases.json
  echo "Records restored. Wait for Route 53 to apply the change, then run scripts/verify.sh."
}

case "${1:-}" in
  prepare) prepare ;;
  start) start "$@" ;;
  restore) restore "$@" ;;
  *) echo "Usage: $0 {prepare|start --approve-failure|restore --approve-restore}"; exit 2 ;;
esac
