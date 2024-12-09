from chatgpt_cli.tools.query_simulation import (
    QUERY_SIMULATION_TABLE_TOOL,
    query_simulation_table,
)
from chatgpt_cli.tools.query_users import QUERY_users_TABLE_TOOL, query_users_table

TOOLS = [
    {"type": "function", "function": QUERY_SIMULATION_TABLE_TOOL},
    {"type": "function", "function": QUERY_users_TABLE_TOOL},
]
# A dictionary mapping tool name to the execution function
TOOL_FUNCTIONS = {
    "query_simulation_table": query_simulation_table,
    "query_users_table": query_users_table,
}
