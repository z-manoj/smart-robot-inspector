"""
Report generation for inspection results.
Creates JSON, markdown, and HTML reports from inspection data.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate inspection reports in multiple formats."""

    def __init__(self, output_dir: str = "./reports"):
        """
        Initialize report generator.

        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_inspection_report(
        self,
        inspection_id: str,
        robot_path: List[Dict],
        inspection_points: List[Dict],
        start_time: str = None,
        end_time: str = None,
    ) -> Dict:
        """
        Create structured inspection report.

        Args:
            inspection_id: Unique inspection identifier
            robot_path: List of waypoints with x, y coordinates
            inspection_points: List of analysis results at each waypoint
            start_time: Inspection start timestamp
            end_time: Inspection end timestamp

        Returns:
            Complete inspection report dict
        """
        if not start_time:
            start_time = datetime.now().isoformat()
        if not end_time:
            end_time = datetime.now().isoformat()

        # Aggregate statistics
        all_issues = []
        issue_counts_by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        pass_count = 0
        fail_count = 0

        for point in inspection_points:
            analysis = point.get("image_analysis", {})
            for issue in analysis.get("detected_issues", []):
                all_issues.append(issue)
                severity = issue.get("severity", "UNKNOWN")
                if severity in issue_counts_by_severity:
                    issue_counts_by_severity[severity] += 1

            status = analysis.get("overall_status", "UNKNOWN")
            if status == "PASS":
                pass_count += 1
            elif status == "FAIL":
                fail_count += 1

        # Determine overall status
        if issue_counts_by_severity["CRITICAL"] > 0:
            overall_status = "FAIL"
        elif issue_counts_by_severity["HIGH"] > 0:
            overall_status = "REVIEW_REQUIRED"
        else:
            overall_status = "PASS"

        report = {
            "inspection_id": inspection_id,
            "timestamp": {
                "start": start_time,
                "end": end_time,
                "generated": datetime.now().isoformat(),
            },
            "summary": {
                "total_inspection_points": len(inspection_points),
                "waypoints_visited": len(robot_path),
                "overall_status": overall_status,
                "total_issues": len(all_issues),
                "issues_by_severity": issue_counts_by_severity,
                "points_passed": pass_count,
                "points_failed": fail_count,
            },
            "robot_path": robot_path,
            "inspection_points": inspection_points,
            "critical_findings": [issue for issue in all_issues if issue.get("severity") == "CRITICAL"],
            "high_priority_findings": [issue for issue in all_issues if issue.get("severity") == "HIGH"],
            "recommendations": self._generate_recommendations(all_issues, overall_status),
        }

        return report

    def _generate_recommendations(self, all_issues: List[Dict], overall_status: str) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []

        if overall_status == "FAIL":
            recommendations.append("URGENT: Address all critical issues before continuing operations")

        critical_issues = [i for i in all_issues if i.get("severity") == "CRITICAL"]
        if critical_issues:
            recommendations.append(f"Stop and address {len(critical_issues)} critical defect(s)")

        high_issues = [i for i in all_issues if i.get("severity") == "HIGH"]
        if high_issues:
            recommendations.append(f"Schedule maintenance for {len(high_issues)} high-priority issue(s)")

        if not all_issues:
            recommendations.append("Inspection passed all checks - continue normal operations")

        return recommendations

    def export_json(self, report: Dict, filename: Optional[str] = None) -> Path:
        """
        Export report as JSON.

        Args:
            report: Report dict
            filename: Output filename (default: auto-generated)

        Returns:
            Path to saved file
        """
        if not filename:
            filename = f"inspection_{report['inspection_id']}.json"

        filepath = self.output_dir / filename
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"JSON report saved to {filepath}")
        return filepath

    def export_markdown(self, report: Dict, filename: Optional[str] = None) -> Path:
        """
        Export report as markdown.

        Args:
            report: Report dict
            filename: Output filename (default: auto-generated)

        Returns:
            Path to saved file
        """
        if not filename:
            filename = f"inspection_{report['inspection_id']}.md"

        filepath = self.output_dir / filename

        # Build markdown
        md_lines = [
            f"# Inspection Report: {report['inspection_id']}",
            "",
            f"**Generated**: {report['timestamp']['generated']}",
            f"**Duration**: {report['timestamp']['start']} to {report['timestamp']['end']}",
            "",
            "## Summary",
            "",
            f"- **Overall Status**: `{report['summary']['overall_status']}`",
            f"- **Inspection Points**: {report['summary']['total_inspection_points']}",
            f"- **Total Issues Found**: {report['summary']['total_issues']}",
            f"- **Points Passed**: {report['summary']['points_passed']}",
            f"- **Points Failed**: {report['summary']['points_failed']}",
            "",
            "## Issue Breakdown",
            "",
            f"- **Critical**: {report['summary']['issues_by_severity'].get('CRITICAL', 0)}",
            f"- **High**: {report['summary']['issues_by_severity'].get('HIGH', 0)}",
            f"- **Medium**: {report['summary']['issues_by_severity'].get('MEDIUM', 0)}",
            f"- **Low**: {report['summary']['issues_by_severity'].get('LOW', 0)}",
            "",
        ]

        # Critical findings
        if report["critical_findings"]:
            md_lines.extend([
                "## ⚠️ Critical Findings",
                "",
            ])
            for issue in report["critical_findings"]:
                md_lines.extend([
                    f"### {issue.get('issue', 'Unknown Issue')}",
                    f"- **Location**: {issue.get('location', 'N/A')}",
                    f"- **Recommendation**: {issue.get('recommendation', 'N/A')}",
                    "",
                ])

        # High priority findings
        if report["high_priority_findings"]:
            md_lines.extend([
                "## ⚠️ High Priority Findings",
                "",
            ])
            for issue in report["high_priority_findings"]:
                md_lines.extend([
                    f"### {issue.get('issue', 'Unknown Issue')}",
                    f"- **Location**: {issue.get('location', 'N/A')}",
                    f"- **Recommendation**: {issue.get('recommendation', 'N/A')}",
                    "",
                ])

        # Recommendations
        md_lines.extend([
            "## Recommendations",
            "",
        ])
        for rec in report["recommendations"]:
            md_lines.append(f"- {rec}")
        md_lines.append("")

        # Robot path
        md_lines.extend([
            "## Robot Path",
            "",
            "| Waypoint | X | Y |",
            "|----------|---|---|",
        ])
        for i, point in enumerate(report["robot_path"]):
            md_lines.append(f"| {i} | {point.get('x', 0):.2f} | {point.get('y', 0):.2f} |")
        md_lines.append("")

        with open(filepath, "w") as f:
            f.write("\n".join(md_lines))

        logger.info(f"Markdown report saved to {filepath}")
        return filepath

    def export_html(self, report: Dict, filename: Optional[str] = None) -> Path:
        """
        Export report as HTML.

        Args:
            report: Report dict
            filename: Output filename (default: auto-generated)

        Returns:
            Path to saved file
        """
        if not filename:
            filename = f"inspection_{report['inspection_id']}.html"

        filepath = self.output_dir / filename

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Inspection Report: {report['inspection_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }}
        h2 {{ color: #0066cc; margin-top: 30px; }}
        .status-PASS {{ color: green; font-weight: bold; }}
        .status-FAIL {{ color: red; font-weight: bold; }}
        .status-REVIEW_REQUIRED {{ color: orange; font-weight: bold; }}
        .issue-CRITICAL {{ background: #ffe0e0; padding: 10px; margin: 10px 0; border-left: 4px solid red; }}
        .issue-HIGH {{ background: #fff4e0; padding: 10px; margin: 10px 0; border-left: 4px solid orange; }}
        .issue-MEDIUM {{ background: #fffde0; padding: 10px; margin: 10px 0; border-left: 4px solid #ffcc00; }}
        .issue-LOW {{ background: #e0f0ff; padding: 10px; margin: 10px 0; border-left: 4px solid #0066cc; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #0066cc; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .summary-box {{ background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Inspection Report: {report['inspection_id']}</h1>
        <p><strong>Generated</strong>: {report['timestamp']['generated']}</p>
        <p><strong>Duration</strong>: {report['timestamp']['start']} to {report['timestamp']['end']}</p>

        <div class="summary-box">
            <h2>Summary</h2>
            <p><strong>Overall Status</strong>: <span class="status-{report['summary']['overall_status']}">{report['summary']['overall_status']}</span></p>
            <table>
                <tr>
                    <td>Inspection Points</td>
                    <td>{report['summary']['total_inspection_points']}</td>
                </tr>
                <tr>
                    <td>Total Issues</td>
                    <td>{report['summary']['total_issues']}</td>
                </tr>
                <tr>
                    <td>Points Passed</td>
                    <td>{report['summary']['points_passed']}</td>
                </tr>
                <tr>
                    <td>Points Failed</td>
                    <td>{report['summary']['points_failed']}</td>
                </tr>
            </table>
        </div>

        <h2>Issue Breakdown</h2>
        <table>
            <tr>
                <th>Severity</th>
                <th>Count</th>
            </tr>
            <tr>
                <td>Critical</td>
                <td>{report['summary']['issues_by_severity'].get('CRITICAL', 0)}</td>
            </tr>
            <tr>
                <td>High</td>
                <td>{report['summary']['issues_by_severity'].get('HIGH', 0)}</td>
            </tr>
            <tr>
                <td>Medium</td>
                <td>{report['summary']['issues_by_severity'].get('MEDIUM', 0)}</td>
            </tr>
            <tr>
                <td>Low</td>
                <td>{report['summary']['issues_by_severity'].get('LOW', 0)}</td>
            </tr>
        </table>
"""

        # Add findings
        if report["critical_findings"]:
            html_content += "<h2>Critical Findings</h2>"
            for issue in report["critical_findings"]:
                html_content += f"""
        <div class="issue-CRITICAL">
            <strong>{issue.get('issue', 'Unknown')}</strong><br>
            Location: {issue.get('location', 'N/A')}<br>
            Recommendation: {issue.get('recommendation', 'N/A')}
        </div>
"""

        html_content += """
    </div>
</body>
</html>"""

        with open(filepath, "w") as f:
            f.write(html_content)

        logger.info(f"HTML report saved to {filepath}")
        return filepath
