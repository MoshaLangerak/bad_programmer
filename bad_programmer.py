import streamlit as st
import time
import os

def get_replicate_api_token():
    os.environ['REPLICATE_API_TOKEN'] = st.secrets['REPLICATE_API_TOKEN']

def stream_chat_message(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.02)

def display_initial_message(streaming=True):
    with st.chat_message("Bad Programmer", avatar="🤖"):
        if streaming:
            st.write_stream(stream_chat_message("Hello! I am a bad programmer. I need help writing good code. Can you help me?"))
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

def display_ui():
    st.title('Meet the bad programmer!')
    st.write("This is a bad programmer. He writes bad code. However, he is trying to improve. Can you help him?")

def get_and_process_prompt():
    if st.session_state.messages[-1]['role'] == "user":
        # Generate a response
        with st.chat_message("Bad Programmer", avatar="🤖"):
            response = "Response"
            st.write_stream(stream_chat_message(response))
        st.session_state.messages.append({"role": "Bad Programmer", "avatar": "🤖", "content": response})
        
    if st.session_state.chat_finished:
        st.button('New problem please!', on_click=restart_chat, key="new_problem")
        st.chat_input(disabled=True)
    elif prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

def restart_chat():
    st.session_state.messages = []
    st.session_state.chat_finished = False
    st.rerun()
    
def main():
    get_replicate_api_token()
    display_ui()

    # Initialize the session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_finished = False

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
        
    get_and_process_prompt()

if __name__ == "__main__":
    main()