import anthropic
import openai
import streamlit as st
import json
import os
import base64
import requests
from dotenv import load_dotenv

st.set_page_config(layout="wide")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def determine_media_type(image_path):
    # Determine image media type based on file extension
    file_extension = os.path.splitext(image_path)[1].lower()
    media_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp'
    }
    return media_type_map.get(file_extension, 'image/jpeg')

def anthropic_analyze_image(image_path, api_key, prompt):

    # Determine image media type
    media_type = determine_media_type(image_path)

    # Encode the image
    base64_image = encode_image(image_path)

    # Anthropic API endpoint
    url = "https://api.anthropic.com/v1/messages"

    # Request payload
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }

    # Headers
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
        "Anthropic-Version": "2023-06-01"
    }

    try:
        # Send the request
        response = requests.post(url, json=payload, headers=headers)
        
        # Check for successful response
        if response.status_code != 200:
            print("Response Content:", response.text)
            response.raise_for_status()
        
        # Parse the response
        response_data = response.json()
        
        # Extract and return Claude's description
        return response_data['content'][0]['text']
    
    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return f"An error occurred: {e}"
    except (KeyError, IndexError) as e:
        print(f"Parsing Error: {e}")
        return f"Error parsing API response: {e}"
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return f"An unexpected error occurred: {e}"

def anthropic_verify_api_key(api_key):
    # Correct Anthropics endpoint for testing
    endpoint = "https://api.anthropic.com/v1/messages"

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
        "Anthropic-Version": "2023-06-01"
    }

    # Minimal valid payload for the /complete endpoint
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Verifying API key. DO NOT RESPOND."
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        
        if response.status_code == 200:
            return True
        else:
            print(f"Invalid API Key: {response.status_code}, {response.json()}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error while validating API key: {e}")
        return False

def get_environment_attributes()->dict:
    load_dotenv('.env')
    return {
    "app_name": os.getenv('APP_NAME'),
    "app_version": os.getenv('APP_VERSION'),
    "app_description": os.getenv('APP_DESCRIPTION'),
    "app_author": os.getenv('APP_AUTHOR'),
    }

def setup_session_variables():
    if "image_selected" not in st.session_state:
        st.session_state.image_selected = False

    if "model_selected" not in st.session_state:
        st.session_state.model_selected = False

    if "return_values_selected" not in st.session_state:
        st.session_state.return_values_selected = False

def update_return_values_selected():
    st.session_state.return_values_selected = any([
        st.session_state.description,
        st.session_state.color_palette,
        st.session_state.aspect_ratio,
        st.session_state.subjects_detected
    ]) 

    st.session_state.model_selected = any([
        st.session_state.anthropic_model
    ])

    st.session_state.image_selected = any([
        st.session_state.image_uploaded
    ])

    if st.session_state.image_uploaded == None:
        st.session_state.result = None

def spacing(number_of_spaces:int):
    for _ in range(number_of_spaces):
        st.write("")

def ai_prompt():
    prompt = "Return the following key: value pairs in the response JSON:\n\n"

    if st.session_state.description:
        prompt += "\"description\": \"A detailed description of the image.\"\n"
    if st.session_state.color_palette:
        prompt += "\"color-palette\": \"A list of colors present in the image.\"\n"
    if st.session_state.aspect_ratio:
        prompt += "\"aspect-ratio\": \"The aspect ratio of the image.\"\n"
    if st.session_state.subjects_detected:
        prompt += "\"subjects-detected\": \"A list of subjects detected in the image.\"\n"

    prompt += "\nDo not return anything else."

    return prompt

def get_api_keys():
    if os.getenv('STREAMLIT_CLOUD') == 'false':
        if not os.path.exists('.anthropic_key'):
            with open('.anthropic_key', 'w') as f:
                if os.environ.get('ANTHROPIC_API_KEY'):
                    f.write(os.environ.get('ANTHROPIC_API_KEY'))
                else:
                    f.write('Enter API Key')
        with open('.anthropic_key', 'r') as f:
            st.session_state.anthropic_api_key = f.read().strip()


# Get environment variables.
env_vars = get_environment_attributes()
setup_session_variables()
get_api_keys()

st.title(env_vars["app_name"])
st.subheader(env_vars["app_description"])
st.caption(f"Version: {env_vars['app_version']} | {env_vars['app_author']}")

spacing(2)

with st.container(border=1, height=100):
    col1,col2,col3,col4= st.columns(4)
    with col1:
        if st.session_state.image_selected:
            st.write("✅ Image Uploaded")
        else:
            st.write("❌ Image Uploaded")
    with col2:
        if st.session_state.model_selected:
            st.write("✅ Model Selected")
        else:
            st.write("❌ Model Selected")
    with col3:
        if st.session_state.return_values_selected:
            st.write("✅ Return Values Selected")
        else:
            st.write("❌ Return Values Selected")
    with col4:
        if all ([st.session_state.return_values_selected, st.session_state.model_selected, st.session_state.image_selected]):
            st.write("✅ Ready to Analyze")
        else:
            st.write("❌ Ready to Analyze")

    progress=int(st.session_state.return_values_selected)+int(st.session_state.model_selected)+int(st.session_state.image_selected,)
    st.progress(progress/3, text=None)

spacing(2)


col1, col2 = st.columns([2.75,1.25], gap="medium")

with col1:

    # Upload Image
    st.subheader("Upload Image")

    with st.container(border=1):
        # File upload (you may replace this for simplicity)
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "gif", "bmp", "webp"],on_change=update_return_values_selected, key="image_uploaded")

        # Make sure user first uploads an image
        if uploaded_file != None:
            
            # Set the upload directory
            upload_dir = "uploads/"
            
            # Check if the upload directory exists, if not, create it
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Save the uploaded file temporarily                
            temp_image_path = os.path.join(upload_dir, uploaded_file.name)
            with open(temp_image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            uploaded_file = temp_image_path

            if "display_image" not in st.session_state:
                st.session_state.display_image = False

            def toggle_show_image_button():
                st.session_state.display_image = not st.session_state.display_image
            
            st.toggle(
                "Preview Image",
                value=st.session_state.display_image,
                on_change=toggle_show_image_button
            )

    spacing(1)

    if uploaded_file != None and st.session_state.display_image:
        st.subheader("Preview Image")
        with st.container(border=1):
            st.image(uploaded_file, use_container_width=True)

    if all ([st.session_state.return_values_selected, st.session_state.model_selected, st.session_state.image_selected]):
        st.subheader("Image Analysis")
        with st.container(border=1):

            if "result" in st.session_state and st.session_state.result != None:
                st.code(st.session_state.result, language="json", wrap_lines=True)

            st.write("")

with col2:

    # AI Models
    st.subheader("Select AI Models")

    with st.container(border=1):
        column1, column2, colum3 = st.columns([.3,.2,.5])
        with column1:
            st.write("Anthropic")
        
        with column2:
            anthropic_model=st.toggle("Anthropic", False, key="anthropic_model", label_visibility="collapsed", on_change=update_return_values_selected)
        
        with colum3:
            def write_anthropic_api_key():
                if os.getenv('STREAMLIT_CLOUD') == 'false':
                    with open('.anthropic_key', 'w') as f:
                        f.write(f'{st.session_state.anthropic_api_key}\n')

            if anthropic_model:
                with st.popover("API Key", use_container_width=True):
                    new_api_key = st.text_input("API Key", type="password", on_change=write_anthropic_api_key, key="anthropic_api_key")
                    if not new_api_key:
                        st.warning("API Key can't be empty. Please enter a valid API Key.")


    spacing(1)

    # Return values
    st.subheader("Select Return Values")

    with st.container(border=1):
        column1, column2 = st.columns(2)
        with column1:
            st.write("Description")
            st.write("Color Palette")
            st.write("Aspect Ratio")
            st.write("Subjects Detected")

        with column2:  

            description=st.checkbox("Description", False, key="description", label_visibility="collapsed",on_change=update_return_values_selected)
            color_palette=st.checkbox("Color Palette", False, key="color_palette", label_visibility="collapsed",on_change=update_return_values_selected)
            aspect_ratio=st.checkbox("Aspect Ratio", False, key="aspect_ratio", label_visibility="collapsed",on_change=update_return_values_selected)
            subjects_detected=st.checkbox("Subjects Detected", False, key="subjects_detected", label_visibility="collapsed",on_change=update_return_values_selected)

    spacing(2)

    if all ([st.session_state.return_values_selected, st.session_state.model_selected, st.session_state.image_selected]):
        if st.button("Analyze Image", key="analyze_image_button", use_container_width=True, type="primary"):
            with st.spinner("Running..."):
                if not anthropic_verify_api_key(st.session_state.anthropic_api_key):
                    st.error("Invalid Anthropic API key.")
                else:
                    st.session_state.result = anthropic_analyze_image(uploaded_file, st.session_state.anthropic_api_key, ai_prompt())
                    st.rerun()