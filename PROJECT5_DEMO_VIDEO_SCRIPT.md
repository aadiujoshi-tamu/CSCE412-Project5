# Project 5 Demo Video Script (3–4 Minutes)

## Before recording

Open these in separate tabs or windows:

1. `https://csce412aadiujoshi.shop`
2. This project folder in VS Code.
3. A terminal in the project folder.
4. The GitHub repository: `https://github.com/aadiujoshi-tamu/CSCE412-Project5`

Start on the home page. Keep the terminal font large enough to read.

---

## 0:00–0:25 — Introduce the project

**Show:** The deployed home page in a browser.

**Say:**

> This is my CSCE 412 Project 5. I built a five-page static website and deployed it securely on AWS. The site uses my custom domain, csce412aadiujoshi.shop, with HTTPS through CloudFront. The project also includes a multi-agent AI system that plans, checks, and verifies the deployment.

**Do:** Click through **Services**, **Approach**, **Team**, and **Contact**. On Services, click one filter button. On Contact, show the form briefly.

---

## 0:25–0:50 — Explain the AWS architecture

**Show:** `PROJECT5_TECHNICAL_DOCUMENTATION.md`, Section 2, and the architecture diagram.

**Say:**

> Route 53 manages the DNS records for my custom domain. The domain points to CloudFront, which provides HTTPS, caching, and security headers. CloudFront gets the website files from a private S3 bucket. The bucket is not public because CloudFront uses Origin Access Control to make signed requests. ACM provides the TLS certificate for the domain.

**Show:** The browser address bar with `https://csce412aadiujoshi.shop`.

---

## 0:50–1:20 — Show the agent architecture

**Show:** `agents/specialists.py` and `agents/run.py` in VS Code. Then show the agent architecture diagram in the documentation.

**Say:**

> My system has four specialized agents. The Requirements Agent breaks down the task. The Infrastructure Agent checks the site files and CloudFront. The Security Agent checks S3 privacy. The Verification Agent checks the domain, HTTPS, redirect, certificate, DNS aliases, and CloudFront. They pass structured JSON messages to the next agent instead of manually copying text between chats.

> The agents use Amazon Bedrock with Amazon Nova Micro for reasoning. Their AWS and HTTP tool results are saved separately, so the model summary is not treated as proof by itself.

---

## 1:20–2:10 — Run the agents live

**Show:** Terminal.

**Type:**

```bash
python3 -m agents.run --run-id video-demo
```

**Say while it runs:**

> This is a real read-only execution. It invokes all four agents through Amazon Bedrock. The agents also call allowlisted tools to check the live site and AWS configuration. This command does not deploy or modify infrastructure.

**Show:** The final JSON summary after the command finishes.

**Say:**

> The final result includes real evidence: HTTPS pages return 200, the missing route returns 404, HTTP redirects to HTTPS, CloudFront is deployed, Route 53 aliases point to CloudFront, the ACM certificate is issued for my domain, and direct anonymous S3 access is denied.

**Type:**

```bash
tail -n 8 logs/agent-run-video-demo.jsonl
```

**Say:**

> This JSON Lines log records timestamps, agent decisions, structured handoffs, tool arguments, tool outputs, and the final result.

---

## 2:10–2:40 — Show direct verification and security evidence

**Type:**

```bash
bash scripts/verify.sh
```

**Say:**

> This independent verification script checks the pages, the HTTP-to-HTTPS redirect, CloudFront, S3 public-access blocks, and direct anonymous S3 access. The expected direct S3 result is 403 Forbidden, which proves the bucket is private.

**Show:** The `301` redirect and `403 Forbidden` lines in the terminal.

---

## 2:40–3:35 — Controlled DNS failure and recovery

> Only run this part when you are ready to create a brief outage for your own project domain. The commands modify only your Route 53 `A` and `AAAA` aliases. Record this section as one continuous sequence.

**Show:** `scripts/controlled_dns_failure.sh` in VS Code.

**Say:**

> The assignment requires a controlled, reversible failure. My script first saves the current Route 53 aliases, requires explicit approval before removing them, and requires a separate approval before restoring them.

**Type:**

```bash
bash scripts/controlled_dns_failure.sh prepare
```

**Say:**

> This prepares a backup and shows the exact records that will be changed. I review this before approval.

**Type:**

```bash
bash scripts/controlled_dns_failure.sh start --approve-failure
```

**Say:**

> I am now approving the controlled failure. The domain aliases are temporarily removed.

**Type:**

```bash
python3 -m agents.run --run-id video-dns-failure
```

**Say:**

> The agents now detect the failure from the live DNS and website evidence. They analyze the missing Route 53 aliases and recommend restoring the backed-up records.

**Type:**

```bash
bash scripts/controlled_dns_failure.sh restore --approve-restore
```

**Say:**

> I approve the recovery. The script restores the exact Route 53 records it saved before the test.

**Type:**

```bash
python3 -m agents.run --run-id video-dns-recovery
```

**Say:**

> The final run verifies that the aliases, HTTPS site, CloudFront delivery, and private S3 origin are working again.

> If Route 53 propagation takes longer than the video allows, show the returned Route 53 change ID and use the already-recorded post-recovery verification after propagation completes.

---

## 3:35–3:55 — Close with the repository and logs

**Show:** GitHub repository page and `project5-agent-logs.zip` in the project folder.

**Say:**

> My private GitHub repository contains the complete website source, agent code, AWS configuration files, deployment and verification scripts, and execution logs. The log archive includes real agent communication, tool execution, verifier failure recovery, and final deployment evidence.

> This project demonstrates a secure static AWS website and a multi-agent system that makes evidence-based deployment and verification decisions.

---

## Optional short command list

Use these commands if you need them during recording:

```bash
# Real agent validation
python3 -m agents.run --run-id video-demo

# Independent deployment verification
bash scripts/verify.sh

# Controlled cloud failure and recovery
bash scripts/controlled_dns_failure.sh prepare
bash scripts/controlled_dns_failure.sh start --approve-failure
python3 -m agents.run --run-id video-dns-failure
bash scripts/controlled_dns_failure.sh restore --approve-restore
python3 -m agents.run --run-id video-dns-recovery
```
