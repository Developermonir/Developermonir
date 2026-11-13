"""Refresh plugin versions in the profile README."""
import json
import re
import urllib.request

README = "README.md"


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-readme"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def version_or_none(fn):
    try:
        return fn()
    except Exception:
        return None


pro = version_or_none(lambda: get_json("https://pro.breakui.com/wp-json/bu-pro/v1/update")["version"])
pp = version_or_none(
    lambda: get_json(
        "https://api.wordpress.org/plugins/info/1.2/?action=plugin_information&request%5Bslug%5D=breakui-preview-pass"
    )["version"]
)

text = open(README, encoding="utf-8").read()
if pro:
    text = re.sub(r"(\*\*BreakUI Pro\*\*\]\([^)]*\) \|[^|]*\| )v[\d.]+", rf"\g<1>v{pro}", text)
if pp:
    text = re.sub(r"(\*\*BreakUI Preview Pass\*\*.*?\|[^|]*\| )v[\d.]+", rf"\g<1>v{pp}", text)
open(README, "w", encoding="utf-8").write(text)
print("BreakUI Pro:", pro, "| Preview Pass:", pp)
