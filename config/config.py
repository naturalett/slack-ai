import yaml
import os

class Config:
    def __init__(self, config_file=f"{os.getcwd()}/config/config.yml"):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as f:
            config_data = yaml.safe_load(f)
            self.SLACK_BOT_TOKEN = config_data.get('SLACK_BOT_TOKEN', '')