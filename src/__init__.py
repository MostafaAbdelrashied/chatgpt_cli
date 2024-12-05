from loguru import logger

from src.utils.args_parser import parse_args
from src.utils.env_vars import check_environment_variables
from src.utils.logging import setup_logging

args = parse_args()
setup_logging(args.log_level)

REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "OPENAI_API_KEY",
]

env_results = check_environment_variables(
    *REQUIRED_ENV_VARS,
)
if not env_results.is_valid:
    logger.error(env_results.message)
    exit(1)
