"""
Configuration module for the chat agent.

This module handles loading environment variables, configuring API keys,
and setting up the OpenAI client for use throughout the application.
"""

import os
from typing import Optional
import certifi
import httpx

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
        cert_path = r"C:\Users\slehmann\Projects\n8n\cacert.pem"
        transport = httpx.HTTPTransport(
            verify=cert_path,  # Use your specific cert file
            trust_env=True  # This will use environment proxy settings
        )
        client = OpenAI(
            api_key=api_key,
            http_client=httpx.Client(
                transport=transport,
                trust_env=True,  # Use system proxy settings
                verify=cert_path  # Use your specific cert file
            )
        )
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


