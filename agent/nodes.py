from .state import AgentState
from typing import Dict, Any
from pathlib import Path
from .constants import SECRET_PATTERNS
from .cli import TestMemory
import re


def check_command(state: AgentState) -> Dict[str, Any]:
    """checks that the user has entered the command"""
    messages = state.get('messages',[])
    if not messages:
        return {
            'is_safe': False,
            'final_answer': 'please enter the command' 
        }
    
    last_message = messages[-1]
    content = last_message.get('content', '').strip()
    if not content:
        return {
            'is_safe': False,
            'final_answer': 'please enter the command' 
        }
    return {
        'command': content,
    }


def safety_validator(state: AgentState) -> Dict[str, Any]:
    """
    checks that the files in the command are inside PROJECT_ROOT 
    and there is no access to secret/system files
    """
    command = state.get('command')
    if not command:
        return {
            'is_safe': False,
            'final_answer': 'please enter the command' 
        }
    project_root = state.get('project_root', '/workspace')
    file_paths = re.findall(
        r'(?:(?<=[\s"\'])(?:\/|\.\/)[^\s"\']*|(?<=[\s"\'])[^\s"\']+\.\w+)',
        command
    )

    if not file_paths:
        return {'is_safe': True}

    validated_paths = []
    for path in file_paths:
        path = path.strip('"\'').strip()
        if path in ['python', 'pip', 'npm', 'node', 'git', 'ls', 'cat', 'echo']:
            continue

        try:
            if path.startswith('/'):
                full_path = Path(path)
            else:
                full_path = Path(project_root) / path

            resolved = full_path.resolve()
            project_root_resolved = Path(project_root).resolve()

            try:
                resolved.relative_to(project_root_resolved)
            except ValueError:
                return {
                    'is_safe': False,
                    'final_answer': f'access denied: path "{path}" is outside the project ({project_root})'
                }
            
            path_str = str(resolved)
            for pattern in SECRET_PATTERNS:
                if re.search(pattern, path_str, re.IGNORECASE):
                    return {
                        'is_safe': False,
                        'final_answer': f'access denied: "{path}" contains sensitive information'
                    }
            if not resolved.exists() and not any(cmd in command for cmd in ['create', 'new', 'write']):
                validated_paths.append({
                    'path': str(resolved),
                    'exists': False,
                    'warning': f'file not found: {path}'
                })
            else:
                validated_paths.append({
                    'path': str(resolved),
                    'exists': resolved.exists(),
                    'is_file': resolved.is_file() if resolved.exists() else False
                })
        except Exception as e:
            return {
                'is_safe': False,
                'final_answer': f'error when checking the path "{path}": {str(e)}'
            }
    return {
        "is_safe": True,
        "validated_paths": validated_paths,
        "files_to_read": [vp['path'] for vp in validated_paths if vp.get('exists', False)]
    }

# TODO: call llm for more complex planning
def planner(state, model_name) -> Dict[str, Any]:
    if state.get('command'):
        plan = [
            f"command: {state.command}",
            "gather context",
            "analyze the code",
            f"generate a {state.command}-response"
        ]
    return {
        'command': state.command,
        'selected_code': state.selected_code,
        'plan': plan,
        'next_action': 'continue'
    }


def context_builder(state, memory) -> Dict[str, Any]:
    """it collects context from memory and determines where to go next"""
    messages = state.get('messages',[])
    last_message = messages[-1] if messages else {}
    query = last_message.get('content', '')
    command = state.get('command', 'explain')
    selected_code = state.get('selected_code', '')

    context = {
        'query': query,
        'command': command,
        'selected_code': selected_code,
        "needs_files": False,
        "needs_indexing": False,
        "needs_vector_search": False,
        "files_to_read": [],
        "search_terms": []
    }

    if selected_code and ('import' in selected_code or 'from' in selected_code):
        context['needs_files'] = True
        for line in selected_code.split('\n'):
            if 'import' in line or 'from' in line:
                # TODO: file parsing
                ['files_to_read'] = re.findall(
                    r'(?:(?<=[\s"\'])(?:\/|\.\/)[^\s"\']*|(?<=[\s"\'])[^\s"\']+\.\w+)',
                    line
                )

    # TODO: implement whether a search is needed in a vector database needs_vector_search, needs_indexing

    return {"context": context}