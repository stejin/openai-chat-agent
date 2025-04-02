import requests
import os
from dotenv import load_dotenv

def test_openai_connection():
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    # First, try with normal verification
    print("Testing with normal verification...")
    try:
        response = requests.get('https://api.openai.com/v1/models', 
                              headers={'Authorization': f'Bearer {api_key}'})
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:100]}")
    except Exception as e:
        print(f"Error with normal verification: {str(e)}")
    
    # Then try with verification disabled (FOR TESTING ONLY)
    print("\nTesting with verification disabled (FOR TESTING ONLY)...")
    try:
        response = requests.get('https://api.openai.com/v1/models', 
                              headers={'Authorization': f'Bearer {api_key}'},
                              verify=False)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:100]}")
    except Exception as e:
        print(f"Error with verification disabled: {str(e)}")

if __name__ == "__main__":
    test_openai_connection()

