# CSCE 412 Project 5: Secure Cloud Website and Multi-Agent System

This repository contains a five-page static website and a Python multi-agent workflow that helps plan, deploy, inspect, secure, and verify its AWS deployment. The public site is served at [https://csce412aadiujoshi.shop](https://csce412aadiujoshi.shop).

## Architecture

```
Visitor -> Route 53 -> CloudFront (HTTPS + security headers) -> OAC -> private S3 bucket
                         ^
                         ACM certificate
```

The website files live in `site/`. Amazon S3 is private, and the CloudFront Origin Access Control is the only permitted reader. Route 53 hosts the public DNS zone and ACM provides the certificate attached to CloudFront.

## Multi-agent design

`agents/run.py` creates four specialized agents and passes structured `AgentMessage` records between them:

| Agent | Responsibility | Tools |
| --- | --- | --- |
| Requirements | Converts the project objective into testable tasks and risks. | Bedrock Converse API |
| Infrastructure | Inspects site files and CloudFront state; can deploy only with explicit approval. | Bedrock, AWS CLI, deployment script |
| Security | Checks S3 public-access controls and probes direct anonymous S3 access. | Bedrock, AWS CLI, HTTPS probe |
| Verification | Checks the domain pages, HTTPS response, HTTP redirect, and CloudFront status. | Bedrock, HTTPS probe, AWS CLI |

Each agent uses Amazon Bedrock Converse with `amazon.nova-micro-v1:0`. Outputs are model-generated, while tool results are recorded separately as the source of truth. The runner never accepts arbitrary model-generated commands. It calls only allowlisted tool methods.

## Setup

Requirements:

- Python 3.11 or later
- AWS CLI v2 configured with a least-privilege IAM identity
- AWS permissions for the read operations used by the runner; deployment requires S3 upload and CloudFront invalidation permissions
- Amazon Bedrock model access in `us-east-1` for `amazon.nova-micro-v1:0`
- `jq` and `curl`

Install the Python dependency:

```bash
python3 -m pip install -r requirements.txt
```

Copy `config/project.example.json` to `config/project.json` and update the resource identifiers for a different deployment. `config/project.json` includes no credentials or tokens.

## Running the agents

Read-only agent run:

```bash
python3 -m agents.run --run-id representative-readonly-run
```

The runner writes timestamped JSON Lines evidence in `logs/`. It contains model output, messages passed among agents, executed tool arguments, tool outputs, and final verification evidence.

Deploy through the approved infrastructure agent path:

```bash
python3 -m agents.run --approve-deployment --run-id approved-deployment-run
```

The `--approve-deployment` flag is the human approval gate. It uploads the `site/` directory to the configured bucket and invalidates CloudFront. The standalone command is equivalent:

```bash
bash scripts/deploy.sh --apply
```

## Reproducing a representative workflow

1. Run the read-only workflow above. It invokes all four agents and records programmatic handoffs.
2. Review the generated JSONL log for `agent_message`, `agent_completed`, and `run_completed` records.
3. Run `bash scripts/verify.sh` to independently inspect the live domain, redirect, private bucket access, and CloudFront configuration.
4. After reviewing the changes, run the approval-gated deployment workflow.
5. Re-run the read-only workflow to produce fresh post-deployment evidence.

## Controlled failure and recovery

The course requires a real, reversible failure with human approval before correction. `scripts/controlled_dns_failure.sh` creates a temporary backup in `/private/tmp` containing only this project's Route 53 `A` and `AAAA` aliases. It has separate explicit approval flags to remove and restore the aliases:

```bash
bash scripts/controlled_dns_failure.sh prepare
bash scripts/controlled_dns_failure.sh start --approve-failure
# run the verification agent and preserve the real failed evidence
bash scripts/controlled_dns_failure.sh restore --approve-restore
# run the verification agent again and preserve the recovery evidence
```

The outage affects only this project's domain aliases. Review the generated change batch before each approval. Never perform this test against another student's resources and never expose AWS credentials.

## Repository submission checklist

- Keep this repository private and add the instructor and TAs from Canvas as collaborators.
- Do not commit `logs/`, credentials, tokens, `.env`, or AWS access keys.
- Run a real agent workflow after the final deployment and place only the resulting redacted evidence ZIP in the Canvas upload.
- Submit this private repository URL in Canvas.
