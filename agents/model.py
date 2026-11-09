import os

import boto3
from botocore.config import Config


class BedrockModel:
    """Small adapter around Bedrock Converse for agent reasoning."""

    def __init__(self, model_id: str, region: str):
        self.model_id = model_id
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=Config(retries={"total_max_attempts": 5, "mode": "adaptive"}, connect_timeout=10, read_timeout=60),
        )

    def decide(self, system: str, prompt: str) -> dict[str, object]:
        response = self.client.converse(
            modelId=self.model_id,
            system=[{"text": system}],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 350, "temperature": 0.2},
            requestMetadata={"project": "csce412-project5", "component": "multi-agent-runner"},
        )
        text = "".join(block.get("text", "") for block in response["output"]["message"]["content"])
        return {
            "analysis": text,
            "stop_reason": response["stopReason"],
            "usage": response.get("usage", {}),
        }
