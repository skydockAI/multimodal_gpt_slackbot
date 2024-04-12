# Welcome to Multimodal GPT Slackbot by SkyDock AI 👋

**Run your own secure version of ChatGPT Enterprise in just a few minutes ⚡️**

Multimodal GPT Slackbot is a comprehensive Docker image designed to enable businesses to empower their teams with the latest AI technologies provided by OpenAI, in a secure and efficient manner. By integrating OpenAI's APIs on the backend with Slack as the user interface, it offers a seamless experience for users to engage with multimodal AI capabilities directly within Slack.

- ✅ Conversation History
- ✅ GPT Vision Support
- ✅ Image Generation
- ✅ Text to Speech Conversion
- ✅ Speech to Text Conversion


## 🚀 Quickstart
To run Multimodal GPT Slackbot, you can choose from several options:

### 1. Using the Pre-built Docker Image:
Pull the Docker image:
```bash
docker pull skydockai/multimodal_gpt_slackbot:latest
```

Configure Environment Variables: Download the [config.env](https://github.com/skydockAI/multimodal_gpt_slackbot/blob/main/config.env) file and update the first three variables (**SLACK_SOCKET_TOKEN**, **SLACK_BOT_USER_TOKEN**, and **OPENAI_KEY**) with your Slack app tokens and OpenAI API key.

Run the Docker image:
```bash
docker run --env-file ./config.env multimodal_gpt_slackbot:latest
```

### 2. Building Your Own Docker Image:
Clone the source code:
```bash
git clone https://github.com/skydockAI/multimodal_gpt_slackbot.git
```

Build the Docker image:
```bash
docker build -t multimodal_gpt_slackbot:latest .
```

Configure and run: Follow the same steps as in the pre-built Docker image setup to configure your `config.env` and run the image.

### 3. Using Docker Compose:
Clone the source code:
```bash
git clone https://github.com/skydockAI/multimodal_gpt_slackbot.git
```

Configure environment variables: Update the `config.env` as described above.

Run with Docker Compose: 
```bash
docker compose up
```


## Key Features:
- **Conversation History**: Maintains the context of each conversation within a Slack thread, ensuring continuity and ease of reference.
<img src="/images/conversation_history.png" alt="Conversation History"></img>

- **GPT Vision Support**: Utilizes the gpt-4-turbo model to provide cutting-edge vision capabilities.
<img src="/images/gpt_vision.png" alt="GPT Vision Support"></img>

- **Image Generation**: Leverages the Dall-E models to support creative and dynamic image generation.
<img src="/images/image_generation.png" alt="Image Generation"></img>

- **Text to Speech Conversion**: Converts text messages into spoken words, enhancing accessibility.
<img src="/images/tts.png" alt="Text to Speech Conversion"></img>

- **Speech to Text Conversion**: Uses the Whisper model to transcribe spoken words into text, facilitating easy communication.
<img src="/images/stt.png" alt="Speech to Text Conversion"></img>


## License:
**Multimodal GPT Slackbot** is open-source and licensed under the [GPL-3.0](LICENSE) license.
