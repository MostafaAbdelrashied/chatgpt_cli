# ChatGPT CLI

## Description
A Python-based CLI tool for interacting with various OpenAI models.

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
poetry run chatgpt_cli # Run the CLI
```

## Features
- Chat with with different OpenAI models
- Store chat history in a PostgreSQL database
- Continue previous conversations using different models
- Scalable and easy to extend with more functionalities

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
