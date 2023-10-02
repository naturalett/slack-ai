from google.cloud import bigquery

class BigQueryManager:
    def __init__(self):
        self.big_query_client = bigquery.Client()
        self.big_query_dataset = "slack"
        self.big_query_table = "slack_summarization"
        self.big_query_location = "US"

    def insert_data(self, palm_topic_response, palm_answer_response):
        # Prepare the data for insertion
        input_string=palm_answer_response
        questions_list = input_string.split('\n')
        json_data = [{"topic": palm_topic_response, "summarization": questions_list, "counter": 1}]

        # Define the schema for your table
        schema = [
            bigquery.SchemaField("topic", "STRING"),
            bigquery.SchemaField("summarization", "STRING", mode="REPEATED"),
            bigquery.SchemaField("counter", "INT64"),
        ]

        # Create a BigQuery table reference
        table_ref = self.big_query_client.dataset(self.big_query_dataset).table(self.big_query_table)

        # Create the load job configuration
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )

        # Load the JSON data into the table
        load_job = self.big_query_client.load_table_from_json(
            json_data,
            table_ref,
            location=self.big_query_location,
            job_config=job_config,
        )

        # Wait for the job to complete
        load_job.result()

    def find_matching_summarization(self, topic):
        # Construct a BigQuery SQL query with query parameters to find a matching summarization based on the topic
        query_summarization = f"""
            SELECT summarization
            FROM `{self.big_query_dataset}.{self.big_query_table}`
            WHERE topic LIKE '%{topic}%'
        """

        # Create a query job
        query_job_summarization = self.big_query_client.query(
            query_summarization,
            location=self.big_query_location,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("topic", "STRING", f'%{topic}%')]
            ),
        )
        # Execute the query and retrieve results
        results_summarization = query_job_summarization.result()

        # Extract the matching summarization from the results
        matching_summarization = []
        for row in results_summarization:
            matching_summarization.extend(row['summarization'])

        if matching_summarization:

            #  Increase the counter if topic already exists.
            query_counter = f"""
                SELECT counter
                FROM `{self.big_query_dataset}.{self.big_query_table}`
                WHERE topic LIKE '%{topic}%'
                LIMIT 1
            """
            query_job_counter = self.big_query_client.query(
                query_counter,
                location=self.big_query_location,
                job_config=bigquery.QueryJobConfig(
                    query_parameters=[bigquery.ScalarQueryParameter("topic", "STRING", f'%{topic}%')]
                ),
            )
            counter = next(query_job_counter.result())['counter']
            query_update = f"""
                UPDATE `{self.big_query_dataset}.{self.big_query_table}`
                SET counter = {counter+1}
                WHERE topic LIKE '%{topic}%'
            """

            update_job = self.big_query_client.query(query_update, location=self.big_query_location)
            update_job.result()

            formatted_result = '\n'.join(matching_summarization)
            formatted_result = formatted_result.replace("'", "''")

            final_result = f"""
        {formatted_result}
            """

            print(final_result)
            return final_result
        else:
            return ""
