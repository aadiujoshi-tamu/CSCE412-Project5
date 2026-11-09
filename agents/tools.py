import subprocess
from pathlib import Path
from typing import Any


class ToolRunner:
    """Allowlisted local and AWS checks. Tools never accept model-supplied shell text."""

    def __init__(self, config: dict[str, Any]):
        self.config = config

    @staticmethod
    def command(arguments: list[str]) -> dict[str, Any]:
        completed = subprocess.run(arguments, capture_output=True, text=True, check=False)
        return {
            "command": arguments,
            "exit_code": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }

    def check_site_files(self) -> dict[str, Any]:
        site = Path(self.config["site_dir"])
        required = ["index.html", "services.html", "approach.html", "team.html", "contact.html", "404.html", "styles.css", "script.js"]
        missing = [name for name in required if not (site / name).is_file()]
        return {"site_dir": str(site), "required": required, "missing": missing, "passed": not missing}

    def cloudfront_status(self) -> dict[str, Any]:
        return self.command([
            "aws", "cloudfront", "get-distribution", "--id", self.config["distribution_id"],
            "--query", "Distribution.[Status,DomainName,DistributionConfig.Enabled]", "--output", "json",
        ])

    def route53_aliases(self) -> dict[str, Any]:
        return self.command([
            "aws", "route53", "list-resource-record-sets", "--hosted-zone-id", self.config["zone_id"],
            "--query", f"ResourceRecordSets[?Name=='{self.config['domain']}.'] | [?Type=='A' || Type=='AAAA']",
            "--output", "json",
        ])

    def certificate_status(self) -> dict[str, Any]:
        distribution = self.command([
            "aws", "cloudfront", "get-distribution", "--id", self.config["distribution_id"],
            "--query", "Distribution.DistributionConfig.ViewerCertificate.ACMCertificateArn", "--output", "text",
        ])
        arn = distribution["stdout"]
        if distribution["exit_code"] != 0 or not arn or arn == "None":
            return {"distribution_lookup": distribution, "certificate": None}
        certificate = self.command([
            "aws", "acm", "describe-certificate", "--region", self.config["region"], "--certificate-arn", arn,
            "--query", "Certificate.[Status,DomainName,SubjectAlternativeNames]", "--output", "json",
        ])
        return {"distribution_lookup": distribution, "certificate": certificate}

    def s3_public_access(self) -> dict[str, Any]:
        return self.command([
            "aws", "s3api", "get-public-access-block", "--bucket", self.config["bucket"],
            "--query", "PublicAccessBlockConfiguration", "--output", "json",
        ])

    def s3_anonymous_probe(self) -> dict[str, Any]:
        url = f"https://{self.config['bucket']}.s3.{self.config['region']}.amazonaws.com/index.html"
        return self.http_head(url)

    @staticmethod
    def http_head(url: str) -> dict[str, Any]:
        completed = subprocess.run(
            ["curl", "-sS", "-I", "--max-time", "15", "-A", "csce412-agent-verifier/1.0", url],
            capture_output=True,
            text=True,
            check=False,
        )
        headers: dict[str, str] = {}
        status = None
        for line in completed.stdout.splitlines():
            if line.startswith("HTTP/"):
                fields = line.split()
                if len(fields) > 1 and fields[1].isdigit():
                    status = int(fields[1])
            elif ":" in line:
                key, value = line.split(":", 1)
                headers[key.lower()] = value.strip()
        error = completed.stderr.strip() or None
        return {"url": url, "status": status, "headers": headers, "error": error, "tool": "curl"}

    def verify_urls(self) -> dict[str, Any]:
        domain = self.config["domain"]
        paths = ["/", "/services.html", "/approach.html", "/team.html", "/contact.html", "/missing-resource"]
        return {path: self.http_head(f"https://{domain}{path}") for path in paths}

    def http_redirect(self) -> dict[str, Any]:
        return self.http_head(f"http://{self.config['domain']}/")

    def deployment(self, approve: bool) -> dict[str, Any]:
        if not approve:
            return {"performed": False, "reason": "Deployment requires --approve-deployment."}
        return self.command(["bash", "scripts/deploy.sh", "--apply"])
