import json
import time
from datetime import datetime

import requests
from discord_webhooks import DiscordWebhooks

bot_token = ""
web_hook_url = ""
base_vote_url = "https://ark-servers.net/api/?object=servers&element=voters&key={}&month=current&format=json"
base_discord_url = "https://discordapp.com/api/v6"
messages_endpoint = "/channels/663811736725487676/messages"
delete_endpoint = "/channels/663811736725487676/messages/{}"
discord_auth = {"Authorization": f"Bot {bot_token}"}
server_keys = []


def get_vote_json():
    with open('voters.json') as f:
        return json.load(f)


def save_vote_json(data):
    with open('voters.json', 'w') as json_file:
        json.dump(data, json_file)


def build_data():
    for key in server_keys:
        try:
            r = requests.get(base_vote_url.format(key))
            raw = r.json()
            server = raw["name"]
            voters = raw["voters"]
            data = get_vote_json()
            data[server] = voters
            save_vote_json(data)
        except Exception as e:
            print(e)
            continue


def send_webhook():
    voters = []
    max_votes = []
    data = get_vote_json()
    for x in data.items():
        for v in x[1]:
            voters.append(v)
    for x in voters:
        if x["nickname"] in [x["nickname"] for x in max_votes]:
            for u in max_votes:
                if u["nickname"] == x["nickname"]:
                    u["votes"] = str(int(x["votes"]) + int(u["votes"]))
        else:
            max_votes.append(x)
    message = "**Current Votes!** \U0001F389 \n\n"
    for v in max_votes:
        message += f"**User:** {v['nickname']} **Votes:** {v['votes']}\n"
    webhook = DiscordWebhooks(web_hook_url)
    webhook.set_content(content="**Vote Rewards**:\n"
                                "**12 = 500ARc\n15 = 750ARc\n18 = 1000ARc\n21 = 1250ARc**\n\n",
                        title='Click Me To Vote!',
                        description=message,
                        url='https://ark-servers.net/group/568/',
                        timestamp=str(datetime.now()),
                        color=0xF58CBA)
    webhook.send()


def delete_messages():
    r = requests.get(url=base_discord_url + messages_endpoint, headers=discord_auth)
    raw = r.json()
    ids = []
    if len(raw) > 1:
        for m in raw:
            ids.append(m["id"])
    requests.post(url=base_discord_url + delete_endpoint.format("bulk-delete"), headers=discord_auth,
                  json={"messages": ids})
    if len(raw) == 1:
        requests.delete(url=base_discord_url + delete_endpoint.format(raw[0]["id"]), headers=discord_auth)


if __name__ == "__main__":
    while True:
        delete_messages()
        build_data()
        send_webhook()
        time.sleep(3600)
