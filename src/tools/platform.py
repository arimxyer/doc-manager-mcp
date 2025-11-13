"""Platform detection tools for doc-manager."""

from pathlib import Path
import json

from ..models import DetectPlatformInput
from ..constants import ResponseFormat
from ..utils import detect_project_language, handle_error

async def detect_platform(params: DetectPlatformInput) -> str:
    """Detect and recommend documentation platform for the project.

    This tool analyzes the project structure to detect existing documentation
    platforms or recommend the most suitable platform based on project characteristics.

    Args:
        params (DetectPlatformInput): Validated input parameters containing:
            - project_path (str): Absolute path to project root
            - response_format (ResponseFormat): Output format (markdown or json)

    Returns:
        str: Platform detection results with recommendation and rationale

    Examples:
        - Use when: Choosing a documentation platform for a new project
        - Use when: Migrating from one platform to another
        - Use when: Verifying current platform detection

    Error Handling:
        - Returns error if project_path doesn't exist
        - Returns "unknown" platform if no platform detected
    """
    try:
        project_path = Path(params.project_path).resolve()

        if not project_path.exists():
            return f"Error: Project path does not exist: {project_path}"

        # Platform detection logic
        detected_platforms = []

        # Hugo detection
        if (project_path / "hugo.toml").exists() or (project_path / "hugo.yaml").exists() or (project_path / "config.toml").exists():
            detected_platforms.append({
                "platform": "hugo",
                "confidence": "high",
                "evidence": ["Found Hugo configuration file"]
            })

        # Docusaurus detection
        if (project_path / "docusaurus.config.js").exists() or (project_path / "docusaurus.config.ts").exists():
            detected_platforms.append({
                "platform": "docusaurus",
                "confidence": "high",
                "evidence": ["Found Docusaurus configuration file"]
            })

        # MkDocs detection
        if (project_path / "mkdocs.yml").exists():
            detected_platforms.append({
                "platform": "mkdocs",
                "confidence": "high",
                "evidence": ["Found mkdocs.yml configuration"]
            })

        # Sphinx detection
        if (project_path / "docs" / "conf.py").exists() or (project_path / "doc" / "conf.py").exists():
            detected_platforms.append({
                "platform": "sphinx",
                "confidence": "high",
                "evidence": ["Found Sphinx conf.py"]
            })

        # VitePress detection
        if (project_path / ".vitepress" / "config.js").exists() or (project_path / ".vitepress" / "config.ts").exists():
            detected_platforms.append({
                "platform": "vitepress",
                "confidence": "high",
                "evidence": ["Found VitePress configuration"]
            })

        # Determine recommendation
        language = detect_project_language(project_path)
        recommendation = None
        rationale = []

        if detected_platforms:
            # Use detected platform
            recommendation = detected_platforms[0]["platform"]
            rationale.append(f"Detected existing {recommendation} platform")
        else:
            # Recommend based on project characteristics
            if language == "Go":
                recommendation = "hugo"
                rationale.append("Hugo is written in Go and popular in Go ecosystem")
            elif language in ["JavaScript/TypeScript", "Node.js"]:
                recommendation = "docusaurus"
                rationale.append("Docusaurus is React-based and popular in JavaScript ecosystem")
            elif language == "Python":
                recommendation = "mkdocs"
                rationale.append("MkDocs is Python-based and popular in Python ecosystem")
            else:
                recommendation = "hugo"
                rationale.append("Hugo is fast, language-agnostic, and widely adopted")

        # Format response
        if params.response_format == ResponseFormat.JSON:
            result = {
                "detected_platforms": detected_platforms,
                "recommendation": recommendation,
                "rationale": rationale,
                "project_language": language
            }
            return json.dumps(result, indent=2)
        else:
            lines = ["# Documentation Platform Detection", ""]

            if detected_platforms:
                lines.append("## Detected Platforms")
                for platform in detected_platforms:
                    lines.append(f"- **{platform['platform'].upper()}** ({platform['confidence']} confidence)")
                    for evidence in platform['evidence']:
                        lines.append(f"  - {evidence}")
                lines.append("")

            lines.append("## Recommendation")
            lines.append(f"**{recommendation.upper()}**")
            lines.append("")
            lines.append("### Rationale:")
            for reason in rationale:
                lines.append(f"- {reason}")
            lines.append("")
            lines.append(f"### Project Context:")
            lines.append(f"- Primary Language: {language}")

            return "\n".join(lines)

    except Exception as e:
        return handle_error(e, "detect_platform")
