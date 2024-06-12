from quixstreams import Application  # import the Quix Streams modules for interacting with Kafka:
# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# import additional modules as needed
import random
import os
import json
import requests

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="data_source", auto_create_topics=True)  # create an Application

# define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

# Replace with your GitHub token and repository details
GITHUB_TOKEN = os.getenv('GH_TOKEN', '')
OWNER = 'quixio'
REPO = 'quix-streams'

def get_data():

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get traffic sources
    traffic_url = f'https://api.github.com/repos/{OWNER}/{REPO}/traffic/popular/referrers'
    response = requests.get(traffic_url, headers=headers)
    traffic_sources = response.json()

    # Get referring sites
    referring_sites_url = f'https://api.github.com/repos/{OWNER}/{REPO}/traffic/popular/paths'
    response = requests.get(referring_sites_url, headers=headers)
    referring_sites = response.json()

    # Get total and unique visitors
    views_url = f'https://api.github.com/repos/{OWNER}/{REPO}/traffic/views'
    response = requests.get(views_url, headers=headers)
    views = response.json()


    # debug
    traffic_sources_json = json.dumps(traffic_sources)
    referring_sites_json = json.dumps(referring_sites)
    views_json = json.dumps(views)
    print("Traffic Sources JSON:", traffic_sources_json)
    print("Referring Sites JSON:", referring_sites_json)
    print("Views JSON:", views_json)


    return {
        'traffic': traffic_sources,
        'referrers': referring_sites,
        'views': views,
    }

def main():
    """
    Read data from the hardcoded dataset and publish it to Kafka
    """
    while True:
        # create a pre-configured Producer object.
        with app.get_producer() as producer:
            # iterate over the data from the hardcoded dataset
            data_with_id = get_data()
            for row_data in data_with_id:

                json_data = json.dumps(row_data)  # convert the row to JSON

                # publish the data to the topic
                producer.produce(
                    topic=topic.name,
                    key=f'github_stats_{OWNER}_{REPO}',
                    value=json_data,
                )

                # for more help using QuixStreams see docs:
                # https://quix.io/docs/quix-streams/introduction.html

            print("All rows published")
        time.sleep(3600) # sleep 1 hour


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")