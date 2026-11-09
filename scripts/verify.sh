#!/usr/bin/env bash
set -euo pipefail

config_file="config/project.json"
domain=$(jq -r '.domain' "$config_file")
bucket=$(jq -r '.bucket' "$config_file")
region=$(jq -r '.region' "$config_file")
distribution_id=$(jq -r '.distribution_id' "$config_file")

for page in / /services.html /approach.html /team.html /contact.html /missing-resource; do
  printf '\nHTTPS %s\n' "$page"
  curl -sS -I "https://$domain$page" | sed -n '1,12p'
done

printf '\nHTTP redirect\n'
curl -sS -I "http://$domain/" | sed -n '1,12p'

printf '\nS3 public-access block\n'
aws s3api get-public-access-block --bucket "$bucket" --output json

printf '\nDirect anonymous S3 probe (expect 403)\n'
curl -sS -I "https://$bucket.s3.$region.amazonaws.com/index.html" | sed -n '1,12p'

printf '\nCloudFront distribution\n'
aws cloudfront get-distribution --id "$distribution_id" --query 'Distribution.[Status,DomainName,DistributionConfig.Aliases.Items]' --output json
