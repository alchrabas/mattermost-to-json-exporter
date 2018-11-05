import datetime
import json

channels = json.load(open("dumped_mattermost.json", "r"))

new_channels = []
for channel in channels:
    final_records = []
    displayed_date = datetime.date.fromtimestamp(0)
    for post in channel["posts"]:
        post_date = datetime.date.fromtimestamp(post["timestamp"] / 1000)
        date_and_time = datetime.datetime.fromtimestamp(post["timestamp"] / 1000)
        if post_date > displayed_date:
            final_records.append({
                "message": "[" + str(post_date) + "]",
                "pictures": [],
            })
            displayed_date = post_date
        final_records.append({
            "message": str(date_and_time.hour).zfill(2) +
                       ":" + str(date_and_time.minute).zfill(2) +
                       " <" + post["user"] + "> " + post["message"],
            "pictures": post["pictures"]})
    new_channels += [
        {
            "name": channel["name"],
            "messages": final_records,
        }
    ]

with open("formatted.json", "w") as f:
    f.write(json.dumps(new_channels))
