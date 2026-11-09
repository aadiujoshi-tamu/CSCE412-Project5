import argparse
import json
import sys
from pathlib import Path
from typing import Any

from botocore.exceptions import ClientError

from agents.contracts import AgentMessage, timestamp
from agents.logging import RunLogger
from agents.model import BedrockModel
from agents.specialists import InfrastructureAgent, RequirementsAgent, SecurityAgent, VerificationAgent
from agents.tools import ToolRunner


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Project 5 multi-agent workflow.")
    parser.add_argument("--config", default="config/project.json")
    parser.add_argument("--approve-deployment", action="store_true", help="Allows the infrastructure agent to upload the static site and invalidate CloudFront.")
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    run_id = args.run_id or timestamp().replace(":", "-").replace("+00:00", "Z")
    logger = RunLogger(Path("logs") / f"agent-run-{run_id}.jsonl")
    config = load_config(Path(args.config))
    logger.event("run_started", run_id=run_id, approval={"deployment": args.approve_deployment}, config={key: value for key, value in config.items() if "secret" not in key.lower()})

    model = BedrockModel(config["bedrock_model_id"], config["region"])
    tools = ToolRunner(config)
    agents = {
        "requirements": RequirementsAgent("requirements", "You are the requirements agent. Decompose the supplied cloud website objective into no more than six concise, testable tasks. State assumptions and risks. Do not claim a task happened unless evidence says it did.", model, tools),
        "infrastructure": InfrastructureAgent("infrastructure", "You are the infrastructure agent. Interpret requirements and the real tool results in at most six bullets. Explain readiness and any blocker. Tool results are the evidence; never assume missing facts.", model, tools),
        "security": SecurityAgent("security", "You are the security agent. Assess private-origin controls from supplied tool evidence in at most six bullets. State precise gaps and the smallest safe corrective action. Do not expose credentials or infer outcomes that are absent.", model, tools),
        "verification": VerificationAgent("verification", "You are the verification agent. In at most eight concise bullets, evaluate only the supplied HTTP and AWS evidence. Report a requirement as passing when its supplied evidence supports it. If evidence is absent, call it incomplete evidence, not a failed deployment. Tool results are authoritative; never invent results.", model, tools),
    }
    messages: list[AgentMessage] = []

    def send(sender: str, recipient: str, kind: str, payload: dict[str, Any]) -> None:
        message = AgentMessage(len(messages) + 1, timestamp(), sender, recipient, kind, payload)
        messages.append(message)
        logger.event("agent_message", message=message.as_dict())

    try:
        requirements = agents["requirements"].run("Deploy and validate a secure five-page static website with a private S3 origin, CloudFront HTTPS, Route 53 DNS, and reproducible automation.")
        logger.event("agent_completed", agent="requirements", result=requirements)
        send("requirements", "infrastructure", "requirements_plan", requirements)
        infrastructure = agents["infrastructure"].run(requirements, args.approve_deployment)
        logger.event("agent_completed", agent="infrastructure", result=infrastructure)
        send("infrastructure", "security", "deployment_evidence", infrastructure)
        security = agents["security"].run(infrastructure)
        logger.event("agent_completed", agent="security", result=security)
        send("security", "verification", "security_evidence", security)
        verification = agents["verification"].run(security)
        logger.event("agent_completed", agent="verification", result=verification)
        summary = {"run_id": run_id, "verification": verification, "message_count": len(messages), "log": str(logger.path)}
        print(json.dumps(summary, indent=2))
        logger.event("run_completed", summary=summary)
        return 0
    except ClientError as error:
        logger.event("run_failed", error=error.response.get("Error", {}))
        print(f"AWS error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
