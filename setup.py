# setup.py
from setuptools import setup, find_packages

setup(
    name="ltb",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langgraph",
        "langchain",
        "langchain-community",
        "langchain-core",
        "langchain-ollama",
        "fastapi",
        "uvicorn",
        "httpx",
    ],
)
