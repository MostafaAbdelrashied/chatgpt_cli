from chatgpt_cli.tools.query_db import QUERY_DB_TOOL, query_db

TOOLS = [QUERY_DB_TOOL]
# A dictionary mapping tool name to the execution function
TOOL_FUNCTIONS = {
    "query_db": query_db,
}
