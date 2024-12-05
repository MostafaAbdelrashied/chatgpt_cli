import asyncio

from src.db.setup import init_db
from src.services import ChatService
from src.utils.args_parser import parse_args


def main():
    asyncio.run(run_chat_application())


async def run_chat_application():
    await init_db()
    chat_service = ChatService(parse_args().stream)
    await chat_service.start()


if __name__ == "__main__":
    main()
