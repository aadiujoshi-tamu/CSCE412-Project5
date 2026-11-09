import json
from dataclasses import dataclass
from typing import Any

from .model import BedrockModel
from .tools import ToolRunner


@dataclass
class Specialist:
    name: str
    system_prompt: str
    model: BedrockModel
    tools: ToolRunner

    def reason(self, context: dict[str, Any]) -> dict[str, Any]:
        decision = self.model.decide(self.system_prompt, json.dumps(context, indent=2, sort_keys=True))
        return {"agent": self.name, "decision": decision, "context_keys": sorted(context)}


class RequirementsAgent(Specialist):
    def run(self, objective: str) -> dict[str, Any]:
        return self.reason({"objective": objective, "constraints": ["five static pages", "four specialized agents", "S3, CloudFront, Route 53, ACM only", "human approval for impactful changes"]})


class InfrastructureAgent(Specialist):
    def run(self, requirements: dict[str, Any], approve_deployment: bool) -> dict[str, Any]:
        tools = {"site_files": self.tools.check_site_files(), "cloudfront": self.tools.cloudfront_status(), "deployment": self.tools.deployment(approve_deployment)}
        result = self.reason({"requirements": requirements, "tool_results": tools})
        result["tool_results"] = tools
        return result


class SecurityAgent(Specialist):
    def run(self, infrastructure: dict[str, Any]) -> dict[str, Any]:
        tools = {"public_access_block": self.tools.s3_public_access(), "anonymous_s3_probe": self.tools.s3_anonymous_probe()}
        result = self.reason({"infrastructure": infrastructure, "tool_results": tools, "required_outcome": "S3 must remain private and CloudFront must be the public delivery layer."})
        result["tool_results"] = tools
        return result


class VerificationAgent(Specialist):
    def run(self, security: dict[str, Any]) -> dict[str, Any]:
        tools = {
            "https_pages": self.tools.verify_urls(),
            "http_redirect": self.tools.http_redirect(),
            "cloudfront": self.tools.cloudfront_status(),
            "route53_aliases": self.tools.route53_aliases(),
            "certificate": self.tools.certificate_status(),
        }
        result = self.reason({"security_evidence": security["tool_results"], "tool_results": tools, "required_outcome": "Report evidence, failures, and a safe next action."})
        result["tool_results"] = tools
        return result
