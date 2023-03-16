# 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

import openai
import streamlit as st
from streamlit_chat import message
from audio_recorder_streamlit import audio_recorder
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from gtts import gTTS
from io import BytesIO

openai.api_key=st.secrets['api_secret']

st.markdown("<h2 style='text-align: center;'>Universal Chatbot </h2>", unsafe_allow_html=True)

with st.columns(3)[1]:
     st.image("download.jpeg")
#st.markdown("![Alt Text](https://images.app.goo.gl/d6XYMRXebQNLqxSi7)")

stt_button = Button(label="Speak",button_type="success",width=690,height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=60,
    debounce_time=0)

def generate_response(prompt):
    completions=openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,  #randomness of answer
    )
    message=completions.choices[0].text
    return message 

#storing chat
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

user_input="Hello, how are you?"
if result:
    if "GET_TEXT" in result:
        user_input=result.get("GET_TEXT")
        st.text_input("You: ",user_input, key="input")

if user_input:
    output=generate_response(user_input)
    #store the output
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

text = st.text_input("Answer:",output)
sound_file = BytesIO()
tts = gTTS(output,lang='en',slow=False)
tts.write_to_fp(sound_file)
st.audio(sound_file)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))