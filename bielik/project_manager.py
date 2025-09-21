#!/usr/bin/env python3
"""
Bielik Project Manager - Session-based project management system.

This module manages projects within Bielik sessions, allowing users to:
- Create and manage multiple projects per session
- Generate HTML-based artifact representations with metadata
- Validate HTML artifacts, .env files, and command scripts
- Store projects with physical HTML representation for browser viewing
"""

import os
import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


@dataclass
class ProjectMetadata:
    """Project metadata structure."""
    id: str
    name: str
    description: str
    created_at: str
    updated_at: str
    artifacts_count: int
    html_path: str
    tags: List[str]
    session_id: str


@dataclass
class ArtifactMetadata:
    """Artifact metadata structure."""
    id: str
    name: str
    type: str  # folder, calc, pdf, etc.
    command: str
    created_at: str
    size_bytes: int
    checksum: str
    project_id: str


class ProjectManager:
    """Manages Bielik projects and their HTML representations."""
    
    def __init__(self, base_dir: str = "./bielik_projects"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Session management
        self.session_id = str(uuid.uuid4())
        self.current_project_id: Optional[str] = None
        self.projects: Dict[str, ProjectMetadata] = {}
        self.artifacts: Dict[str, List[ArtifactMetadata]] = {}
        
        # Load existing projects
        self._load_projects()
    
    def create_project(self, name: str, description: str = "", tags: List[str] = None) -> str:
        """
        Create a new project with HTML representation.
        
        Args:
            name: Project name
            description: Project description
            tags: Project tags for categorization
            
        Returns:
            Project ID
        """
        if tags is None:
            tags = []
            
        project_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        # Create project directory
        project_dir = self.base_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        # Create HTML representation path
        html_path = str(project_dir / "index.html")
        
        # Create project metadata
        metadata = ProjectMetadata(
            id=project_id,
            name=name,
            description=description,
            created_at=timestamp,
            updated_at=timestamp,
            artifacts_count=0,
            html_path=html_path,
            tags=tags,
            session_id=self.session_id
        )
        
        self.projects[project_id] = metadata
        self.artifacts[project_id] = []
        
        # Generate initial HTML representation
        self._generate_project_html(project_id)
        
        # Save project metadata
        self._save_project_metadata(project_id)
        
        return project_id
    
    def switch_to_project(self, project_id: str) -> bool:
        """Switch current working project."""
        if project_id in self.projects:
            self.current_project_id = project_id
            return True
        return False
    
    def add_artifact(self, command_type: str, command: str, content: str, 
                    name: str = None) -> str:
        """
        Add an artifact to the current project.
        
        Args:
            command_type: Type of command (folder, calc, pdf, etc.)
            command: Original command used
            content: Artifact content/data
            name: Optional artifact name
            
        Returns:
            Artifact ID
        """
        if not self.current_project_id:
            raise ValueError("No active project. Create or switch to a project first.")
        
        artifact_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        if name is None:
            name = command_type + "_" + datetime.datetime.now().strftime('%H%M%S')
        
        # Calculate content size and checksum
        content_bytes = content.encode('utf-8')
        size_bytes = len(content_bytes)
        checksum = str(hash(content))  # Simple checksum
        
        # Create artifact metadata
        artifact = ArtifactMetadata(
            id=artifact_id,
            name=name,
            type=command_type,
            command=command,
            created_at=timestamp,
            size_bytes=size_bytes,
            checksum=checksum,
            project_id=self.current_project_id
        )
        
        # Add to project
        self.artifacts[self.current_project_id].append(artifact)
        
        # Update project metadata
        project = self.projects[self.current_project_id]
        project.artifacts_count += 1
        project.updated_at = timestamp
        
        # Add artifact to HTML representation
        self._add_artifact_to_html(self.current_project_id, artifact, content)
        
        # Save updated metadata
        self._save_project_metadata(self.current_project_id)
        
        return artifact_id
    
    def get_project_summary(self, project_id: str = None) -> Dict[str, Any]:
        """Get project summary information."""
        if project_id is None:
            project_id = self.current_project_id
            
        if not project_id or project_id not in self.projects:
            return {"error": "Project not found"}
        
        project = self.projects[project_id]
        artifacts = self.artifacts.get(project_id, [])
        
        return {
            "project": asdict(project),
            "artifacts": [asdict(a) for a in artifacts],
            "total_size": sum(a.size_bytes for a in artifacts),
            "artifact_types": list(set(a.type for a in artifacts))
        }
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects in current session."""
        return [
            {
                "id": project_id,
                "name": project.name,
                "description": project.description,
                "artifacts_count": project.artifacts_count,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "tags": project.tags,
                "is_current": project_id == self.current_project_id
            }
            for project_id, project in self.projects.items()
        ]
    
    def _generate_project_html(self, project_id: str):
        """Generate HTML representation for project using template-based approach."""
        project = self.projects[project_id]
        artifacts = self.artifacts.get(project_id, [])
        
        # Build the complete HTML using simple string building
        html_parts = []
        
        # HTML Document start
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html lang="en">')
        
        # Head section
        self._build_html_head(html_parts, project)
        
        # Body start
        html_parts.append('<body>')
        
        # Project header
        self._build_project_header(html_parts, project)
        
        # Artifacts container
        html_parts.append('<div class="artifacts-container">')
        
        # Build artifacts or empty state
        if artifacts:
            self._build_artifacts_section(html_parts, artifacts)
        else:
            self._build_empty_state(html_parts)
        
        # Close containers and add footer
        html_parts.append('</div>')
        self._build_footer_script(html_parts)
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        # Join all parts and write to file
        html_content = '\n'.join(html_parts)
        html_path = Path(project.html_path)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _build_html_head(self, html_parts, project):
        """Build HTML head section."""
        project_metadata_json = json.dumps(asdict(project))
        tags_joined = ','.join(project.tags)
        
        html_parts.extend([
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '    <title>Bielik Project: ' + project.name + '</title>',
            '    <meta name="project-name" content="' + project.name + '">',
            '    <meta name="project-description" content="' + project.description + '">',
            '    <meta name="created-at" content="' + project.created_at + '">',
            '    <meta name="updated-at" content="' + project.updated_at + '">',
            '    <meta name="artifacts-count" content="' + str(project.artifacts_count) + '">',
            '    <meta name="tags" content="' + tags_joined + '">',
            '    <meta name="project-metadata" content=\'' + project_metadata_json + '\'>',
            self._get_css_styles(),
            '</head>'
        ])
    
    def _build_project_header(self, html_parts, project):
        """Build project header section."""
        # Build tags HTML if they exist
        tags_html = ''
        if project.tags:
            tag_spans = []
            for tag in project.tags:
                tag_spans.append('<span class="tag">' + tag + '</span>')
            tags_html = '<div class="tags">' + ''.join(tag_spans) + '</div>'
        
        html_parts.extend([
            '<div class="project-header">',
            '    <h1 class="project-title">🦅 ' + project.name + '</h1>',
            '    <p>' + project.description + '</p>',
            '    <div class="project-meta">',
            '        <span class="meta-item">📅 Created: ' + project.created_at[:10] + '</span>',
            '        <span class="meta-item">📝 Artifacts: ' + str(project.artifacts_count) + '</span>',
            '        <span class="meta-item">🆔 ID: ' + project.id[:8] + '</span>',
            '    </div>',
            '    ' + tags_html,
            '</div>'
        ])
    
    def _build_artifacts_section(self, html_parts, artifacts):
        """Build artifacts section."""
        for artifact in artifacts:
            html_parts.extend([
                '    <div class="artifact"',
                '         data-artifact-id="' + artifact.id + '"',
                '         data-artifact-type="' + artifact.type + '"',
                '         data-created-at="' + artifact.created_at + '"',
                '         data-checksum="' + artifact.checksum + '"',
                '         data-size-bytes="' + str(artifact.size_bytes) + '">',
                '        <div class="artifact-header">',
                '            <h3 class="artifact-title">' + artifact.name + '</h3>',
                '            <span class="artifact-type">' + artifact.type + '</span>',
                '        </div>',
                '        <div class="artifact-command">Command: ' + artifact.command + '</div>',
                '        <div class="artifact-content" id="content-' + artifact.id + '">',
                '            <!-- Content will be populated separately -->',
                '        </div>',
                '    </div>'
            ])
    
    def _build_empty_state(self, html_parts):
        """Build empty state section."""
        html_parts.extend([
            '    <div class="empty-state">',
            '        <h3>No artifacts yet</h3>',
            '        <p>Use Context Provider Commands to create artifacts for this project.</p>',
            '        <p>Example: <code>folder: ~/documents</code>, <code>calc: 2 + 3 * 4</code>, <code>pdf: document.pdf</code></p>',
            '    </div>'
        ])
    
    def _build_footer_script(self, html_parts):
        """Build footer script section."""
        html_parts.extend([
            '<script>',
            '    console.log("Bielik Project loaded:", document.title);',
            '    const footer = document.createElement("div");',
            '    footer.style.cssText = "text-align: center; margin-top: 40px; padding: 20px; color: #666; border-top: 1px solid #eee;";',
            '    footer.innerHTML = "<p>Generated by Bielik CLI on " + new Date().toLocaleString() + "</p>";',
            '    document.body.appendChild(footer);',
            '</script>'
        ])
    
    def _get_css_styles(self):
        """Get CSS styles as a string."""
        return '''    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .project-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .project-title {
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }
        .project-meta {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            opacity: 0.9;
        }
        .meta-item {
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .artifacts-container {
            display: grid;
            gap: 20px;
        }
        .artifact {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .artifact-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .artifact-title {
            margin: 0;
            color: #333;
        }
        .artifact-type {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .artifact-command {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            margin-bottom: 15px;
            border: 1px solid #e9ecef;
        }
        .artifact-content {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e9ecef;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: monospace;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        .tags {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .tag {
            background: #e9ecef;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            color: #495057;
        }
    </style>'''
    
    def _add_artifact_to_html(self, project_id: str, artifact: ArtifactMetadata, content: str):
        """Add artifact content to existing HTML file."""
        # For now, regenerate the entire HTML
        # In production, this could be optimized to append only new artifacts
        self._generate_project_html(project_id)
        
        # Update the specific artifact content via JavaScript injection or server-side update
        html_path = Path(self.projects[project_id].html_path)
        if html_path.exists():
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Replace the placeholder content for this artifact
            content_placeholder = '<!-- Content will be populated separately -->'
            actual_content = content.replace('<', '&lt;').replace('>', '&gt;')  # Escape HTML
            
            # Find and replace the specific artifact content
            soup = BeautifulSoup(html_content, 'html.parser')
            content_div = soup.find('div', {'id': 'content-' + artifact.id})
            if content_div:
                content_div.clear()
                content_div.append(actual_content)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
    
    def _save_project_metadata(self, project_id: str):
        """Save project metadata to JSON file."""
        project_dir = self.base_dir / project_id
        metadata_file = project_dir / "metadata.json"
        
        metadata = {
            "project": asdict(self.projects[project_id]),
            "artifacts": [asdict(a) for a in self.artifacts.get(project_id, [])]
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _load_projects(self):
        """Load existing projects from disk."""
        if not self.base_dir.exists():
            return
        
        for project_dir in self.base_dir.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        project_data = data.get("project", {})
                        project_id = project_data.get("id")
                        
                        if project_id:
                            self.projects[project_id] = ProjectMetadata(**project_data)
                            
                            artifacts_data = data.get("artifacts", [])
                            self.artifacts[project_id] = [
                                ArtifactMetadata(**a) for a in artifacts_data
                            ]
                    except Exception as e:
                        print("⚠️ Failed to load project from " + str(project_dir) + ": " + str(e))


# Global project manager instance
_project_manager: Optional[ProjectManager] = None


def get_project_manager() -> ProjectManager:
    """Get global project manager instance."""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager


def create_project(name: str, description: str = "", tags: List[str] = None) -> str:
    """Create a new project (convenience function)."""
    return get_project_manager().create_project(name, description, tags)


def add_artifact(command_type: str, command: str, content: str, name: str = None) -> str:
    """Add artifact to current project (convenience function)."""
    return get_project_manager().add_artifact(command_type, command, content, name)
