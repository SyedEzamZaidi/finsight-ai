import anthropic
from dotenv import load_dotenv
import os

# Load the .env file so Python can read your API key
load_dotenv()

# Create the Anthropic client using your API key
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Send a simple message to Claude
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Say exactly this: FinSight AI connection successful."
        }
    ]
)

# Print Claude's response
print(message.content[0].text)