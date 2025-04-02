#!/usr/bin/env python3
"""
Chat Agent Module

This module implements a ChatAgent class for handling conversations with OpenAI's API.
It provides methods for sending messages and handling responses with error handling
and rate limiting functionality.
"""

import sys
import json
import argparse
from typing import List, Dict, Any, Optional

from openai.types.chat import ChatCompletionMessage
from tenacity import retry, stop_after_attempt, wait_exponential

# Import our custom modules
from config import create_openai_client
from utils import setup_logger, APIErrorHandler, safe_execute

# Set up logging
logger = setup_logger(__name__)

class ChatAgent:
    """
    A class to handle conversations with OpenAI's API.
    
    Attributes:
        client: OpenAI client from our config
        model: The model to use for chat completions
        conversation_history: List of message dictionaries representing the conversation
        system_prompt: The system prompt to use for the conversation
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo", system_prompt: Optional[str] = None):
        """
        Initialize the ChatAgent with a model and optional system prompt.
        
        Args:
            model: The OpenAI model to use for chat completions
            system_prompt: Optional system prompt to set the behavior of the assistant
        """
        self.client = create_openai_client()
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        
        # Set up system prompt if provided
        if system_prompt:
            self.set_system_prompt(system_prompt)
        else:
            # Default system prompt
            self.set_system_prompt("You are a helpful AI assistant.")
    
    def set_system_prompt(self, system_prompt: str) -> None:
        """
        Set or update the system prompt for the conversation.
        
        Args:
            system_prompt: The system prompt text
        """
        # Check if there's already a system message
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            self.conversation_history[0]["content"] = system_prompt
        else:
            # Insert system message at the beginning
            self.conversation_history.insert(0, {"role": "system", "content": system_prompt})
        
        logger.info(f"System prompt set: {system_prompt[:50]}...")
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: The role of the message sender (user, assistant, system)
            content: The content of the message
        """
        if role not in ["user", "assistant", "system"]:
            raise ValueError(f"Invalid role: {role}. Must be 'user', 'assistant', or 'system'")
        
        # If it's a system message, use set_system_prompt instead
        if role == "system":
            self.set_system_prompt(content)
            return
            
        self.conversation_history.append({"role": role, "content": content})
        logger.debug(f"Added {role} message: {content[:50]}...")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def send_message(self, message: str) -> str:
        """
        Send a message to the OpenAI API and get a response.
        
        Args:
            message: The message content to send
            
        Returns:
            The assistant's response
            
        Raises:
            Exception: If there's an issue with the API call after retries
        """
        try:
            # Add the user message to the conversation
            self.add_message("user", message)
            
            # Send the conversation to the API
            logger.info(f"Sending message to {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": m["role"], "content": m["content"]} 
                          for m in self.conversation_history],
                temperature=0.7,
            )
            
            # Extract the assistant's message
            assistant_message = response.choices[0].message.content
            
            # Add the assistant's response to the conversation
            self.add_message("assistant", assistant_message)
            
            return assistant_message
            
        except Exception as e:
            # Handle API errors (this will be logged by the handler)
            error_info = APIErrorHandler.handle_error(e)
            logger.error(f"Error sending message: {error_info['message']}")
            raise
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            A list of message dictionaries
        """
        return self.conversation_history
    
    def clear_conversation(self, keep_system_prompt: bool = True) -> None:
        """
        Clear the conversation history.
        
        Args:
            keep_system_prompt: Whether to keep the system prompt
        """
        if keep_system_prompt and self.conversation_history and self.conversation_history[0]["role"] == "system":
            system_prompt = self.conversation_history[0]["content"]
            self.conversation_history = [{"role": "system", "content": system_prompt}]
        else:
            self.conversation_history = []
        
        logger.info("Conversation history cleared")
    
    def save_conversation(self, filename: str) -> None:
        """
        Save the conversation history to a JSON file.
        
        Args:
            filename: The filename to save to
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            logger.info(f"Conversation saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
    
    def load_conversation(self, filename: str) -> None:
        """
        Load a conversation history from a JSON file.
        
        Args:
            filename: The filename to load from
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)
            logger.info(f"Conversation loaded from {filename}")
        except Exception as e:
            logger.error(f"Error loading conversation: {str(e)}")


def main():
    """
    Main function to run the chat agent from the command line.
    
    Usage:
        python -m main --model gpt-3.5-turbo --system "You are a helpful assistant."
    """
    parser = argparse.ArgumentParser(description='Chat with OpenAI API')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo', 
                        help='OpenAI model to use')
    parser.add_argument('--system', type=str, 
                        help='System prompt to set assistant behavior')
    args = parser.parse_args()
    
    try:
        # Create the chat agent
        agent = ChatAgent(model=args.model, system_prompt=args.system)
        
        print(f"Chat initialized with model: {args.model}")
        print("Type 'exit', 'quit', or press Ctrl+C to end the conversation.")
        print("Type 'save <filename>' to save the conversation.")
        print("Type 'load <filename>' to load a conversation.")
        print("Type 'clear' to clear the conversation history.")
        print("Type 'help' to see these commands again.")
        print('-' * 50)
        
        # Main chat loop
        while True:
            try:
                user_input = input("> ")
                
                # Handle commands
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    print("Commands:")
                    print("  exit, quit - End the conversation")
                    print("  save <filename> - Save the conversation")
                    print("  load <filename> - Load a conversation")
                    print("  clear - Clear the conversation history")
                    print("  help - Show this help message")
                    continue
                elif user_input.lower().startswith('save '):
                    filename = user_input[5:].strip()
                    agent.save_conversation(filename)
                    print(f"Conversation saved to {filename}")
                    continue
                elif user_input.lower().startswith('load '):
                    filename = user_input[5:].strip()
                    agent.load_conversation(filename)
                    print(f"Conversation loaded from {filename}")
                    continue
                elif user_input.lower() == 'clear':
                    agent.clear_conversation()
                    print("Conversation history cleared")
                    continue
                
                # Get response from the agent
                print("Thinking...")
                response = agent.send_message(user_input)
                print("\nAssistant:")
                print(response)
                print('-' * 50)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                logger.exception("Error in main chat loop")
    
    except Exception as e:
        print(f"Error initializing chat agent: {str(e)}")
        logger.exception("Error initializing chat agent")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


