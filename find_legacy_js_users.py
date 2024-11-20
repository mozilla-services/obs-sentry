#!/bin/python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///

"""
Find projects using obsolete versions of the Sentry JavaScript SDK.

The script lists the affected projects as well as the team admins of the teams owning
these projects.

You need to set the `SENTRY_RO_TOKEN` environment variable to run this script.
"""

import os

from dotenv import load_dotenv

from sentry_client import SentryClient


def main():
    client = SentryClient(os.environ["SENTRY_RO_TOKEN"])

    print("Affected projects:")
    teams = []
    for project in client.projects():
        project_slug = project["slug"]
        query = "sdk.name:sentry.javascript.browser !sdk.version:8.*"
        results = False
        for _ in client.issues(project_slug, query):
            results = True
            break
        if results:
            team_slug = project["team"]["slug"]
            print(f"    {project_slug:<30} owned by {team_slug}")
            print(
                f"        https://mozilla.sentry.io/issues/?project={project["id"]}&query=sdk.name%3Asentry.javascript.browser%20%21sdk.version%3A8.%2A&referrer=issue-list&statsPeriod=14d"
            )
            teams.append(team_slug)

    print("\nTeam admins:")
    members = set()
    for team_slug in teams:
        print(f"\n    {team_slug}")
        for member in client.team_members(team_slug):
            if member["orgRole"] != "member" or member["teamRole"] is not None:
                formatted = f"{member["name"]} <{member["email"]}>"
                members.add(formatted)
                print(f"        {formatted}")

    print("\nDeduplicated list of admins:")
    print("   ", ",\n    ".join(sorted(members)))


if __name__ == "__main__":
    load_dotenv()
    main()
