import asyncio

from chatgpt_cli.db.setup import init_db


def main():
    asyncio.run(init_db())
    print("Database initialized!")


if __name__ == "__main__":
    main()
