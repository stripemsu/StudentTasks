# Tracking system for recurring tasks

Based on python, flask and SQLAlchemy. Tested with Postgres in production. Does not have any specific database-related hooks, so will work with MySQL and sqlite.

Please update config.py according to your requirements.

System does not store passwords, but authenticate its users over ldap directory.
However, as it initially been oriented to work in big organisation, user role should be added via web interface.

There are following roles in the system:
* Admin - can edit users and roles, audit tasks in own facility, create new facilities, and all below
* Supervisor - can edit task description and watch logs
* User - can mark tasks done
