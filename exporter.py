import psycopg2
import json
from shutil import copyfile

conn = psycopg2.connect(database="mattermost", user="ENTER USER HERE", password="ENTER PASSWORD HERE", host="localhost")

cur = conn.cursor()

FILES_ROOT = "/opt/mattermost/data/"

cur.execute("SELECT id, username FROM users")


def copy_file_by_id(file_id):
    cur.execute("SELECT path FROM fileinfo WHERE id = %s", (file_id,))
    file_path = cur.fetchone()[0]
    absolute_path = FILES_ROOT + file_path

    unique_file_name = "_".join(file_path.split("/")[-2:])

    copyfile(absolute_path, "images/" + unique_file_name)
    return unique_file_name


def copy_file_by_name(file_name):
    absolute_path = FILES_ROOT + file_name
    unique_file_name = "_".join(file_name.split("/")[-2:])
    copyfile(absolute_path, "images/" + unique_file_name)
    return unique_file_name


users = {}
for (user_id, username) in cur.fetchall():
    users[user_id] = username

cur.execute("SELECT id, name FROM channels WHERE type = 'O'")

channels = {}
for (channel_id, channel_name) in cur.fetchall():
    channels[channel_id] = channel_name

all_posts = []
for channel_id in channels.keys():
    print("CHANNEL: ", channel_id, channels[channel_id])
    cur.execute(
        """SELECT id, channelid, message, userid, createat, filenames, fileids FROM posts WHERE channelid = %s
        AND deleteat = 0 ORDER BY channelid, createat""",
        (channel_id,))
    rows = cur.fetchall()

    posts = []
    for row in rows:
        post_id, channel_id, message, user_id, created, filenames, fileids = row
        # print(channels[channel_id], " <" + users.get(user_id, "UNKNOWN") + "> ", message)

        file_names = json.loads(filenames)
        file_ids = json.loads(fileids)

        files_to_save = []
        for file_id in file_ids:
            files_to_save += [copy_file_by_id(file_id)]

        for file_name in file_names:
            files_to_save += [copy_file_by_name(file_name)]

        posts.append({
            "user": users.get(user_id, "UNKNOWN"),
            "message": message,
            "timestamp": created,
            "pictures": files_to_save,
        })

    channel_data = {
        "id": channel_id,
        "name": channels[channel_id],
        "posts": posts,
    }
    all_posts.append(channel_data)

with open("dumped_mattermost.json", "w") as file:
    file.write(json.dumps(all_posts))

# print(json.dumps(all_posts, indent=4, sort_keys=True))
