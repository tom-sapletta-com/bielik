#!/usr/bin/env python3
"""
Project Management Command for Bielik CLI.

This command provides session-based project management functionality:
- :project create <name> [description] - Create new project
- :project switch <id|name> - Switch to project
- :project list - List all projects
- :project info [id] - Show project information
- :project open [id] - Open project HTML in browser
"""

import os
import sys
import webbrowser
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add bielik to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bielik.cli.command_api import CommandBase
from bielik.project_manager import get_project_manager
from bielik.validators import validate_html_artifact


class ProjectCommand(CommandBase):
    """Project management command for session-based project handling."""
    
    def __init__(self):
        super().__init__()
        self.name = "project"
        self.description = "Session-based project management system"
        self.usage = """
Project Management Commands:
  :project create <name> [description] [--tags tag1,tag2]
      Create a new project with optional description and tags
      
  :project switch <id|name>
      Switch to an existing project (by ID or name)
      
  :project list
      List all projects in current session
      
  :project info [id]
      Show detailed information about project (current if no ID)
      
  :project open [id]
      Open project HTML representation in default browser
      
  :project validate [id]
      Validate project HTML artifact and metadata
      
Examples:
  :project create "My Analysis" "Data analysis project" --tags data,analysis
  :project switch my-proj
  :project list
  :project info
  :project open abc123ef
  :project validate
"""
    
    def execute(self, args: List[str], context: Dict[str, Any]) -> str:
        """Execute project management command."""
        if not args:
            return self._show_help()
        
        command = args[0].lower()
        project_manager = get_project_manager()
        
        try:
            if command == "create":
                return self._create_project(args[1:], project_manager)
            elif command == "switch":
                return self._switch_project(args[1:], project_manager)
            elif command == "list":
                return self._list_projects(project_manager)
            elif command == "info":
                return self._show_project_info(args[1:], project_manager)
            elif command == "open":
                return self._open_project(args[1:], project_manager)
            elif command == "validate":
                return self._validate_project(args[1:], project_manager)
            else:
                return "❌ Unknown project command: " + command + "\n\n" + self.usage
        
        except Exception as e:
            return "❌ Project command failed: " + str(e)
    
    def _create_project(self, args: List[str], project_manager) -> str:
        """Create a new project."""
        if not args:
            return "❌ Project name is required\nUsage: :project create <name> [description] [--tags tag1,tag2]"
        
        name = args[0]
        description = ""
        tags = []
        
        # Parse arguments
        i = 1
        while i < len(args):
            if args[i] == "--tags" and i + 1 < len(args):
                tags = [tag.strip() for tag in args[i + 1].split(",")]
                i += 2
            else:
                if not description:
                    description = args[i]
                i += 1
        
        try:
            project_id = project_manager.create_project(name, description, tags)
            project_manager.switch_to_project(project_id)
            
            project = project_manager.projects[project_id]
            
            return f"""✅ **Project Created Successfully**

🆔 **Project ID:** {project_id}
📛 **Name:** {name}
📝 **Description:** {description or 'No description'}
🏷️ **Tags:** {', '.join(tags) if tags else 'None'}
📅 **Created:** {project.created_at[:19].replace('T', ' ')}
📁 **HTML Path:** {project.html_path}

🎯 **Project is now active.** Use Context Provider Commands (like `calc:`, `pdf:`, `folder:`) to add artifacts to this project.

💡 **Quick Start:**
- Add folder analysis: `folder: ~/documents`
- Add calculation: `calc: 2 + 3 * 4`
- Add PDF analysis: `pdf: document.pdf`
- View project: `:project open`
"""
        
        except Exception as e:
            return f"❌ Failed to create project: {str(e)}"
    
    def _switch_project(self, args: List[str], project_manager) -> str:
        """Switch to an existing project."""
        if not args:
            return "❌ Project ID or name is required\nUsage: :project switch <id|name>"
        
        identifier = args[0]
        
        # Try to find project by ID or name
        target_project_id = None
        
        # First try exact ID match
        if identifier in project_manager.projects:
            target_project_id = identifier
        else:
            # Try to find by name or partial ID
            for project_id, project in project_manager.projects.items():
                if (project.name.lower() == identifier.lower() or 
                    project_id.startswith(identifier) or
                    identifier in project.name.lower()):
                    target_project_id = project_id
                    break
        
        if not target_project_id:
            available = "\n".join([
                f"  • {p.name} (ID: {pid[:8]}...)" 
                for pid, p in project_manager.projects.items()
            ])
            return f"""❌ Project not found: {identifier}

📋 **Available Projects:**
{available or '  No projects found'}

💡 Use `:project list` to see all projects or `:project create` to create a new one."""
        
        if project_manager.switch_to_project(target_project_id):
            project = project_manager.projects[target_project_id]
            return f"""✅ **Switched to Project**

🆔 **Project ID:** {target_project_id}
📛 **Name:** {project.name}
📝 **Description:** {project.description or 'No description'}
📊 **Artifacts:** {project.artifacts_count}
📅 **Last Updated:** {project.updated_at[:19].replace('T', ' ')}

🎯 **Project is now active.** New artifacts will be added to this project.
"""
        else:
            return f"❌ Failed to switch to project: {identifier}"
    
    def _list_projects(self, project_manager) -> str:
        """List all projects in current session."""
        projects = project_manager.list_projects()
        
        if not projects:
            return """📋 **No Projects Found**

🎯 Create your first project:
`:project create "My Project" "Description here"`

💡 Projects help organize your analysis artifacts and provide beautiful HTML representations for sharing and review.
"""
        
        # Sort by creation time (newest first)
        projects.sort(key=lambda p: p['created_at'], reverse=True)
        
        result = "📋 **Bielik Projects** (Current Session)\n\n"
        
        for project in projects:
            status = "🎯 **ACTIVE**" if project['is_current'] else "📁"
            
            result += f"""{status} **{project['name']}**
   🆔 ID: {project['id'][:8]}...
   📝 {project['description'] or 'No description'}
   📊 Artifacts: {project['artifacts_count']}
   🏷️ Tags: {', '.join(project['tags']) if project['tags'] else 'None'}
   📅 Created: {project['created_at'][:19].replace('T', ' ')}
   📅 Updated: {project['updated_at'][:19].replace('T', ' ')}

"""
        
        result += f"""💡 **Quick Actions:**
- Switch project: `:project switch <id|name>`
- View project: `:project open <id>`
- Project info: `:project info <id>`
- New project: `:project create <name>`
"""
        
        return result
    
    def _show_project_info(self, args: List[str], project_manager) -> str:
        """Show detailed project information."""
        project_id = args[0] if args else project_manager.current_project_id
        
        if not project_id:
            return "❌ No active project. Use `:project switch <id>` or specify project ID."
        
        if project_id not in project_manager.projects:
            return f"❌ Project not found: {project_id}"
        
        try:
            summary = project_manager.get_project_summary(project_id)
            
            if "error" in summary:
                return f"❌ {summary['error']}"
            
            project_data = summary['project']
            artifacts_data = summary['artifacts']
            
            result = f"""📊 **Project Information**

🆔 **ID:** {project_data['id']}
📛 **Name:** {project_data['name']}
📝 **Description:** {project_data['description'] or 'No description'}
🏷️ **Tags:** {', '.join(project_data['tags']) if project_data['tags'] else 'None'}
🔢 **Session ID:** {project_data['session_id'][:8]}...

📅 **Timeline:**
   Created: {project_data['created_at'][:19].replace('T', ' ')}
   Updated: {project_data['updated_at'][:19].replace('T', ' ')}

📊 **Statistics:**
   Artifacts: {project_data['artifacts_count']}
   Total Size: {summary['total_size']:,} bytes
   Artifact Types: {', '.join(summary['artifact_types']) if summary['artifact_types'] else 'None'}

📁 **HTML Path:** {project_data['html_path']}

"""
            
            if artifacts_data:
                result += "🎨 **Artifacts:**\n"
                for artifact in artifacts_data:
                    result += f"""   • **{artifact['name']}** ({artifact['type']})
     Command: {artifact['command']}
     Size: {artifact['size_bytes']:,} bytes
     Created: {artifact['created_at'][:19].replace('T', ' ')}

"""
            else:
                result += """🎨 **Artifacts:** None yet

💡 Add artifacts using Context Provider Commands:
   `folder: ~/documents` - Analyze folder structure
   `calc: 2 + 3 * 4` - Mathematical calculations  
   `pdf: document.pdf` - Document analysis
"""
            
            return result
            
        except Exception as e:
            return f"❌ Failed to get project info: {str(e)}"
    
    def _open_project(self, args: List[str], project_manager) -> str:
        """Open project HTML representation in browser."""
        project_id = args[0] if args else project_manager.current_project_id
        
        if not project_id:
            return "❌ No active project. Use `:project switch <id>` or specify project ID."
        
        if project_id not in project_manager.projects:
            return f"❌ Project not found: {project_id}"
        
        try:
            project = project_manager.projects[project_id]
            html_path = Path(project.html_path)
            
            if not html_path.exists():
                return f"❌ Project HTML file not found: {html_path}"
            
            # Open in default browser
            webbrowser.open(f"file://{html_path.absolute()}")
            
            return f"""🌐 **Project Opened in Browser**

🆔 **Project:** {project.name}
📁 **HTML File:** {html_path}
🔗 **URL:** file://{html_path.absolute()}

💡 The project page includes:
   - Interactive artifact viewer
   - Project metadata
   - Beautiful formatting
   - Offline browsing capability
"""
        
        except Exception as e:
            return f"❌ Failed to open project: {str(e)}"
    
    def _validate_project(self, args: List[str], project_manager) -> str:
        """Validate project HTML artifact and metadata."""
        project_id = args[0] if args else project_manager.current_project_id
        
        if not project_id:
            return "❌ No active project. Use `:project switch <id>` or specify project ID."
        
        if project_id not in project_manager.projects:
            return f"❌ Project not found: {project_id}"
        
        try:
            project = project_manager.projects[project_id]
            html_path = Path(project.html_path)
            
            if not html_path.exists():
                return f"❌ Project HTML file not found: {html_path}"
            
            # Validate HTML artifact
            result = validate_html_artifact(html_path)
            
            status = "✅ **VALID**" if result.is_valid else "❌ **INVALID**"
            
            response = f"""🔍 **Project Validation Results**

🆔 **Project:** {project.name}
📊 **Status:** {status}

"""
            
            if result.errors:
                response += "❌ **Errors:**\n"
                for error in result.errors:
                    response += "   • " + error + "\n"
                response += "\n"
            
            if result.warnings:
                response += "⚠️ **Warnings:**\n"
                for warning in result.warnings:
                    response += "   • " + warning + "\n"
                response += "\n"
            
            if result.suggestions:
                response += "💡 **Suggestions:**\n"
                for suggestion in result.suggestions:
                    response += "   • " + suggestion + "\n"
                response += "\n"
            
            if result.metadata:
                response += "📊 **Metadata:**\n"
                for key, value in result.metadata.items():
                    if key != 'content_hash':  # Skip long hash
                        response += "   • " + key + ": " + str(value) + "\n"
            
            return response
            
        except Exception as e:
            return f"❌ Failed to validate project: {str(e)}"
    
    def get_help(self) -> str:
        """Return help information (required by CommandBase)."""
        return f"""🦅 **Bielik Project Management**

{self.usage}

💡 **About Projects:**
Projects help organize your analysis artifacts with beautiful HTML representations.
Each project creates a physical folder with an interactive HTML file that can be 
viewed in any browser, shared, or archived.

🎯 **Workflow:**
1. Create project: `:project create "Analysis"`
2. Add artifacts: `folder: ~/data`, `calc: 2+2`, `pdf: file.pdf`
3. View results: `:project open`
4. Switch projects: `:project switch <name>`

📁 **Project Storage:** ./bielik_projects/
"""
    
    def _show_help(self) -> str:
        """Show help information."""
        return self.get_help()


# Command registration
def get_command():
    """Return command instance for registration."""
    return ProjectCommand()
