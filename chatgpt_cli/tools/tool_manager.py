from chatgpt_cli.tools.query_simulation import (
    QUERY_SIMULATION_TABLE_TOOL,
    query_simulation_table,
)

TOOLS = [QUERY_SIMULATION_TABLE_TOOL]
# A dictionary mapping tool name to the execution function
TOOL_FUNCTIONS = {"query_simulation_table": query_simulation_table}
