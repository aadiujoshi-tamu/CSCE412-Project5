#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" != "--apply" ]]; then
  echo "Refusing to deploy without --apply. This is an approval gate."
  exit 2
fi

config_file="config/project.json"
domain=$(jq -r '.domain' "$config_file")
bucket=$(jq -r '.bucket' "$config_file")
distribution_id=$(jq -r '.distribution_id' "$config_file")
site_dir=$(jq -r '.site_dir' "$config_file")

test -f "$site_dir/index.html"
for page in services.html approach.html team.html contact.html 404.html; do
  test -f "$site_dir/$page"
done

aws s3 sync "$site_dir/" "s3://$bucket/" \
  --delete \
  --exclude "*.html" \
  --cache-control "public,max-age=31536000,immutable"

for page in index.html services.html approach.html team.html contact.html 404.html; do
  aws s3 cp "$site_dir/$page" "s3://$bucket/$page" \
    --cache-control "no-cache,no-store,must-revalidate" \
    --content-type "text/html"
done

aws cloudfront create-invalidation --distribution-id "$distribution_id" --paths "/*" --output json
echo "Deployment requested for https://$domain"
