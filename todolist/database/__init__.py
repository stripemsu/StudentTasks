from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

from .dbscript import ccltypes, dblogtypes 
cycletypes = ccltypes()
logtypes = dblogtypes()

from .dbmodel import *

logtypes.AddType(0,'None',TaskLog)
logtypes.AddType(1,'Float',TaskLogFloat)

from .refill import refill_db
