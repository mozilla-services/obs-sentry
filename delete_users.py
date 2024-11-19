#!/bin/python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///
"""
Delete a set of users from the Mozilla Sentry organization.

The user ids of the users to delete are read from stdin. Each line starting with a
integer user id specifies a user to delete. Other lines are ignored. You can optionally
specify the main email address of the user account in addition to the user id, and the
script will only delete the user if the email address matches. Further fields after the
email address are also ignored.

You can use the output of the `obsolete_user.py` script as an input for this script.

You need to set the `SENTRY_TOKEN` environment variable.

Summary of the input line format:

    <user id> [<primary email>] [<ignored fields> ...]

Example input with just user ids:

    1250801
    1407292
    1894897

Example input with user ids, email addresses and full names:

    1250801 fallen@mozilla.com     Frances Allen
    1407292 ghopper@mozilla.com    Grace Hopper
    1894897 alovelace@mozilla.com  Ada Lovelace
"""

import os
import sys

from dotenv import load_dotenv

from sentry_client import SentryClient


def parse_and_validate_input(input: str, client: SentryClient) -> list[str]:
    member_ids = []
    for line in input.splitlines():
        tokens = line.split(maxsplit=2)
        if not tokens:
            continue
        member_id = tokens[0]
        try:
            int(member_id)
        except ValueError:
            continue
        if len(tokens) > 1:
            email = tokens[1]
            actual_email = client.get_member(member_id)["email"]
            if email != actual_email:
                print(
                    f"mismatched email address for member id {member_id}:",
                    file=sys.stderr,
                )
                print(
                    f"given in input: {email}, actual: {actual_email}", file=sys.stderr
                )
                sys.exit(1)
        member_ids.append(member_id)
    return member_ids


def main(input: str):
    client = SentryClient(os.environ["SENTRY_TOKEN"])
    for member_id in parse_and_validate_input(input, client):
        print(f"Deleting member with id {member_id}...")
        client.delete_member(member_id)


if __name__ == "__main__":
    load_dotenv()
    main(sys.stdin.read())
