"""
Configuration module for the chat agent.

This module handles loading environment variables, configuring API keys,
and setting up the OpenAI client for use throughout the application.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI, APIError

# Load environment variables from .env file
load_dotenv()


def get_openai_api_key() -> str:
    """
    Retrieve the OpenAI API key from environment variables.
    
    Returns:
        str: The OpenAI API key.
        
    Raises:
        ValueError: If the API key is not found in environment variables.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
            "in your .env file or system environment variables."
        )
    
    return api_key


def create_openai_client() -> OpenAI:
    """
    Create and configure an OpenAI client instance.
    
    Returns:
        OpenAI: Configured OpenAI client instance.
    """
    try:
        api_key = get_openai_api_key()
        client = OpenAI(api_key=api_key)
        return client
    except ValueError as e:
        # Re-raise the error with the same message
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(f"Error creating OpenAI client: {str(e)}")


# Create a global client instance for use throughout the application
try:
    openai_client = create_openai_client()
except (ValueError, Exception) as e:
    print(f"Warning: {str(e)}")
    openai_client = None


