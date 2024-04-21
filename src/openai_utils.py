import base64
import random
import time
from types import SimpleNamespace

def get_gpt_response(ai_client, gpt_model, system_prompt, conversation_history, tools):
    prompt_structure = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history:
        prompt_structure.append(msg) 
    try:
        response = ai_client.chat.completions.create(
            model = gpt_model,
            messages = prompt_structure,
            tools = tools,
            tool_choice = "auto"
        )
        return response.choices[0].message
    except Exception as e:
        return SimpleNamespace(content=f"[ERROR] Problem calling OpenAI API:\n {e}")

def generate_image(ai_client, image_model, input_text, size = "square"):
    if size == "portrait":
        image_size = "1024x1792"
    elif size == "landscape":
        image_size = "1792x1024"
    else:
        image_size = "1024x1024"
    response = ai_client.images.generate(model = image_model, prompt = input_text, size = image_size, quality = "standard", n=1)
    return response.data[0].url

def generate_tts(ai_client, file_folder, tts_model, tts_voice, input_text):
    speech_file_path = f'{file_folder}/{generate_random_file_name()}.mp3'
    with ai_client.audio.speech.with_streaming_response.create(model = tts_model, voice = tts_voice, input = input_text) as response:
        response.stream_to_file(speech_file_path)
    return speech_file_path

def generate_stt(ai_client, file_path, stt_model):
    audio_file= open(file_path, "rb")
    response = ai_client.audio.transcriptions.create(model = stt_model, file = audio_file, response_format="text")
    return response

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_random_file_name():
    return f'{int(time.time_ns())}_{random.randint(0,10000)}'