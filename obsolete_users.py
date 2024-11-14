#!/bin/python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-dotenv",
#     "python-ldap",
#     "requests",
# ]
# ///
"""
List users with expired invites, and users who are no longer at Mozilla.

To find users no longer at Mozilla, the list of members of the Mozilla Sentry org is
checked against the LDAP directory. You need to be on the Mozilla Corp VPN to be able
to query the LDAP server.

You can pipe the output of the script to `delete_users.py` to delete all users in the
output from the Mozilla Sentry org.

You need to set the `LDAP_BIND_USER` and `SENTRY_RO_TOKEN` environment variables.
"""

import getpass
from operator import itemgetter
import os
import platform

from dotenv import load_dotenv
import ldap.dn

from sentry_client import SentryClient


LDAP_SERVER = "ldap://ldap-ro.vips.ldap.mdc1.mozilla.com"

# Only needed on Linux
CA_CERTIFICATES = "/etc/ssl/certs/ca-certificates.crt"


def ldap_connection():
    bind_user = os.environ["LDAP_BIND_USER"]
    password = getpass.getpass(f"Password for {bind_user}: ")
    connection = ldap.initialize(LDAP_SERVER)
    connection.protocol_version = ldap.VERSION3
    connection.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
    if platform.system() == "Linux":
        connection.set_option(ldap.OPT_X_TLS_CACERTFILE, CA_CERTIFICATES)
    connection.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
    connection.start_tls_s()
    connection.simple_bind_s(bind_user, password)
    return connection


def get_ldap_users():
    conn = ldap_connection()
    return set(
        user[1]["mail"][0].decode()
        for user in conn.search_s(
            base="dc=mozilla", scope=ldap.SCOPE_SUBTREE, attrlist=["mail"]
        )
        if "mail" in user[1]
    )


def print_users(users):
    for user in users:
        email = user["email"]
        user_id = user["id"]
        print(f"{user_id:<10} {email:<40}", end="")
        if user["user"]:
            print(user["user"]["lastLogin"])
        else:
            print()


def main():
    client = SentryClient(os.environ["SENTRY_RO_TOKEN"])
    ldap_users = get_ldap_users()
    expired_invites = []
    obsolete_users = []
    for user in client.org_members():
        if user["expired"]:
            expired_invites.append(user)
            continue
        if user["pending"]:
            emails = [user["email"]]
        else:
            emails = [x["email"] for x in user["user"]["emails"]]
        if all(email not in ldap_users for email in emails):
            obsolete_users.append(user)
    expired_invites.sort(key=itemgetter("email"))
    obsolete_users.sort(key=itemgetter("email"))
    print("User ID    Expired invites")
    print_users(expired_invites)
    print(
        "\n{:<10} {:<40} {}".format("User ID", "Sentry users not in LDAP", "Last login")
    )
    print_users(obsolete_users)


if __name__ == "__main__":
    load_dotenv()
    main()
