import time

def stream_chat_message(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.02)