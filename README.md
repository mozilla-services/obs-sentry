# obs-sentry

Scripts to help the Observability Team at Mozilla manage Sentry.

## Files

* `find_legacy_js_users.py` - list projects using an obsolete version of the JS SDK
  and their team admins
* `obsolete_users.py` - list users with expired invites, and users no longer at Mozilla
* `sentry_client.py` - module with a simple Sentry REST API client

## Running the scripts

The easiest way to run the scripts is using [`uv`][1], e.g.

     uv run obsolete_users.py

[1]: https://docs.astral.sh/uv/

## Environment variables

The scripts use these environment variables:

* `LDAP_BIND_USER` - bind user used for LDAP queries
* `SENTRY_RO_TOKEN` - a Sentry API token with read-only access
* `SENTRY_TOKEN` - a Sentry API token with read and write access

You can set these variables in `.env` in this directory.
