import requests
import os
import random
import sys
import json

# 1. إعدادات المحتوى
AFFILIATE_LINK = "https://www.checkout-ds24.com/redir/533733/snow002023/"
topics = [
    "how to whiten teeth naturally at home",
    "best probiotics for dental health",
    "how to prevent gum disease naturally",
    "how to stop bad breath permanently",
    "best foods for strong teeth and gums",
    "natural ways to strengthen tooth enamel"
]
topic = random.choice(topics)

# 2. الحصول على توكن الوصول
token_res = requests.post(
    "https://oauth2.googleapis.com/token",
    data={
        "client_id": os.environ["BLOGGER_CLIENT_ID"],
        "client_secret": os.environ["BLOGGER_CLIENT_SECRET"],
        "refresh_token": os.environ["BLOGGER_REFRESH_TOKEN"],
        "grant_type": "refresh_token"
    }
)
print(f"Client ID starts with: {os.environ['BLOGGER_CLIENT_ID'][:10]}...")
print(f"Refresh token starts with: {os.environ['BLOGGER_REFRESH_TOKEN'][:10]}...")
print(f"Token response: {token_res.text}")
access_token = token_res.json().get("access_token")
if not access_token:
    print(f"❌ Failed to refresh token: {token_res.text}")
    sys.exit(1)

# 3. جلب صورة
image_url = "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5"
try:
    res = requests.get(
        "https://api.unsplash.com/search/photos",
        params={"query": "dental care teeth", "per_page": 5},
        headers={"Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"}
    )
    if res.status_code == 200:
        image_url = random.choice(res.json()["results"])["urls"]["regular"]
except:
    pass

# 4. توليد المحتوى عبر Gemini
prompt = f"Write a detailed blog post about {topic} in HTML. Use H1 for title, H2 for sections. No markdown, no ``` tags. Include FAQ."
gemini_url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=){os.environ['GEMINI_API_KEY']}"
gemini_res = requests.post(gemini_url, json={"contents": [{"parts": [{"text": prompt}]}]})

try:
    content = gemini_res.json()['candidates'][0]['content']['parts'][0]['text']
    content = content.replace("```html", "").replace("```", "").strip()
except Exception as e:
    print(f"❌ Gemini Error: {e}")
    sys.exit(1)

# 5. بناء المقال
full_html = f"""
<div style="text-align:center;"><img src="{image_url}" style="width:100%;max-width:800px;border-radius:15px;"/></div>
{content}
<div style="background:#f0f7ff;padding:20px;border-radius:10px;text-align:center;margin-top:30px;">
    <h3>🦷 Expert Recommendation</h3>
    <a href="{AFFILIATE_LINK}" style="background:#007BFF;color:white;padding:12px 25px;text-decoration:none;border-radius:5px;display:inline-block;">Learn More Here</a>
</div>
"""

# 6. النشر في Blogger
blog_id = os.environ["BLOGGER_BLOG_ID"]
post_url = f"[https://www.googleapis.com/blogger/v3/blogs/](https://www.googleapis.com/blogger/v3/blogs/){blog_id}/posts/"
payload = {
    "kind": "blogger#post",
    "blog": {"id": blog_id},
    "title": topic.capitalize() + " (Full Guide 2026)",
    "content": full_html
}

publish_res = requests.post(
    f"{post_url}?isDraft=false",
    headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    data=json.dumps(payload)
)

if publish_res.status_code in [200, 201]:
    print(f"✅ SUCCESS! Published: {payload['title']}")
else:
    print(f"❌ Blogger Error: {publish_res.status_code}")
    print(f"Response: {publish_res.text}")
    sys.exit(1)
