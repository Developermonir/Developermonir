"""Refresh the 'Latest' line in README.md with current plugin versions."""
import json
import re
import urllib.request


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-readme"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def safe(fn):
    try:
        return fn()
    except Exception as e:
        print("fetch failed:", e)
        return None


pro = safe(lambda: get("https://pro.breakui.com/wp-json/bu-pro/v1/update")["version"])
pp = safe(lambda: get("https://api.wordpress.org/plugins/info/1.2/?action=plugin_information"
                      "&request%5Bslug%5D=breakui-preview-pass")["version"])

text = open("README.md", encoding="utf-8").read()
if pro:
    text = re.sub(r"(BreakUI Pro</a> <b>)v[\d.]+(</b>)", rf"\g<1>v{pro}\g<2>", text)
if pp:
    text = re.sub(r"(Preview Pass</a> <b>)v[\d.]+(</b>)", rf"\g<1>v{pp}\g<2>", text)
open("README.md", "w", encoding="utf-8").write(text)
print("BreakUI Pro", pro, "| Preview Pass", pp)
