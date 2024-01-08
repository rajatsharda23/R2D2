import streamlit as st
from dotenv import load_dotenv
import os
import asyncio
from openai import OpenAI
from nemoguardrails import LLMRails, RailsConfig

load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"
openapi_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key = openapi_api_key )

config = RailsConfig.from_path("./config")
rails = LLMRails(config)

rails = LLMRails(config=config)

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
        info = rails.explain()
        info.print_llm_calls_summary()
        print(info.colang_history)
        print(info.llm_calls[1].completion)

    except Exception as e:
        print('ERROR: ', e)
    
    return text 

async def resp(prompt: str, pl: list[str]):
    response_from_gpt: str = asyncio.create_task(get_bot_response(prompt, pl))
    response = await response_from_gpt
    
    # Display bot message
    with st.chat_message("assistant"):
        st.markdown(response)
        st.markdown(pl)
    #Add message to AI history
    st.session_state.messages.append({"role":"assistant", "content": response})

#Streamlit App
st.title("R2/D2 bot")

#Initialse chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#Display chat messages from history on app 
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#React to user input
if prompt:= st.chat_input("Start writing here..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    #Add message to user history
    st.session_state.messages.append({"role":"user", "content": prompt})
    prompt_list = []
    asyncio.run(resp(prompt, prompt_list))
    # response_from_gpt: str = asyncio.create_task(get_bot_response(prompt, prompt_list))
