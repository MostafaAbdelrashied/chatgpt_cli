import asyncio

from chatgpt_cli.db.setup import init_db
from chatgpt_cli.services import ChatService
from chatgpt_cli.utils.args_parser import parse_args


def main():
    asyncio.run(run_chat_application())


async def run_chat_application():
    await init_db()
    print("Database initialized!")
    chat_service = ChatService(parse_args().stream)
    await chat_service.start()


if __name__ == "__main__":
    main()
