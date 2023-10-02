import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime, timedelta
from slack_sdk.errors import SlackApiError

import logging
from slack import WebClient
from config import Utils
import yaml
import uuid
import time
from vertexai.preview.language_models import TextGenerationModel
from google.cloud import bigquery

CHANNEL_ID = "<CHANNEL_ID>"
utils_instance = Utils()
big_query_client = bigquery.Client()

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    SLACK_BOT_TOKEN = config['SLACK_BOT_TOKEN']
  
@utils_instance.app.event("message")
def handle_message_events(body, logger):
    ack()
    logger.info(body)

def summarised_thread(message_text_str="", channel_id=CHANNEL_ID, conversation_history_ts=0):

    post_msg = utils_instance.app.client.chat_postMessage(
        channel=channel_id,
        thread_ts=conversation_history_ts,
        text=f"Hello from your bot! :robot_face: \nSeems like the thread is closed. I'm summatizing the issue for myself!"
    )

    # Palm2
    parameters = {
        "temperature": .2,
        "max_output_tokens": 256,   
        "top_p": .8,                
        "top_k": 40,                 
    }
    model = TextGenerationModel.from_pretrained("text-bison@001")
    palm_answer_response = model.predict(
        "\n".join([
            f'This chat log format is one line per message in the format "Time-stamp: Speaker name: Message".',
            f'The `\\n` within the message represents a line break.',
            f'The user understands English only.',
            f'So, The assistant need to speak in English.',
            f'Do not include greeting/salutation/polite expressions in summary',
            f'Additionally, output must have followed format. The output must be starting from summary section',
            f'''something like 
            【Summary】
            - Summary 1
            - Summary 2
            - Summary 3
            ''',
            f'please use following text input as input chat log',
            f'{message_text_str}',
            f'please make sure output text is written in English'
        ]),
        **parameters,
    )


    re_post_msg = utils_instance.app.client.chat_postMessage(
        channel=channel_id, 
        thread_ts=conversation_history_ts,
        text=f"Here you go: \n{palm_answer_response}"
    )

    print(f"palm_answer_response:\n{palm_answer_response}")
    palm_topic_response = model.predict(
    "\n".join([
        f'Can you tell what is the topic of the following answer but in one sentence and just return the result its and not any additional info.',
        f'For example if I ask How many kind of vegetables do exist? then I expect to get just the word vegetables.',
        f'The result needs to be like a title, a word. I should be headline that tells what is the answer about.',
        f'Here is the answer below that you need to supply the relevant title\word\headline:',
        f'{str(palm_answer_response)}'
    ]),
        **parameters,
    )

    print(f"palm_topic_response: {palm_topic_response}")

    # Insert to BigQuery
    input_string=str(palm_answer_response)
    # Split the input string into a list of questions
    questions_list = input_string.split('\n')

    json_data = [
        {"topic": str(palm_topic_response), "summarization": questions_list},
    ]

    # Define the schema for your table
    schema = [
        bigquery.SchemaField("topic", "STRING"),
        bigquery.SchemaField("summarization", "STRING", mode="REPEATED"),
    ]

    # Create a BigQuery table reference
    table_ref = big_query_client.dataset("slack").table("slack_summarization")

    # Create the load job configuration
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    # Load the JSON data into the table
    load_job = big_query_client.load_table_from_json(
        json_data,
        table_ref,
        location="US",  # Must match the destination dataset location.
        job_config=job_config,
    )

    # Wait for the job to complete
    load_job.result()


def get_last_conversation(channel_id=CHANNEL_ID):
    message_texts = []
    oldest = datetime.timestamp(datetime.now() - timedelta(hours=4))
    conversation_history_list = utils_instance.app.client.conversations_history(
        channel=channel_id,
        oldest=oldest
    )

    for conversation_history in conversation_history_list["messages"]:
        print(f"---------{conversation_history['thread_ts']}-------------------")
        conversations_replies = utils_instance.app.client.conversations_replies(
            channel=channel_id,
            ts=conversation_history["thread_ts"],
            limit=1000
        )
        time_difference = datetime.now() - datetime.fromtimestamp(float(conversations_replies["messages"][-1]["thread_ts"]))
        if time_difference > timedelta(hours=0.1):
            print("The timestamp is more than 3 hours old.")
            user_id=conversations_replies["messages"][-1]["user"]
            asd_user_info = utils_instance.app.client.users_info(user=user_id)
            user_info = utils_instance.app.client.users_info(user=user_id)["user"]
            if not user_info["is_bot"]:
                for reply in conversations_replies["messages"]:
                    reply_userid = reply["user"]
                    reply_user_info = utils_instance.app.client.users_info(user=reply_userid)["user"]
                    reply_username = reply_user_info["name"]
                    reply_message_text = reply["text"]
                    reply_ts = datetime.fromtimestamp(float(reply["ts"])).strftime("%Y-%m-%d %H:%M:%S")
                    message_texts.append({'username': reply_username, 'text': reply_message_text, 'ts': reply_ts})

                    if message_texts == []:
                        summarised_txt = f'{utils_instance.TXT_NOUPDATE}'
                    else:
                        message_texts = sorted(message_texts, key=lambda k: k['ts'])
                        message_text_str = ""
                        for item in message_texts:
                            message_text_str += f"'{item['ts']}': {item['username']} said: '{item['text']}'\n"

                print(f"Needs to summarize: {message_text_str}")
                summarised_thread(message_text_str, CHANNEL_ID, conversation_history["thread_ts"])
            else:
                print(f"No need to summarize; We've already did it.")

while True:
    print("Function triggered at:", time.strftime("%H:%M:%S"))

    # Define the time interval in seconds (e.g., 2 minutes)
    interval_minutes = 1
    interval_seconds = interval_minutes * 60
    get_last_conversation()
    time.sleep(interval_seconds)