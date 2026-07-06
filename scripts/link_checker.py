import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from src.config.logger import get_logger

log = get_logger(__name__)


# sends relevant info to webhook
def send_discord(webhook_url: str, content: list[str]):
    payload = {"content": "\n".join(content)}
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "link-checker/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            log.info("Discord status:", status=resp.status)
            log.info(resp.read().decode("utf-8", errors="ignore"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        log.error("Discord HTTPError:", error=e.code, response_body=body)
        raise


# webhook for the discord channel
webhook = os.environ["DISCORD_WEBHOOK_URL"]
# user id of the user we want to ping
user_id = os.environ["USER_ID"]

# works only if this script is in /scripts
REPO_ROOT = Path(__file__).resolve().parents[1]
# replace with any list
URL_LIST_PATH = REPO_ROOT / "data" / "webpages" / "test_list.json"

failed_urls = []

with open(URL_LIST_PATH) as f:
    urls = json.load(f)

for url in urls:
    url_status = urllib.request.urlopen(url).getcode()
    if url_status != 200:
        failed_urls.append(f"FAILED URL: {url}")
    # uncomment this if you want to try the functionality with any other statuscode (or none)
    # failed_urls.append("FAILED URL: " + url)

payload = failed_urls
payload.insert(0, f"<@{user_id}>, these links are returning a 404! Check these links.")

if failed_urls:
    send_discord(webhook, payload)
