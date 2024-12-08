import os

from chatgpt_cli.db.session import get_session
from chatgpt_cli.models import Chat, Message, User
from chatgpt_cli.openai.openai_client import OpenAIClient
from chatgpt_cli.repositories import ChatRepository, MessageRepository, UserRepository


class ChatService:
    def __init__(self, read_file: str = None):
        self.user_repository = UserRepository()
        self.chat_repository = ChatRepository()
        self.message_repository = MessageRepository()
        self.openai_client = OpenAIClient()
        self.read_file_content = (
            self.load_file_content(read_file) if read_file else None
        )

    def load_file_content(self, file_path: str) -> str:
        if not file_path:
            return None
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    async def start(self):
        print("Welcome to the OpenAI Chat Interface!")
        username = input("Enter your username: ").strip()
        async with get_session() as session:
            user = await self.user_repository.get_user_by_username(session, username)
            if not user:
                user = User(username=username)
                await self.user_repository.create_user(session, user)

            while True:
                print("\nOptions:")
                print("1. Start a new chat")
                print("2. Continue a previous chat")
                print("3. Exit")
                choice = input("Select an option: ").strip()
                if choice == "1":
                    model_name = await self.select_model()
                    if model_name:
                        await self.new_chat(user, model_name)
                elif choice == "2":
                    model_name = await self.select_model()
                    if model_name:
                        await self.continue_chat(user, model_name)
                elif choice == "3":
                    print("\nGoodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")

    async def select_model(self):
        models = await self.openai_client.list_models()
        if not models:
            print("No models available.")
            return None
        print("\nSelect a model to chat with:")
        for idx, model in enumerate(models, 1):
            print(f"{idx}. {model.id}")
        choice = input("Enter model number: ").strip()
        try:
            model_index = int(choice) - 1
            if 0 <= model_index < len(models):
                return models[model_index].id
            else:
                print("Invalid selection.")
                return None
        except ValueError:
            print("Please enter a valid number.")
            return None

    async def new_chat(self, user: User, model_name: str):
        async with get_session() as session:
            chat = Chat(user_id=user.id)
            await self.chat_repository.create_chat(session, chat)
            await self.chat_loop(chat, model_name)

    async def continue_chat(self, user: User, model_name: str):
        async with get_session() as session:
            chats = await self.chat_repository.get_chats_by_user(session, user.id)
            if not chats:
                print("\nNo previous chats found.")
                return
            print("\nPrevious chats:")
            for idx, chat in enumerate(chats, 1):
                print(f"{idx}. Chat ID: {chat.id}, Created At: {chat.created_at}")
            choice = input("Enter the chat number to continue: ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(chats):
                    chat = chats[idx]
                    await self.chat_loop(chat, model_name)
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")

    async def chat_loop(self, chat: Chat, model_name: str):
        print(f"\nChatting with model: {model_name}. Type 'exit' to end the chat.\n")
        conversation = [
            {
                "role": "system",
                "content": "You are a helpful customer support assistant. You can use functions when needed.",
            }
        ]

        async with get_session() as session:
            messages = await self.message_repository.get_messages_by_chat(
                session, chat.id
            )
            for message in messages:
                conversation.append(
                    {"role": message.sender, "content": message.content}
                )
                print(f"{message.sender.capitalize()}: {message.content}")

        # If there's file content, add it as a user message at the start
        if self.read_file_content:
            print("Adding file content to chat.")
            conversation.append({"role": "user", "content": self.read_file_content})
            async with get_session() as session:
                message = Message(
                    chat_id=chat.id, sender="user", content=self.read_file_content
                )
                await self.message_repository.create_message(session, message)
            self.read_file_content = None

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == "exit":
                print("Ending the chat.")
                break
            conversation.append({"role": "user", "content": user_input})
            async with get_session() as session:
                message = Message(chat_id=chat.id, sender="user", content=user_input)
                await self.message_repository.create_message(session, message)

            response_text = await self.openai_client.get_response(
                model_name=model_name, messages=conversation
            )
            print(f"Assistant: {response_text}", end="\n\n", flush=True)
            conversation.append({"role": "assistant", "content": response_text})
            async with get_session() as session:
                message = Message(
                    chat_id=chat.id,
                    sender="assistant",
                    content=response_text,
                    model=model_name,
                )
                await self.message_repository.create_message(session, message)
