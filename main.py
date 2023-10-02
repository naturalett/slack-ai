from slack_bolt import App
from modules.slack_manager import SlackManager
from modules.bigquery_manager import BigQueryManager
from modules.palm_model import PalmModel
from modules.highlights import HighlightFinder
from config.config import Config
import yaml
import time

config = Config()
CHANNEL_ID="<CHANNEL_ID>"
app = App(token=config.SLACK_BOT_TOKEN)
slack_manager = SlackManager(app, app.client)
bigquery_manager = BigQueryManager()
palm_model = PalmModel()
finder = HighlightFinder()

finder.set_highlight_words(['jenkins', 'unittest', 'twingate', 'npm', 'bigquery', 'connection', 'python', 'login'])

while True:
    print("Function triggered at:", time.strftime("%H:%M:%S"))
    # Define the time interval in seconds (e.g., 2 minutes)
    interval_minutes = 1
    answer_response = ""
    interval_seconds = interval_minutes * 60
    summarised_conversations = slack_manager.get_last_conversation(CHANNEL_ID, app)
    
    print(f"summarised_conversations: {summarised_conversations}")
    if summarised_conversations:
        for thread_ts, conversation in summarised_conversations.items():
            # Check matching words
            highlight_words = finder.find_highlight_words(conversation)
            if highlight_words:
                print(f"The keywords we extracted from the thread are: {highlight_words}")
                for word in highlight_words:
                    answer_response = bigquery_manager.find_matching_summarization(word)
            if answer_response == "":
                print("We don't have a stored answer in the Big Query. Let's generate one.")

                answer_response = str(palm_model.generate_summary(conversation))

                palm_topic_response = str(palm_model.generate_topic(answer_response)).replace('-', ' ')
                print(f"Topic that we generated from PLaM2:: {palm_topic_response}")

                bigquery_manager.insert_data(palm_topic_response, answer_response)

            print(f"Answer that we pulled:\n{answer_response}")
            slack_manager.post_message(CHANNEL_ID, thread_ts, app, "Hello from your bot! :robot_face: \nSeems like the thread is closed. I'm summatizing the resolution for myself!")
            slack_manager.post_message(CHANNEL_ID, thread_ts,  app, f"Here you go: \n{answer_response}")

    
    time.sleep(interval_seconds)
