from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from .state import AgentState
from .nodes import (
    check_command,
    safety_validator,
    planner,
    context_builder,
    read_files,
    tools_executor,
    assistant,
    postprocessing,
    project_index,
    invoke_vector_db
)

# forks in the road
from routing import (
    rout_after_planner,
    rout_after_assistant,
    rout_after_check,
    rout_after_context_builder,
    rout_after_tools
)


class DevAgentGraph:
    def __init__(self, model_name,memory, base_url='https://openrouter.ai/api/v1'):
        self.model_name = model_name
        self.memory = memory
        self.base_url = base_url

        self._graph = None
        self._compiled=None

        self._build_graph()

    def _build_graph(self):
        self._graph = StateGraph(AgentState)

        # nodes
        self._graph.add_node('check_command', lambda state: check_command(state))
        self._graph.add_node('safety_validator', lambda state: safety_validator(state))
        self._graph.add_node('planner', lambda state: planner(state, self.model_name))
        self._graph.add_node('context_builder', lambda state: context_builder(state, self.memory))
        self._graph.add_node('project_index', lambda state: project_index(state, self.model_name, self.memory, self.base_url))
        self._graph.add_node('invoke_vector_db', lambda state: invoke_vector_db(state, self.model_name, self.memory, self.base_url))
        self._graph.add_node('read_files', lambda state: read_files(state))
        self._graph.add_node('tools_executor', lambda state: tools_executor(state))
        self._graph.add_node('assistant', lambda state: assistant(state, self.model_name, self.memory, self.base_url))
        self._graph.add_node('postprocessing', lambda state: postprocessing(state, self.model_name, self.memory, self.base_url))

        # edges
        self._graph.set_entry_point('check_command')
        self._graph.add_edge('check_command', 'safety_validator')
        self._graph.add_conditional_edges('safety_validator', rout_after_check, ['planner', END])
        self._graph.add_conditional_edges('planner', rout_after_planner, ['context_builder', END])
        self._graph.add_conditional_edges('context_builder', rout_after_context_builder, ['read_files', 'project_index', 'invoke_vector_db'])
        self._graph.add_edge('read_files', 'tools_executor')
        self._graph.add_conditional_edges('tools_executor', rout_after_tools, ['assistant', 'invoke_vector_db'])
        self._graph.add_conditional_edges('assistant', rout_after_assistant, ['postprocessing', 'tools_executor'])
        self._graph.add_edge('postprocessing', END)
        
        checkpointer=MemorySaver()
        self._compiled = self._graph.compile(checkpointer=checkpointer)