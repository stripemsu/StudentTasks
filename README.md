# Tracking system for recurring tasks

Based on python, flask and SQLAlchemy. Tested with Postgres in production. Does not have any specific database-related hooks, so will work with MySQL and sqlite.

Please update config.py according to your requirements.

System does not store passwords, but authentificate its users over ldap directory.
However, as it initially been oriented to work in big organisation, user role shoud be added via web interfase.

There are followin roles in the system:
* Admin - can edit users and roles, adit tasks in own facility, create new facilities, and all below
* Supervisor - can edit task description and waatch logs
* User - can mark tasks done
