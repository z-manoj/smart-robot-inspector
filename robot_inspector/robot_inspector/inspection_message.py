"""
Message conversion helpers for ROS2 topics.
Convert between Python dicts and ROS2 messages.
"""

import json
from typing import Dict, Any
from datetime import datetime


class AnalysisMessageConverter:
    """
    Convert analysis results to/from ROS2 message format.
    Uses JSON serialization for std_msgs/String compatibility.
    """

    @staticmethod
    def analysis_to_message(analysis_dict: Dict[str, Any], inspection_id: str) -> str:
        """
        Convert analysis result to ROS2 message format (JSON string).

        Args:
            analysis_dict: Analysis result from CameraProcessor
            inspection_id: Unique inspection identifier

        Returns:
            JSON string suitable for std_msgs/String
        """
        message = {
            'timestamp': datetime.now().isoformat(),
            'inspection_id': inspection_id,
            'analysis': analysis_dict
        }
        return json.dumps(message)

    @staticmethod
    def message_to_analysis(message_str: str) -> Dict[str, Any]:
        """
        Convert ROS2 message (JSON string) back to analysis dict.

        Args:
            message_str: JSON string from std_msgs/String

        Returns:
            Dict with analysis data
        """
        return json.loads(message_str)

    @staticmethod
    def create_compact_message(
        analysis_dict: Dict[str, Any],
        waypoint_id: int,
        inspection_id: str
    ) -> str:
        """
        Create compact message with essential information only.
        Useful for bandwidth-limited networks.

        Args:
            analysis_dict: Full analysis result
            waypoint_id: Waypoint identifier
            inspection_id: Inspection identifier

        Returns:
            Compact JSON message
        """
        compact = {
            'timestamp': datetime.now().isoformat(),
            'inspection_id': inspection_id,
            'waypoint_id': waypoint_id,
            'status': analysis_dict.get('overall_status'),
            'issues': len(analysis_dict.get('detected_issues', [])),
            'confidence': analysis_dict.get('confidence_score'),
            'critical_count': sum(
                1 for issue in analysis_dict.get('detected_issues', [])
                if issue.get('severity') == 'CRITICAL'
            ),
            'high_count': sum(
                1 for issue in analysis_dict.get('detected_issues', [])
                if issue.get('severity') == 'HIGH'
            )
        }
        return json.dumps(compact)

    @staticmethod
    def severity_to_diagnostic_level(severity: str) -> int:
        """
        Convert severity level to ROS2 DiagnosticLevel.

        Args:
            severity: Severity string (CRITICAL, HIGH, MEDIUM, LOW)

        Returns:
            DiagnosticLevel integer (0=OK, 1=WARN, 2=ERROR)
        """
        severity_map = {
            'CRITICAL': 2,  # Error
            'HIGH': 2,      # Error
            'MEDIUM': 1,    # Warning
            'LOW': 1,       # Warning
        }
        return severity_map.get(severity, 0)


class InspectionSummary:
    """
    Summary of inspection results for easy consumption.
    """

    def __init__(self):
        """Initialize empty summary."""
        self.total_issues = 0
        self.critical_issues = 0
        self.high_issues = 0
        self.medium_issues = 0
        self.low_issues = 0
        self.total_confidence = 0.0
        self.analysis_count = 0
        self.start_time = datetime.now()

    def add_analysis(self, analysis: Dict[str, Any]):
        """
        Add an analysis to the summary.

        Args:
            analysis: Analysis result dict
        """
        self.analysis_count += 1

        # Count issues by severity
        for issue in analysis.get('detected_issues', []):
            severity = issue.get('severity', 'LOW').upper()
            self.total_issues += 1

            if severity == 'CRITICAL':
                self.critical_issues += 1
            elif severity == 'HIGH':
                self.high_issues += 1
            elif severity == 'MEDIUM':
                self.medium_issues += 1
            elif severity == 'LOW':
                self.low_issues += 1

        # Track confidence
        confidence = analysis.get('confidence_score', 0.0)
        self.total_confidence += confidence

    def get_summary(self) -> Dict[str, Any]:
        """
        Get current summary as dict.

        Returns:
            Summary dictionary
        """
        avg_confidence = (
            self.total_confidence / self.analysis_count
            if self.analysis_count > 0
            else 0.0
        )

        elapsed = (datetime.now() - self.start_time).total_seconds()

        return {
            'analysis_count': self.analysis_count,
            'total_issues': self.total_issues,
            'critical_issues': self.critical_issues,
            'high_issues': self.high_issues,
            'medium_issues': self.medium_issues,
            'low_issues': self.low_issues,
            'average_confidence': avg_confidence,
            'overall_status': (
                'FAIL' if self.critical_issues > 0
                else 'REVIEW_REQUIRED' if self.high_issues > 0
                else 'PASS'
            ),
            'elapsed_seconds': elapsed,
            'average_issues_per_analysis': (
                self.total_issues / self.analysis_count
                if self.analysis_count > 0
                else 0.0
            )
        }

    def to_json(self) -> str:
        """
        Get summary as JSON string.

        Returns:
            JSON formatted summary
        """
        return json.dumps(self.get_summary())

    def reset(self):
        """Reset summary."""
        self.__init__()
