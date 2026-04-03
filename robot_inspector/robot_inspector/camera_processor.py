"""
Camera image processor with generic LLM vision analysis.
Supports multiple backends: AWS Bedrock, OpenRouter, Ollama, Anthropic API.
"""

import json
import re
import logging
from typing import Dict, List, Optional

from .llm_provider import LLMProvider, create_provider

logger = logging.getLogger(__name__)


class CameraProcessor:
    """Process camera images and analyze with LLM vision models."""

    def __init__(self, provider: LLMProvider = None, **kwargs):
        """
        Initialize with an LLM provider.

        Args:
            provider: Pre-configured LLMProvider instance.
            **kwargs: If provider is None, passed to create_provider().
                      Supports: provider_name, region_name, model_id, api_key, base_url, model.

        Examples:
            # Bedrock (default, backward compatible)
            CameraProcessor(region_name="us-east-1", model_id="us.anthropic.claude-opus-4-6-v1")

            # OpenRouter
            CameraProcessor(provider_name="openrouter", api_key="sk-...")

            # Local Ollama
            CameraProcessor(provider_name="openai", base_url="http://localhost:11434/v1", model="llava")

            # Direct Anthropic
            CameraProcessor(provider_name="anthropic", api_key="sk-ant-...")

            # Pre-built provider
            CameraProcessor(provider=my_provider)
        """
        if provider:
            self.provider = provider
        else:
            self.provider = create_provider(**kwargs)
        self.analysis_history = []

    def process_image_with_claude(
        self,
        image_bytes: bytes,
        context: str = "Factory/warehouse inspection scene",
        include_severity: bool = True,
    ) -> Dict:
        """
        Send image to LLM for analysis with severity scoring.

        Args:
            image_bytes: PNG/JPEG image data
            context: Scene context for analysis
            include_severity: Include defect severity scoring

        Returns:
            Analysis result dict with objects, issues, severity scores
        """
        try:
            severity_instruction = ""
            if include_severity:
                severity_instruction = """
For each detected issue, provide a severity level:
- CRITICAL: Immediate safety/quality risk
- HIGH: Major defect affecting functionality
- MEDIUM: Moderate issue requiring attention
- LOW: Minor cosmetic issues

Return severity as a field in each issue object."""

            analysis_prompt = f"""You are an industrial warehouse quality inspector. Context: {context}

This image is from a robot camera inspecting warehouse shelves. The colored boxes/cubes are products/packages stored on wooden shelf racks.

Analyze this image and provide:
1. List of all visible products/items on the shelf with counts
2. Any detected defects: damaged products, fallen/tilted items, missing inventory, stains, structural shelf damage
3. Confidence score (0-1) for your analysis
4. Recommended maintenance actions

{severity_instruction}

Respond in JSON format:
{{
    "objects": [
        {{"name": "item_name", "count": 1, "description": "brief description"}}
    ],
    "detected_issues": [
        {{
            "issue": "description",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "location": "where in image",
            "recommendation": "what to do about it"
        }}
    ],
    "scene_description": "overall scene assessment",
    "confidence_score": 0.95,
    "overall_status": "PASS|REVIEW_REQUIRED|FAIL"
}}"""

            response_text = self.provider.send_vision_message(
                image_bytes=image_bytes,
                prompt=analysis_prompt,
            )

            # Extract JSON from response
            try:
                analysis_result = json.loads(response_text)
            except json.JSONDecodeError:
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    analysis_result = json.loads(json_match.group())
                else:
                    logger.warning("Could not extract JSON from response")
                    analysis_result = {
                        "objects": [],
                        "detected_issues": [],
                        "scene_description": response_text,
                        "confidence_score": 0.5,
                        "overall_status": "REVIEW_REQUIRED",
                    }

            self.analysis_history.append(analysis_result)
            logger.info(f"Analysis complete. Status: {analysis_result.get('overall_status', 'UNKNOWN')}")
            return analysis_result

        except Exception as e:
            logger.error(f"Error processing image with Claude: {e}")
            return {
                "error": str(e),
                "objects": [],
                "detected_issues": [],
                "scene_description": "Error during analysis",
                "confidence_score": 0.0,
                "overall_status": "ERROR",
            }

    def compare_analyses(self, analysis1: Dict, analysis2: Dict) -> Dict:
        """Compare two inspection analyses to detect changes."""
        comparison = {
            "timestamp_order": "first -> second",
            "objects_changed": [],
            "new_issues": [],
            "resolved_issues": [],
            "severity_changes": [],
        }

        objs1 = {obj["name"]: obj["count"] for obj in analysis1.get("objects", [])}
        objs2 = {obj["name"]: obj["count"] for obj in analysis2.get("objects", [])}

        for obj_name in set(list(objs1.keys()) + list(objs2.keys())):
            count1 = objs1.get(obj_name, 0)
            count2 = objs2.get(obj_name, 0)
            if count1 != count2:
                comparison["objects_changed"].append({
                    "object": obj_name, "before": count1, "after": count2, "delta": count2 - count1,
                })

        issues1_set = {issue["issue"] for issue in analysis1.get("detected_issues", [])}
        issues2_set = {issue["issue"] for issue in analysis2.get("detected_issues", [])}
        comparison["new_issues"] = list(issues2_set - issues1_set)
        comparison["resolved_issues"] = list(issues1_set - issues2_set)

        return comparison

    def get_analysis_history(self) -> List[Dict]:
        """Get all stored analyses from this session."""
        return self.analysis_history

    def reset_history(self):
        """Clear analysis history."""
        self.analysis_history = []
