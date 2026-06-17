from langgraph.graph import END

def rout_after_check(state) -> str:
    if state.get('is_safe'):
        return 'planner'
    return END


def rout_after_planner(state) -> str:
    if state.get('plan'):
        return 'context_builder'
    return END


def rout_after_context_builder(state) -> list:
    context = state.get('context', {})
    routes = []
    if context.get('files_to_read'):
        routes.append('read_files')
    if context.get('project_index'):
        routes.append('project_index')
    if context.get('vector_db_query'):
        routes.append('invoke_vector_db')
    return routes if routes else END


def rout_after_assistant(state) -> str:
    if state.get('iteration', 0) < 5 and state.get('tool_calls'):
        return 'tools_executor'
    return 'postprocessing'