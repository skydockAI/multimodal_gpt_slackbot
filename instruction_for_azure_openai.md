# Instruction for Azure OpenAI
If you use Azure OpenAI instead of OpenAI, please use the config file [config_azure.env]:
- Update the 3 variables AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_VERSION with your Azure OpenAI information
- Azure OpenAI uses deployment names instead of model names. You should update the model names in the configuration file with your correct deployment names
- Run the Docker image with [config_azure.env] (instead of [config.env]). For example:
```bash
docker run --env-file ./config_azure.env multimodal_gpt_slackbot:latest
```

## Notes:
- GPT Vision only works with GPT-4-Turbo model. You must use an equivalent model from Azure OpenAI for GPT Vision to work.