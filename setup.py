from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f.readlines() if line.strip()]

setup(
    name="openai-chat-agent",
    version="0.1.0",
    description="A Python package for interacting with OpenAI's chat models",
    author="OpenAI Chat Agent",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

