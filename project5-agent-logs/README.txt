Project 5 Agent Execution Evidence
==================================

This folder contains unmodified JSON Lines records from real executions of the
Python multi-agent system. Each event has a UTC timestamp and includes the
invoked agent, model output, structured inter-agent message, tool arguments,
tool result, and run completion record. No credentials or API keys are present.

01-initial-verification-failure.jsonl
  The initial real run. The agents found that Python urllib could not use this
  machine's certificate authority bundle, so HTTPS probes falsely failed.

02-verifier-recovery.jsonl
  The recovery run after the verifier changed to the system curl trust store.
  It records successful HTTPS pages, the HTTP-to-HTTPS 301, CloudFront, and S3.

03-final-agent-validation.jsonl
  The final run adds Route 53 A/AAAA aliases and the attached ACM certificate
  with ISSUED status for csce412aadiujoshi.shop.

04-clean-final-validation.jsonl
  The final corrected run passes only current tool evidence to the verification
  agent. It records private S3 access, issued ACM certificate, Route 53 aliases,
  CloudFront delivery, HTTPS page checks, and the HTTP redirect.

Controlled cloud failure procedure
----------------------------------

scripts/controlled_dns_failure.sh provides the separate required cloud failure.
It saves this project's A/AAAA aliases, requires approval before removal and
restoration, and affects only the project domain. Use it later to capture the
real DNS failure and recovery logs required by the assignment.
