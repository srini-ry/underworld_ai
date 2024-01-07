from openai import OpenAI
import discord
import os
import asyncio
import json
import time
from dotenv import load_dotenv

load_dotenv() 

def show_json(obj):
    print(json.loads(obj.model_dump_json()))

def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()

# Replace with the actual human moderator and Bot 2 Discord IDs
HUMAN_MODERATOR_ID = '565704601060245505'
BOT_2_DISCORD_ID = '1188573328038953050'

# Initialize OpenAI client
client = OpenAI()

# Upload the file and create the assistant

file = client.files.create(
    file=open("JD.pdf", "rb"),
    purpose="assistants",
)

assistant = client.beta.assistants.create(
    name="Personal Assistant",
    instructions="""You are a bot inside a discord server with one more bot(candidate assistant) 
    and a human moderator.
    Your role is that of a personal assistant to a recruiter. 
    You have access to both JD and internal recruiter notes for the same JD. 
    Ask questions if you notice a candidate profile or 
    Answer questions briefly, only referring to the Job description files you have in access
    Next steps for interested candidates is to apply on the company website with referal code "AI_BOT"
    Keep all responses within 3 lines. 
    Stop the conversation and post "ALL DONE", once you have an alignment in the conversation.
    If the other bot says "ALL DONE" first, don't respond any more until you see a new question 

    """,
    model="gpt-4-1106-preview",
    tools=[{"type": "retrieval"}],
    file_ids=[file.id],
)

ASSISTANT_ID = assistant.id  # Assistant ID for Bot 2
print(f"Assistant ID2: {ASSISTANT_ID}")

# Assistant Interaction Functions
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

#def get_response(thread):
#    messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
#    return [message.content[0].text.value for message in messages.data]

def get_response(thread):
    messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    return [(message.id, message.content[0].text.value) for message in messages.data]

"""
# Discord Bot Class for Assistant 1
class DiscordBot2(discord.Client):
    def __init__(self, *args, **kwargs):
        # Define the intents
        intents = discord.Intents.default()
        intents.messages = True  # Enable the bot to receive messages
        intents.message_content = True  # Enable the bot to read message content

        # Initialize the superclass with the intents
        super().__init__(*args, **kwargs, intents=intents)
        
        self.assistant_threads = {}  # Threads for the assistant

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        # Don't respond to messages from the bot itself
        if message.author == self.user:
            return
        
        print(f'Here is msg received:{message.content}')

        # Respond only to the human moderator if explicitly called
        #if message.author.id == HUMAN_MODERATOR_ID and not message.content.startswith('!assistant1'):
        #    return

        # Respond to messages from Bot 2
        #if message.author.id == BOT_2_DISCORD_ID or message.author.id == HUMAN_MODERATOR_ID:
        user_id = message.author.id
        if user_id not in self.assistant_threads:
            thread = client.beta.threads.create()
            self.assistant_threads[user_id] = thread
        else:
            thread = self.assistant_threads[user_id]

        # Processing message through OpenAI Assistant
        run = submit_message(ASSISTANT_ID, thread, message.content)
        run = await self.loop.run_in_executor(None, wait_on_run, run, thread)
        response_messages = get_response(thread)


        # Send the assistant's response to the Discord channel
        if response_messages:
            last_response = response_messages[-1]  # Get the last message text
            print(f"Assistant's Response: {last_response}")
            await message.channel.send(last_response)
"""

class DiscordBot2(discord.Client):
    def __init__(self, *args, **kwargs):

        # Define the intents
        intents = discord.Intents.default()
        intents.messages = True  # Enable the bot to receive messages
        intents.message_content = True  # Enable the bot to read message content

        # Initialize the superclass with the intents
        super().__init__(*args, **kwargs, intents=intents)
        self.assistant_threads = {}  # Threads for the assistant
        self.last_assistant_message_id = {}  # Dictionary to track the last message ID sent by the assistant

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):

        if message.author == self.user:
            return
        print(f'Here is msg received:{message.content}')

        user_id = message.author.id

        if user_id not in self.assistant_threads:
            thread = client.beta.threads.create()
            self.assistant_threads[user_id] = thread
        else:
            thread = self.assistant_threads[user_id]

        # Processing message through OpenAI Assistant
        run = submit_message(ASSISTANT_ID, thread, message.content)
        run = await self.loop.run_in_executor(None, wait_on_run, run, thread)
        response_messages = get_response(thread)

        # Check if there's a new response from the assistant
        if response_messages:
            last_response_id, last_response_text = response_messages[-1]
            if user_id not in self.last_assistant_message_id or self.last_assistant_message_id[user_id] != last_response_id:
                # Update the last message ID sent and send the response to the Discord channel
                self.last_assistant_message_id[user_id] = last_response_id
                print(f"Assistant's Response: {last_response_text}")
                await message.channel.send(last_response_text)


# Load bot token from environment variable
bot_token_2 = os.getenv('DISCORD_BOT_TOKEN2')

# Run the bot
bot2 = DiscordBot2()
bot2.run(bot_token_2)