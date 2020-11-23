from subprocess import getoutput  # skipcq: BAN-B404

import requests

VERSION = getoutput("cat VERSION 2>/dev/null || git describe --tags").lstrip("v")
CONTRIBUTORS = []
GITHUB_LINK = "https://github.com/luwol03/applybot"
AVATAR_URL = "https://github.com/luwol03.png"
GITHUB_DESCRIPTION = requests.get("https://api.github.com/repos/luwol03/applybot").json()["description"]
