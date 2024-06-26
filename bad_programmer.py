import streamlit as st
import time
import os
from transformers import AutoTokenizer
import replicate

from utility_functions import stream_chat_message

def get_replicate_api_token():
    os.environ['REPLICATE_API_TOKEN'] = st.secrets['REPLICATE_API_TOKEN']

def display_ui():
    st.title('Meet the bad programmer!')
    st.write("""This is a bad programmer. He writes bad code. However, he is trying to improve. 
             It is your job to help him write good code. You will be presented with a piece of 
             code that the bad programmer has written. You need to help him fix it. Let's get started!""")

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_finished = False
        st.session_state.temperature = 0.7
        st.session_state.top_p = 0.8
        st.session_state.output = None

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

def display_initial_message(streaming=True):
    with st.chat_message("Bad Programmer", avatar="🤖"):
        if streaming:
            st.write_stream(stream_chat_message("Hello! I am a bad programmer. I need help writing good code."))
            st.write_stream(stream_chat_message(st.session_state.task))
        else:
            st.write("Hello! I am a bad programmer. I need help writing good code. Can you help me?")
            st.write(st.session_state.task)

        # st.code(code, language="python")
        st.code(st.session_state.code, language="python")
        
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
        st.session_state.messages.append({"role": "user", "avatar":"🧑‍💻", "content": prompt})
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

    # add a basic instruction to the prompt
    instruction = """
    You are going to act as "bad programmer", a persona who intentionally writes buggy code for the purpose of teaching and coaching beginner-level programmers. 
    Your task is to generate a Python function that performs a common programming task, introduce an easy-to-fix bug in the function, 
    and present it in a way that encourages the learner to identify and fix the bug. Your responses should encourage the learner to identify and fix the bug themselves. 
    Do not provide the solution directly.
    """

    prompt.append(instruction)

    # add the task and the code to the prompt
    prompt.append("<|im_start|>bad_programmer\n")
    prompt.append(st.session_state.task)
    prompt.append(st.session_state.code)
    prompt.append(st.session_state.bug)
    prompt.append("<|im_end|>")

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

def initial_prompt():
    # perform the initial prompt to get the bad programmer started
    number_of_tries = 0
    
    while st.session_state.output is None:
        print(f"Trying to generate the prompt, attempt number: {number_of_tries}")
        difficulties = ["beginner", "intermediate", "advanced"]
        difficulty = difficulties[0]

        if number_of_tries > 5:
            st.write("There was an error generating the prompt. Please try again.")
            break

        output = replicate.run(
            "snowflake/snowflake-arctic-instruct",
            input={ "prompt": f"""Generate a Python function of around 5 lines that performs a common programming task. 
                   You have to introduce a bug in the code. The bug can be for example, mixing up a + and -, messing up arguments or misspelling a variable. 
                   The bug should not be related to edge cases or not handling certain cases/input values. 
                   A {difficulty}-level programmer should be able to find the bug.
                   Do not include any comments in the code that might hint at or describe the bug.
                   
                   Please return the code with a bug in it in the following way:
                   
                   I am trying to **programming task**, but I have run into a bug can you help me?
                   
                   **Code:**
                   
                   **Bug in the code:**
                   """ },
                )

        try:
            output = "".join(output)
            st.session_state.output = output
            
            output = output.split("**Code:**")

            task = output[0].strip()
            code = output[1].split("**Bug in the code:**")[0].strip()
            bug = output[1].split("**Bug in the code:**")[1].strip()

            # remove ```python and ``` from the code
            code = code.replace("```python", "").replace("```", "").strip()

            st.session_state.task = task
            st.session_state.code = code
            st.session_state.bug = bug

        except IndexError:
            number_of_tries += 1
            continue

def main():
    get_replicate_api_token()
    display_ui()
    init_session_state()
    initial_prompt()
    display_chat_messages()
    get_and_process_prompt()

if __name__ == "__main__":
    main()