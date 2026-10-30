import os
import sys

ALLOWED_SUITES = {"smoke", "regression"}
ALLOWED_SERVICES = {"all", "admin", "auth", "follow", "feed", "messages", "notifications", "search"}
ALLOWED_TAGS = {"all", "flaky", "login", "post", "comment", "register", "like", "moderation"}


def parse_csv(name, allowed):
    raw = os.environ.get(name, "").strip()

    if not raw or raw == "all":
        return []

    values = [value.strip() for value in raw.split(",")]

    if any(not value for value in values):
        sys.exit(f"{name}: empty value in list")

    invalid = sorted(set(values) - allowed)
    if invalid:
        sys.exit(f"{name}: unknown markers: {invalid}")

    return list(dict.fromkeys(values))


suite = os.environ["SUITE"].strip()

if suite != "all" and suite not in ALLOWED_SUITES:
    sys.exit(f"Unknown SUITE: {suite}")

services = parse_csv("SERVICES", ALLOWED_SERVICES)
tags = parse_csv("TAGS", ALLOWED_TAGS)

parts = []

if suite == "all":
    parts.append("(" + " or ".join(ALLOWED_SUITES) + ")")
elif suite != "all":
    parts.append(suite)

if services:
    if "all" in services:
        ...
    else:
        parts.append("(" + " or ".join(services) + ")")

if tags:
    if "all" in tags:
        ...
    else:
        parts.append("(" + " or ".join(tags) + ")")

expression = " and ".join(parts)

print(f"Pytest marker expression: {expression or '(no filter)'}")

with open(os.environ["GITHUB_OUTPUT"], "a") as output:
    output.write(f"mark_expr={expression}\n")
