import os, json, urllib.request, urllib.error
from pathlib import Path


def send_discord(webhook_url: str, content: list[str]):
    payload = {"content": "\n".join(content)}
    print(payload)
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "link-checker/1.0"},
        method="POST",
    )
    # lets try to use logs instead of print
    try:
        with urllib.request.urlopen(req) as resp:
            print("Discord status:", resp.status)
            print(resp.read().decode("utf-8", errors="ignore"))
    except urllib.error.HTTPError as e:
        print("Discord HTTPError:", e.code)
        body = e.read().decode("utf-8", errors="ignore")
        print("Discord response body:", body)
        raise


# can add a hardcoded webhook for the time being (when testing the file itself)
# webhook = os.environ["DISCORD_WEBHOOK_URL"]
# here goes the user id of the user we want to ping
# user_id = os.environ["USER_ID"]

REPO_ROOT = Path(__file__).resolve().parents[1]  # works only if the script is in /scripts
URL_LIST_PATH = REPO_ROOT / "data" / "webpages" / "test_list.json"

failed_urls = []

with open(URL_LIST_PATH) as f:
    urls = json.load(f)

for url in urls:
    url_status = urllib.request.urlopen(url).getcode()
    print(f"url status: {url_status}")
    # uncomment this so that ts actually works with 404 calls or any other calls which arent 200
    # if url_status != 200:
    #    failed_urls.append(f"FAILED URL: {url}")
    # adds "FAILED URL:" before each url
    failed_urls.append("FAILED URL: " + url)  # remove this after testing


payload = failed_urls
# this cmd is when we actually implement user_id
# payload.insert(0, f"<@{user_id}>, these links are returning a 404! Check these links.")
payload.insert(0, "@test, these links are returning a 404! Check these links.")
# if failed_urls: # add 'not' later after testing and shit
#     send_discord(webhook, payload)
print(payload)  # remove this after testing
