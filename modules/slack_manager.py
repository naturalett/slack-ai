from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta

class SlackManager:
    def __init__(self, app, app_client):
        self.app = app
        self.app_client = app_client

    def get_last_conversation(self, channel_id, app):
        try:
            message_texts = []
            summarised_conversation = {}
            oldest = datetime.timestamp(datetime.now() - timedelta(hours=3))
            conversation_history_list = app.client.conversations_history(
                channel=channel_id,
                oldest=oldest
            )

            for conversation_history in conversation_history_list["messages"]:
                if conversation_history.get('thread_ts', 0) != 0:
                    print(f"---------{conversation_history['thread_ts']}-------------------")
                    conversations_replies = app.client.conversations_replies(
                        channel=channel_id,
                        ts=conversation_history["thread_ts"],
                        limit=1000
                    )
                    time_difference = datetime.now() - datetime.fromtimestamp(float(conversations_replies["messages"][-1]["thread_ts"]))
                    if time_difference > timedelta(hours=0.01):
                        print("The timestamp is more than 3 hours old.")
                        user_id=conversations_replies["messages"][-1]["user"]
                        asd_user_info = app.client.users_info(user=user_id)
                        user_info = app.client.users_info(user=user_id)["user"]
                        if not user_info["is_bot"]:
                            for reply in conversations_replies["messages"]:
                                reply_userid = reply["user"]
                                reply_user_info = app.client.users_info(user=reply_userid)["user"]
                                reply_username = reply_user_info["name"]
                                reply_message_text = reply["text"]
                                reply_ts = datetime.fromtimestamp(float(reply["ts"])).strftime("%Y-%m-%d %H:%M:%S")
                                message_texts.append({'username': reply_username, 'text': reply_message_text, 'ts': reply_ts})

                                if message_texts == []:
                                    summarised_txt = f'{TXT_NOUPDATE}'
                                else:
                                    message_texts = sorted(message_texts, key=lambda k: k['ts'])
                                    message_text_str = ""
                                    for item in message_texts:
                                        message_text_str += f"'{item['ts']}': {item['username']} said: '{item['text']}'\n"

                            print(f"Needs to summarize:\n{message_text_str}")
                            ts = conversation_history["thread_ts"]
                            summarised_conversation[ts] = message_text_str
                        else:
                            print(f"No need to summarize; We've already did it.")
                    else:
                        print("Time delta is not more than 3 hours")

        except SlackApiError as e:
            print('Error retrieving conversation history:', e)

        return summarised_conversation

    def post_message(self, channel_id, thread_ts, app, message):
        post_msg = app.client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=message
        )
