from vertexai.preview.language_models import TextGenerationModel
import yaml
import os

class PalmModel:
    def __init__(self):
        self.model = TextGenerationModel.from_pretrained("text-bison@001")
        self.parameters = {
            "temperature": .2,
            "max_output_tokens": 256,
            "top_p": .8,
            "top_k": 40,
        }

        # Load prompts from YAML file
        with open(f'{os.getcwd()}/modules/prompts.yaml', 'r') as yaml_file:
            self.prompts = yaml.safe_load(yaml_file)

    def generate_summary(self, message_text_str):
        prompt = self.prompts['resolution_prompt'][0].format(message_text=message_text_str)
        return self.model.predict(prompt, **self.parameters)

    def generate_topic(self, message_text_str):
        prompt = self.prompts['topics'][0].format(message_text=message_text_str)
        return self.model.predict(prompt, **self.parameters)
