
## Initial Setup

1. Setup openai venv first. 

  ```
  python3 -m venv openai-env
  source openai-env/bin/activate
  pip install --upgrade openai
  ```
  Refer to https://platform.openai.com/docs/quickstart?context=python for further details. 

2. Add the Openai API key and Discord bot keys to .env file
  ```
  echo "OPENAI_API_KEY=your key here" >> .env
  echo "DISCORD_BOT_TOKEN1=your bot token here" >> .env 
  echo "DISCORD_BOT_TOKEN2=your 2nd bot token here" >> .env
  ```

3. Create and configure two discord bots and them to a test server in your discord account 

## Run and test   
1. Open the discord server to which both bots are added on a browser. 
2. Run the bot scripts separately in two terminals
     ```
     python3 assistant_discord1.py
     python3 assistant_discord2.py
     ```
   You may change the instructions and RAG files of each bot directly in the respective python scripts
