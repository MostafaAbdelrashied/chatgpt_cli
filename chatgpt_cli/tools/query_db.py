from sqlalchemy import text

from chatgpt_cli.db.session import get_session


async def query_db(query: str):
    async with get_session() as session:
        result = await session.execute(text(query))
        rows = result.fetchall()
        return {"query": query, "result": rows}


QUERY_DB_TOOL = {
    "name": "query_db",
    "description": "Query the database for information about simulation data. The table exists under schema 'optimization' and table name 'simulation'",
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
