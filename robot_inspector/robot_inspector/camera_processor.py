"""
Camera image processor with AWS Bedrock Claude integration.
Handles image analysis with vision capabilities and defect severity scoring.
"""

import json
import base64
import logging
from typing import Dict, List, Optional
from io import BytesIO
from PIL import Image
import boto3

logger = logging.getLogger(__name__)


class CameraProcessor:
    """Process camera images and analyze with Claude via AWS Bedrock."""

    def __init__(self, region_name: str = "us-east-1", model_id: str = "us.anthropic.claude-opus-4-6-v1"):
        """
        Initialize Bedrock client and model configuration.

        Args:
            region_name: AWS region for Bedrock
            model_id: Bedrock model ID for Claude
        """
        self.bedrock_client = boto3.client("bedrock-runtime", region_name=region_name)
        self.model_id = model_id
        self.analysis_history = []

    def _image_to_base64(self, image_bytes: bytes) -> str:
        """Convert image bytes to base64 string."""
        return base64.b64encode(image_bytes).decode("utf-8")

    def _prepare_image_for_claude(self, image_bytes: bytes) -> Dict:
        """
        Prepare image in Bedrock Claude-compatible format.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Image content dict for Bedrock API
        """
        base64_image = self._image_to_base64(image_bytes)
        return {
            "image": {
                "format": "png",
                "source": {
                    "bytes": image_bytes,
                },
            }
        }

    def process_image_with_claude(
        self,
        image_bytes: bytes,
        context: str = "Factory/warehouse inspection scene",
        include_severity: bool = True,
    ) -> Dict:
        """
        Send image to Claude via Bedrock and get analysis with severity scoring.

        Args:
            image_bytes: PNG/JPEG image data
            context: Scene context for analysis
            include_severity: Include defect severity scoring

        Returns:
            Analysis result dict with objects, issues, severity scores
        """
        try:
            image_content = self._prepare_image_for_claude(image_bytes)

            # Build analysis prompt
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

            # Call Bedrock - fix for correct API format
            content = [image_content, {"text": analysis_prompt}]

            message_response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
                system=[
                    {
                        "text": "You are an expert industrial quality inspector. Analyze images carefully and provide structured, actionable feedback."
                    }
                ],
            )

            # Parse response from Bedrock converse API
            response_text = message_response["output"]["message"]["content"][0]["text"]

            # Extract JSON from response
            try:
                # Try to parse as pure JSON
                analysis_result = json.loads(response_text)
            except json.JSONDecodeError:
                # If direct JSON fails, try to extract JSON from text
                import re
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

            # Store in history for comparison
            self.analysis_history.append(analysis_result)

            logger.info(f"Image analysis complete. Status: {analysis_result.get('overall_status', 'UNKNOWN')}")
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
        """
        Compare two inspection analyses to detect changes.

        Args:
            analysis1: First analysis result
            analysis2: Second analysis result (usually later)

        Returns:
            Comparison report with deltas
        """
        comparison = {
            "timestamp_order": "first -> second",
            "objects_changed": [],
            "new_issues": [],
            "resolved_issues": [],
            "severity_changes": [],
        }

        # Compare objects
        objs1 = {obj["name"]: obj["count"] for obj in analysis1.get("objects", [])}
        objs2 = {obj["name"]: obj["count"] for obj in analysis2.get("objects", [])}

        for obj_name in set(list(objs1.keys()) + list(objs2.keys())):
            count1 = objs1.get(obj_name, 0)
            count2 = objs2.get(obj_name, 0)
            if count1 != count2:
                comparison["objects_changed"].append({
                    "object": obj_name,
                    "before": count1,
                    "after": count2,
                    "delta": count2 - count1,
                })

        # Compare issues
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
