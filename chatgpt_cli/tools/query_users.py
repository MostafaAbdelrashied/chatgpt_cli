from sqlalchemy import text

from chatgpt_cli.db.session import get_session


async def query_users_table(query: str):
    async with get_session() as session:
        result = await session.execute(text(query))
        rows = result.fetchall()
        return {"query": query, "result": rows}


QUERY_users_TABLE_TOOL = {
    "name": "query_users_table",
    "description": "Query the database for information about users, messages, chats data. The table exists under schema 'chat' and table names 'chats', 'messages', 'users'",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to run in the Postgres database",
            }
        },
        "required": ["query"],
    },
}
