import os
import json
import time
import datetime
from collections import Counter
import uuid
import langid
from Latin_to_Amh_Dict import RBLatAm
import openai
import streamlit as st

import PromptTemplate as pt
from OpenAIHandler import OpenAIHandler
from constants import (
    OPENAI_MODEL,
    OPENAI_API_KEY,
)

openai.api_key = OPENAI_API_KEY

# Set up the page configuration
st.set_page_config(page_title="National ID Agency of Ethiopia's Help Chatbot", page_icon="🤖", layout="wide")

st.info("National ID Agency of Ethiopia")

# Side bar information
st.sidebar.title("National ID Agency of Ethiopia's Help Chatbot")

st.sidebar.markdown("Please use English, and Amharic (with both Latin and Ge'ez alphabet)")

# st.sidebar.markdown(
#     "1. Thumbs up 👍: click when you are satisfied by the answer provided by the chatbot \n 2. Thumbs down 👎: click when you are not satisfied by the answer provided by the chatbot. \n \n \n \n \n \n \n \n"
# )

# the system prompt template
# if st.session_state['language'] == 'English':
#     faq_sys_prompt = pt.amharic_translation_prompt_english
# else:
#     faq_sys_prompt = pt.amharic_translation_prompt_amharic

# caounter for the fallback rate
fallbackrate_counter = 0

default_states = {
    "messages": [],  # history of all exchanged messages with role and content
    "feedback": [],
    "feedback_timestamp": [],  # history of bot responses
    "answers": [],
    "answers_timestamp": [],
    "questions": [],
    "questions_timestamp": [],
    "is_responding": False,
    "model": OPENAI_MODEL,
    "prompt": pt.general_prompt,
    # "language": "Amharic",
    "temperature": 0,
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value


def disable_chat():
    st.session_state.chat_disabled = True


if "chat_disabled" not in st.session_state.keys():
    st.session_state.chat_disabled = False


def get_text():
    """ Get the user input text.
    Returns:
        (str): The text entered by the user
    """
    input_text = st.chat_input(
        placeholder="I am NiDA Bot, ask me anything related to Ethiopian National ID and Fayda...",
        disabled=st.session_state.chat_disabled, on_submit=disable_chat
    )

    return input_text


openAI = OpenAIHandler(
    model_name=st.session_state['model'], temperature=st.session_state["temperature"])

user_input = get_text()

def get_transliteration(string, reverse=1):
    for k, v in RBLatAm.items():
      if not reverse:
            string = string.replace(v, k)
      else:
            string = string.replace(k, v)
    
    return string


def split_into_chunks(text, chunk_size):
    words = text.split()
    chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
    return [' '.join(chunk) for chunk in chunks]


def quick_action_event_handler(event):
    """Handles the event when a quick action button is clicked."""

    st.session_state['feedback'].append(event)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Display chat messages from history on the app UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Get the current date
current_date = str(datetime.date.today())

if user_input:
    st.session_state['questions_timestamp'].append(time.time())
    st.session_state['is_responding'] = True

    conversation_history = [["what is today's date", *st.session_state['questions']], [
        current_date, *st.session_state['answers']]]

    language_code, confidence = langid.classify(user_input)

    if language_code == 'en' or language_code == 'am':
        user_input_transliterated = None
    else:
        user_input_transliterated = get_transliteration(user_input, 1)

    # creating memory for the chatbot (this takes conversation_history and keeps the last 5 question-answer pairs )
    memory = openAI.getMemoryConversation(conversation_history, 20)

    if user_input_transliterated == None or user_input_transliterated == '':
        main_input = user_input
    else:
        main_input = user_input_transliterated

    data = dict(query=main_input, memory=memory,
                template=st.session_state['prompt'])

    # display user message in chat message container
    st.session_state.questions.append(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # display chatbot's message in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        openai_obj = OpenAIHandler(message_placeholder=message_placeholder)
        chatbot_response = openai_obj.queryResponse(**data)

        st.session_state['is_responding'] = False

    st.session_state.answers.append(chatbot_response)
    st.session_state.messages.append(
        {"role": "assistant", "content": chatbot_response})

    st.session_state['answers_timestamp'].append(time.time())

    if "Unknown data" in chatbot_response:
        fallbackrate_counter += 1

    if st.session_state.chat_disabled:
        st.session_state.chat_disabled = False

    st.rerun()

conversation_history = [["what is today's date", *st.session_state['questions']],
                        [current_date, *st.session_state['answers']]]


st.session_state['questions'] = []
st.session_state['answers'] = []
st.session_state.messages = []
st.session_state['model'] = "gpt-4o-mini"
st.session_state["temperature"] = 0.4


# st.sidebar.markdown("Change the language from English to Amharic")

# Switches from English to Amharic
# btn = st.sidebar.button("Amharic Mode")
# if btn:
#     if(st.session_state['prompt'] == pt.amharic_translation_prompt):
#             st.session_state['prompt'] = pt.amharic_translation_prompt
#             st.write(f"The Chatbot is now in Amharic mode")
#     else:
#         st.session_state['prompt'] = pt.amharic_translation_prompt
#         st.write(f"The Chatbot is now in English mode")
    
st.sidebar.markdown("End the session to save the conversation for reference")

# adding a sidebar button to end the session and what happens when the button is clicked
if st.sidebar.button("End Session"):
    st.write(
        f"Your session has ended and your conversation has been saved. Thank you!")
    # counting the number times the user clicked on thumbs up, thumbs down
    element_counts = Counter(st.session_state['feedback'])

    total_interactions = len(
        conversation_history[0]) + len(conversation_history[1])

    if not os.path.exists("conversations"):
        os.makedirs("conversations")

    current_time = time.strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    file_name = f"conversations/conversation_{current_time}_{unique_id}.json"

    data = {
        "total_interactions": total_interactions,
        "time_generated": time.time(),
        "fallback_rate": fallbackrate_counter,
        "user_satisfaction": element_counts,
        "Conversation": conversation_history,
        "question_timestamps": st.session_state['questions_timestamp'],
        "answer_timestamps": st.session_state['answers_timestamp'],
    }

    with open(file_name, "w") as file:
        json.dump(data, file)

    fallbackrate_counter = 0

    # clearning the session state for that session
    for key in st.session_state.keys():
        del st.session_state[key]
