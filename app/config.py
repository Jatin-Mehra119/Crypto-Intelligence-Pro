import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])