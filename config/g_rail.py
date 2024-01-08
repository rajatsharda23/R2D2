from dotenv import load_dotenv
import os
import asyncio
from openai import OpenAI
from nemoguardrails import LLMRails, RailsConfig
from langchain.base_language import BaseLanguageModel

load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"
openapi_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key = openapi_api_key )

config = RailsConfig.from_path("./config")
rails = LLMRails(config)

rails = LLMRails(config=config)

# API call to get answer from gpt-3.5
async def get_api_response(prompt: str) -> str | None:
    text: str | None = None

    try:
        response = await rails.generate_async(
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        text = response["content"]
        # info = rails.explain()
        # info.print_llm_calls_summary()
        # print(info.colang_history)
        # print(info.llm_calls[1].completion)

    except Exception as e:
        print('ERROR: ', e)
    
    return text 
   
# To append the new prompt to last to retain history
def update_list(message: str, pl: list[str]):
    pl.append(message)
def create_prompt(message: str, pl: list[str]) -> str:
    p_message : str = f'\n{message}'
    update_list(p_message, pl)
    prompt: str = ''.join(pl)
    return prompt

async def get_bot_response(message: str, pl: list[str]) -> str:
    prompt: str = create_prompt(message,pl)
    bot_response: str = asyncio.create_task(get_api_response(prompt))
    update_bot_response  = await bot_response


    if update_bot_response:
        update_list(update_bot_response,pl)
    
    else:   #Incase of error in API call to gpt
        update_bot_response = 'Something went wrong...'

    return update_bot_response    

async def main():
    prompt_list = ['']  #History of prompts for comtext
    
    while True:
        user_input: str = input('You: ')
        if user_input.lower() == 'mischeif managed':
            break
        response: str = asyncio.create_task(get_bot_response(user_input, prompt_list))
        value = await response
        print(f'Bot:  {value}')

        if user_input.lower() in ['quit', 'exit', 'bye']:
            break

        if response=='Something went wrong...' or response=='I cannot answer such questions, please read the guidlines...':
            break

if __name__ == '__main__':
    asyncio.run(main())