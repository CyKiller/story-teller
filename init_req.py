import os
import pkg_resources


REQUIRED_PACKAGES = [
    "transformers",
    "torch",
    "openai",
    "nltk",
    "milvus",
    "pymilvus",
    "fpdf",
]


def check_packages(packages):
    for package in packages:
        try:
            dist = pkg_resources.get_distribution(package)
            print(f"{dist.key} ({dist.version}) is installed")
        except pkg_resources.DistributionNotFound:
            raise Exception(
                f"{package} is NOT installed. Please install it to proceed.")


def get_openai_api_key():
    try:
        key = os.environ["OPENAI_API_KEY"]
        return key
    except KeyError:
        raise Exception("OPENAI_API_KEY not found in environment variables")


check_packages(REQUIRED_PACKAGES)
OPENAI_API_KEY = get_openai_api_key()
