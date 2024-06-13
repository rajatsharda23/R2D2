import streamlit as st
from dotenv import load_dotenv
import os
import asyncio
from openai import OpenAI
from nemoguardrails import LLMRails, RailsConfig

load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"
openapi_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key = openapi_api_key)

config = RailsConfig.from_path("./config")
rails = LLMRails(config)

rails = LLMRails(config=config)
prompt_list = []

# To append the new prompt to last to retain history
async def get_bot_response(message: str) -> str:
    prompt = message
    bot_response: str = asyncio.create_task(get_api_response(prompt))
    update_bot_response  = await bot_response


    if not update_bot_response:
        update_bot_response = 'Something went wrong...'

    return update_bot_response   

def create_prompt(message: str, pl: list[str]) -> str:
    p_message : str = f'\n{message}'
    prompt: str = ''.join(pl)
    return prompt

# API call to get answer from gpt-3.5
async def get_api_response(prompt: str) -> str | None:
    text: str | None = None

    prompt_list = []
    for key in st.session_state['messages']:
        prompt_list.append(key['content'])

    prompt = create_prompt(prompt, prompt_list)

    try:
        response = await rails.generate_async(
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        text = response["content"]
        # print('---------------------------- \n')
        # print(prompt)
        # print('(1) \n')
        # print(response)
        # print('(2)\n')
        # info = rails.explain()
        # info.print_llm_calls_summary()
        # print('(3) \n')
        # print(info.colang_history)
        # print('(4) \n')
        # print(info.llm_calls[1].completion)
        # print('(5) \n')
        # print(text)

    except Exception as e:
        print('ERROR: ', e)
    
    return text 

async def resp(prompt: str):
     with st.chat_message(name="R2D2", avatar='assets/r2d2.png'):
        message_placeholder = st.empty()
        full_response = ""

        response_from_gpt: str = asyncio.create_task(get_bot_response(prompt))
        response = await response_from_gpt
        
        full_response += response
        
        # Display bot message
        message_placeholder.markdown(full_response + "| ")
        message_placeholder.markdown(full_response)
        
        #Add message to AI history
        st.session_state.messages.append({"role": "R2D2", "content": response})


#Streamlit App
st.title("R2/D2 bot")
st.write("Ran out of OpenAI credits :( ..... will update this soon. until then, check out -> https://catchyaa.streamlit.app/ OR my portfolio -> https://rajat-portfolio23.netlify.app/")

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
    
    
    #Display bot response
    
    asyncio.run(resp(prompt))
