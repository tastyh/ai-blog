import requests
import os
import random
import time

AFFILIATE_LINK = "https://www.checkout-ds24.com/redir/533733/snow002023/"
HISTORY_FILE = "used_topics.txt"
FIRST_RUN_FILE = "first_run_done.txt"

topics = [
    "how to whiten teeth naturally at home",
    "best probiotics for dental health",
    "how to prevent gum disease naturally",
    "how to stop bad breath permanently",
    "best foods for strong teeth and gums"
]

def is_first_run():
    return not os.path.exists(FIRST_RUN_FILE)

def mark_first_run_done():
    with open(FIRST_RUN_FILE, "w") as f:
        f.write("done")

def load_used():
    if not os.path.exists(HISTORY_FILE):
        return []
    return open(HISTORY_FILE).read().splitlines()

def save_topic(topic):
    with open(HISTORY_FILE, "a") as f:
        f.write(topic + "\n")

def retry(func, tries=3):
    for i in range(tries):
        try:
            return func()
        except Exception as e:
            print(e)
            time.sleep(2)
    return None

def get_token():
    def req():
        return requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": os.environ["BLOGGER_CLIENT_ID"],
                "client_secret": os.environ["BLOGGER_CLIENT_SECRET"],
                "refresh_token": os.environ["BLOGGER_REFRESH_TOKEN"],
                "grant_type": "refresh_token"
            }
        ).json()

    data = retry(req)
    return data.get("access_token")

def generate(topic):
    def req():
        return requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            params={"key": os.environ["GEMINI_API_KEY"]},
            json={
                "contents": [{"parts": [{"text": f"Write SEO HTML article about {topic}"}]}]
            }
        ).json()

    data = retry(req)
    if not data or "candidates" not in data:
        return "<h1>Error</h1>"
    return data["candidates"][0]["content"]["parts"][0]["text"]

def post(token, title, content):
    return requests.post(
        f"https://www.googleapis.com/blogger/v3/blogs/{os.environ['BLOGGER_BLOG_ID']}/posts/",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"title": title, "content": content}
    )

used = load_used()
available = [t for t in topics if t not in used] or topics

token = get_token()

if is_first_run():
    print("FIRST RUN")
    mark_first_run_done()

topic = random.choice(available)
content = generate(topic)

res = post(token, topic, content)

if res.status_code == 200:
    print("Posted")
    save_topic(topic)
else:
    print(res.text)
