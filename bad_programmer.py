import streamlit as st
import time

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

def main():
    st.title("Meet the bad programmer!")
    st.write("This is a bad programmer. He writes bad code. However, he is trying to improve. Can you help him?")

    # Initialize the chatbot
    if "messages" not in st.session_state:
        st.session_state.messages = []

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
        
    if prompt := st.chat_input("Type your message here..."):
        with st.chat_message("user"):
            st.write(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})


if __name__ == "__main__":
    main()