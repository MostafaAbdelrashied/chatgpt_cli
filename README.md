# ChatGPT CLI

## Description
A Python-based CLI tool for interacting with various OpenAI models using the OpenAI API. The tool allows you to chat with different models, store chat history in a PostgreSQL database, and continue previous conversations using different models.

## Installation and Usage
1. Clone the repository
2. Install dependencies
```bash
poetry install
```
3. Create a `.env` file in the root directory and add the following environment variables:
```bash
OPENAI_API_KEY=
DATABASE_URL=
```
4. Run the CLI
```bash
poetry run chatgpt_cli # Run the CLI. Use --no-stream or --stream to disable or enable streaming mode
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
