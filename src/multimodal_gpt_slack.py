from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI, AzureOpenAI
import requests
import os
import json
import re
from openai_utils import *

SLACK_SOCKET_TOKEN = os.getenv("SLACK_SOCKET_TOKEN")
SLACK_BOT_USER_TOKEN = os.getenv("SLACK_BOT_USER_TOKEN")

OPENAI_KEY = os.getenv("OPENAI_KEY")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION")

WAITING_MESSAGE = os.getenv("WAITING_MESSAGE")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
TEMP_FILES_FOLDER = os.getenv("TEMP_FILES_FOLDER")

IMAGE_GENERATION_ENABLED = os.getenv('IMAGE_GENERATION_ENABLED', 'False').lower() in ('true', '1')
TEXT_TO_SPEECH_ENABLED = os.getenv('TEXT_TO_SPEECH_ENABLED', 'False').lower() in ('true', '1')
SPEECH_TO_TEXT_ENABLED = os.getenv('SPEECH_TO_TEXT_ENABLED', 'False').lower() in ('true', '1')

GPT_MODEL = os.getenv("GPT_MODEL")
TTS_MODEL = os.getenv("TTS_MODEL")
TTS_VOICE = os.getenv("TTS_VOICE")
IMAGE_MODEL = os.getenv("IMAGE_MODEL")
STT_MODEL = os.getenv("STT_MODEL")

app = App(token = SLACK_BOT_USER_TOKEN)
if OPENAI_KEY:
    print("Running with OpenAI")
    ai_client = OpenAI(api_key=OPENAI_KEY)
elif AZURE_OPENAI_KEY:
    print("Running with Azure OpenAI")
    ai_client = AzureOpenAI(api_key = AZURE_OPENAI_KEY, api_version=AZURE_OPENAI_VERSION, azure_endpoint=AZURE_OPENAI_ENDPOINT)
else:
    print("[ERROR] Missing both OPENAI_KEY and AZURE_OPENAI_KEY")
    exit(1)

tools = []
if IMAGE_GENERATION_ENABLED:
    tools.append({
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": "Generate image basing on description",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description of the image, e.g. a house under an apple tree",
                    },
                    "size": {
                        "type": "string",
                        "enum": ["square", "portrait", "landscape"],
                        "description": "Size of the generated image. Use square if no information is provided",
                    }
                },
                "required": ["description"],
            },
        },
    })
    print('IMAGE_GENERATION: Enabled')
else:
    print('IMAGE_GENERATION: Disabled')

if TEXT_TO_SPEECH_ENABLED:
    tools.append({
        "type": "function",
        "function": {
            "name": "generate_tts",
            "description": "Generate or convert from text to speech",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_text": {
                        "type": "string",
                        "description": "Text to be converted to speech",
                    }
                },
                "required": ["input_text"],
            },
        },
    })
    print('TEXT_TO_SPEECH: Enabled')
else:
    print('TEXT_TO_SPEECH: Disabled')

if SPEECH_TO_TEXT_ENABLED:
    tools.append({
        "type": "function",
        "function": {
            "name": "generate_stt",
            "description": "Transcript or convert from speech to text",
            "parameters": {
                "type": "object",
                "properties": {
                }
            },
        },
    })
    print('SPEECH_TO_TEXT: Enabled')
else:
    print('SPEECH_TO_TEXT: Disabled')

@app.message()
def im_message(client, message):
    if message["channel_type"] == "im": # Direct message
        reply = client.chat_postMessage(channel = message["channel"], thread_ts = message["ts"], text = WAITING_MESSAGE)
        response = process_conversation(client, message)
        client.chat_update(channel = message["channel"], ts = reply["ts"], text = response)
        
@app.event("app_mention")
def handle_app_mention_events(client, body):
    message = body["event"]
    reply = client.chat_postMessage(channel = message["channel"], thread_ts = message["ts"], text = WAITING_MESSAGE)
    response = process_conversation(client, message)
    client.chat_update(channel = message["channel"], ts = reply["ts"], text = response)

#============================================#
def process_conversation(client, message):
    conversation_history = get_conversation_history(client, message)
    result = get_gpt_response(ai_client, GPT_MODEL, SYSTEM_PROMPT, conversation_history, tools)
    if result.content:
        response = result.content
    elif result.tool_calls:
        function_name = result.tool_calls[0].function.name
        arguments = json.loads(result.tool_calls[0].function.arguments)
        if function_name == "generate_image":
            description = arguments["description"]
            try:
                size = arguments["size"]
            except:
                size = "square"
            try:
                image_url = generate_image(ai_client, IMAGE_MODEL, description, size)
                image_content = requests.get(image_url)
                image_filepath = f'{TEMP_FILES_FOLDER}/{generate_random_file_name()}.jpg'
                with open(image_filepath, "wb") as f:
                    f.write(image_content.content)
                client.files_upload_v2(channel = message["channel"], thread_ts = message["ts"], file = image_filepath, title = description)
                response = f'[SUCCESS] Image has been generated successfully'
                clean_up_file(image_filepath)
            except Exception as e:
                response = f'[ERROR] Problem generating image using DALL-E:\n {e}'
        elif function_name == "generate_tts":
            input_text = arguments["input_text"]
            try:
                generated_file = generate_tts(ai_client, TEMP_FILES_FOLDER, TTS_MODEL, TTS_VOICE, input_text)
                client.files_upload_v2(channel = message["channel"], thread_ts = message["ts"], file = generated_file, title = "Text To Speech")
                response = f'[SUCCESS] Your text has been converted to speech'
                clean_up_file(generated_file)
            except Exception as e:             
                response = f'[ERROR] Problem converting from text to speech:\n {e}'
        elif function_name == "generate_stt":
            if "files" in message:
                try:
                    file_path = save_uploaded_file(message["files"][0])
                    response = f'[SUCCESS] {generate_stt(ai_client, file_path, STT_MODEL)}'
                    clean_up_file(file_path)
                except Exception as e:
                    response = f'[ERROR] Problem converting from speech to text:\n {e}'
            else:
                response = f'[ERROR] No attached audio found in your message'
        else:
            response = f"[ERROR] Invalid function"
    else:
        response = f"[ERROR] Invalid response from OpenAI"
    return response

def get_conversation_history(client, message):
    result = []
    if "thread_ts" in message:
        conversation = client.conversations_replies(channel = message["channel"], ts = message["thread_ts"])
        if "messages" in conversation:
            for msg in conversation["messages"]:
                if "client_msg_id" in msg:
                    gpt_message = create_gpt_user_message_from_slack_message(msg)
                    result.append(gpt_message)
                if "bot_id" in msg:
                    if msg["text"] != WAITING_MESSAGE:
                        result.append({"role": "assistant", "content": msg["text"]})
    else:
        gpt_message = create_gpt_user_message_from_slack_message(message)
        result.append(gpt_message)
    return result

def save_uploaded_file(file):
    url = file["url_private"]
    file_path = f'{TEMP_FILES_FOLDER}/{generate_random_file_name()}.{file["filetype"]}'
    headers = {"Authorization": "Bearer " + SLACK_BOT_USER_TOKEN}
    response = requests.get(url, headers = headers)
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path

def create_gpt_user_message_from_slack_message(slack_message):
    if "files" in slack_message:
        attached_file = slack_message["files"][0]
        if attached_file["filetype"].lower() in ["png", "jpg", "jpeg", "gif", "webp"]:
            image_file = save_uploaded_file(attached_file)
            base64_image = encode_image(image_file)
            result = {
                "role": "user",
                "content": [
                    {"type": "text", "text": slack_message["text"]},
                    {
                        "type": "image_url",
                        "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
            clean_up_file(image_file)
        else:
            result = {"role": "user", "content": slack_message["text"]}
    else:
        result = {"role": "user", "content": slack_message["text"]}
    return result

def clean_up_file(file_path):
    try:
        os.remove(file_path)
    except:
        pass

def remove_mentions(text):
    pattern = r'<@.*?>'
    return re.sub(pattern, '', text)

#============================================#

# Create folder for temporary files if not exist
if not os.path.exists(TEMP_FILES_FOLDER):
    os.makedirs(TEMP_FILES_FOLDER)
# Start the bot
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_SOCKET_TOKEN).start()
