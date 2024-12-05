import streamlit as st
from io import StringIO
from openai import OpenAI
from pymatgen.core.structure import Structure
import os

# Show title and description.
st.title("💬 Chatbot for QE input")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-4o model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

st.write(
    "To generate input file, provide structure file."
    "The Chatbot will generate an input file for QE single point scf calculations. And pseudo potential files from SSSP PBEsol efficiency library."
)

# read OpenAI key
openai_api_key = st.text_input("OpenAI API Key", type="password")
# upload structure file into buffer
structure_file = st.file_uploader("Upload the structure file", type=("cif"))

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
if not structure_file:
    st.info("Please add your structure file to continue")
if openai_api_key and structure_file:
    # create a local copy of structure file in the container
    save_directory = "./temp"
        ## Do we need to save files to the local SQL database?
        ## Or we need to delete temp folder after download? 
        ## What if user wants to press the download button again?
        ## What happens if several users accessing app simultaniously?
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    file_name = structure_file.name
    file_path = os.path.join(save_directory, file_name)
    
    with open(file_path, "wb") as f:
        f.write(structure_file.getbuffer())

    structure = Structure.from_file(file_path)
    


    st.write(structure.formula)
    # stringio = StringIO(structure_file.getvalue())
    # st.write(stringio)
    
    st.download_button(
        label="Download the files",
        data=open(file_path, "rb").read(),
        file_name=file_name,
        mime="application/octet-stream"
    )
    
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)
    # structure=Structure.from_file(structure_file)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
