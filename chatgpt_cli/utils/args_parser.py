import argparse


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Project description")

    parser.add_argument(
        "--stream",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Stream the response from the model",
    )
    args, _ = parser.parse_known_args()

    return args
