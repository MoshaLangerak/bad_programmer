import streamlit as st
import time
import os
from transformers import AutoTokenizer
import replicate

def get_replicate_api_token():
    os.environ['REPLICATE_API_TOKEN'] = st.secrets['REPLICATE_API_TOKEN']

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_finished = False
        st.session_state.temperature = 0.3
        st.session_state.top_p = 0.9

def display_ui():
    st.title('Meet the bad programmer!')
    st.write("""This is a bad programmer. He writes bad code. However, he is trying to improve. 
             It is your job to help him write good code. You will be presented with a piece of 
             code that the bad programmer has written. You need to help him fix it. Let's get started!""")

def display_chat_messages():
    # if there are no messages, display the initial message
    if not st.session_state.messages:
        display_initial_message()

        st.session_state.messages.append({"role": "Bad Programmer", "avatar": "🤖",
                                        "content": "INITIAL_MESSAGE"})
    else:
        # Display the chat messages
        for message in st.session_state.messages:
            if message['content'] == "INITIAL_MESSAGE":
                display_initial_message(streaming=False)
            else:
                with st.chat_message(message['role'], avatar=message.get("avatar", None)):
                    st.write(message['content'])
        
def stream_chat_message(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.02)

def display_initial_message(streaming=True):
    with st.chat_message("Bad Programmer", avatar="🤖"):
        if streaming:
            st.write_stream(stream_chat_message("Hello! I am a bad programmer. I need help writing good code."))
            st.write_stream(stream_chat_message("I am trying to write a function that adds two numbers. Can you help me?"))
        else:
            st.write("Hello! I am a bad programmer. I need help writing good code. Can you help me?")
            st.write("I am trying to write a function that adds two numbers. Can you help me?")

        # Display a piece of that the user can change and help the bad programmer
        code = '''def add_numbers(a, b):
        return a - b
        '''
        st.code(code, language="python")
        
        if streaming:
            st.write_stream(stream_chat_message("Can you help me fix this code?"))
        else:
            st.write("Can you help me fix this code?")

def get_and_process_prompt():
    if st.session_state.messages[-1]['role'] == "user":
        # Generate a response
        with st.chat_message("Bad Programmer", avatar="🤖"):
            generate_response()
            st.write_stream(stream_chat_message(st.session_state.messages[-1]["content"]))

    if len(st.session_state.messages) > 5:
        st.session_state.chat_finished = True
        st.write("You have reached the end of the chat. Do you want to start a new problem?")
        
    if st.session_state.chat_finished:
        st.button('New problem please!', on_click=restart_chat, key="new_problem")
        st.chat_input(disabled=True)
    elif prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

def restart_chat():
    st.session_state.messages = [{"role": "Bad Programmer", "avatar": "🤖",
                                        "content": "INITIAL_MESSAGE"}]
    st.session_state.chat_finished = False

def get_num_tokens(prompt):
    """Get the number of tokens in a given prompt"""
    tokenizer = AutoTokenizer.from_pretrained("huggyllama/llama-7b")
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)

def generate_response():
    prompt = []

    for message in st.session_state.messages:
        if message['role'] == "user":
            prompt.append("<|im_start|>user\n" + message["content"] + "<|im_end|>")
        else:
            prompt.append("<|im_start|>bad_programmer\n" + message["content"] + "<|im_end|>")
    
    prompt.append("<|im_start|>bad_programmer\n")
    prompt_str = "\n".join(prompt)

    num_tokens = get_num_tokens(prompt_str)
    if num_tokens > 1500:
        restart_chat()

    st.session_state.messages.append({"role": "Bad Programmer", "avatar": "🤖", "content": ""})
    for event_index, event in enumerate(replicate.stream("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                #   "prompt_template": r"{prompt}",
                                  "temperature": st.session_state.temperature,
                                  "top_p": st.session_state.top_p,
                                  })):
        
        st.session_state.messages[-1]["content"] += str(event)

def main():
    get_replicate_api_token()
    display_ui()
    init_session_state()
    display_chat_messages()
    get_and_process_prompt()

if __name__ == "__main__":
    main()