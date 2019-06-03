import sys
from . import db,cycletypes,logtypes
from .. import app
from datetime import datetime, date
from sqlalchemy import or_

PY3 = (sys.version_info[0] == 3)

if PY3:  # pragma: no cover
    string_types = str,  # pragma: no flakes
    text_type = str  # pragma: no flakes
else:  # pragma: no cover
    string_types = basestring,  # pragma: no flakes
    text_type = unicode # pragma: no flakes

class UserRoles(db.Model):
    __tablename__ = 'userroles'
    def __init__(self, facility_id, role_id):
        self.facility_id = facility_id
        self.role_id = role_id
    def __repr__(self):
        return '<UserRoles %d:%r:%r>' % (self.user_id,str(self.facility), str(self.role))
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    facility_id = db.Column(db.Integer(), db.ForeignKey('facility.id'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))

    facility = db.relationship('Facility')
    role = db.relationship('Role')

class UserTasks(db.Model):
    __tablename__ = 'usertasks'
    def __init__(self,task=None,priority=100):
        self.task=task
        self.priority=priority
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    task_id = db.Column(db.Integer(), db.ForeignKey('task.id'))
    priority = db.Column(db.Integer(), default = 100)
    task = db.relationship('Task')
    user = db.relationship('User')

class UserEquipment(db.Model):
    __tablename__ = 'userequipment'
    def __init__(self,Eq=None,priority=100):
        self.equipment=Eq
        self.priority=priority
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    equipment_id = db.Column(db.Integer(), db.ForeignKey('equipment.id'))
    priority = db.Column(db.Integer(), default = 100)
    equipment = db.relationship('Equipment')
    user = db.relationship('User')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(10),unique = True)
    nickname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    active = db.Column(db.Boolean())
    roles = db.relationship('UserRoles')
    usertasks = db.relationship('UserTasks')
    userequipment = db.relationship('UserEquipment')

    def __init__(self, username, nick, active=True):
        self.username = username
        self.nickname = nick
        self.active = active

    def __repr__(self):
        return '<User %r>' % self.username

    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.active

    @property
    def name(self):
        if self.nickname is not None and len(self.nickname)>0:
            return self.nickname
        else:
            return self.username

    def has_role(self, role):
        return any(ur.role.name == role for ur in self.roles)

    def has_roles(self, roles):
        for role in roles:
            if any(ur.role.name == role for ur in self.roles):
                return True
        return False

    """
    Role is a text,
    Facility is an instance
    """
    def has_department_role(self,facility,role):
        return any((ur.role.name == role and ur.facility_id==facility.id) for ur in self.roles)
        #return UserRoles.query.filter(User==self).filter(Facility.name==facility).filter(Role.name==role).first() is not None

    def departments_with_role(self,role):
        return (ur.facility for ur in self.roles if ur.role.name == role)
        #return UserRoles.query.filter(User==self).filter(Role.name==role).all()

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def get_tasklist(self):
        return Task.query.join(UserTasks).join(UserEquipment).join(User).\
                    filter(Task.active==True).\
                    filter(UserTasks.user_id==User.id).\
                    filter(UserEquipment.user_id==User.id).\
                    filter(or_(Task.id==UserTasks.id,Tasks.equipment_id==UserEquipment.equipment_id))




class Facility(db.Model):
    __tablename__ = 'facility'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True)

    def __init__(self,name=''):
        self.name=name
    def __repr__(self):
        return '<Facility %r>' % self.name
    def __str__(self):
        return self.name
    def MayAdmin(self, user, role='Admin'):
        return Facility.query.join(UserRoles).join(Role).\
                    filter(Facility.id==self.id).\
                    filter(UserRoles.user_id==user.id).\
                    filter(Role.name==role).one_or_none()\
                is not None;

    def AllMayAdmin(user,role='Admin'):
        return Facility.query.join(UserRoles).join(Role).\
                    filter(UserRoles.user_id==User.id).\
                    filter(Role.name==role).order_by('id').all()

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    room_id = db.Column(db.Integer(), db.ForeignKey('room.id'))
    room = db.relationship('Room', uselist=False)
    facility_id = db.Column(db.Integer(), db.ForeignKey('facility.id'))
    facility = db.relationship('Facility', uselist=False)

    def __init__(self,name=None,room=None,facility=None):
        self.name=name
        self.room=room
        self.facility=facility
    def __repr__(self):
        return '<Eq %r>' % self.name
    def __str__(self):
        return self.name+' ['+ self.facility.name+':'+ self.room.name+']'
    def MayAdmin(self, user, role='Admin'):
        return Equipment.query.join(Facility).join(UserRoles).join(Role).\
                    filter(Equipment.id==self.id).\
                    filter(UserRoles.user_id==user.id).\
                    filter(Role.name==role).one_or_none()\
                is not None;

    def AllMayAdmin(user, role='Admin'):
        return Equipment.query.join(Facility).join(UserRoles).join(Role).\
                    filter(UserRoles.user_id==user.id).\
                    filter(Role.name==role).order_by(Equipment.id.desc()).all()

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True)
    descr = db.Column(db.String(255))

    def __init__(self,name,descr):
        self.name=name
        self.descr=descr
    def __repr__(self):
        return '<Role %r>' % self.name
    def __str__(self):
        return self.name
    def __eq__(self, other):
        return (self.name == other or
        self.id == getattr(other, 'id', None))
    def __ne__(self, other):
        return not self.__eq__(other)
    def __hash__(self):
        return hash(self.name)


class Room(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)

    def __init__(self,room=''):
        self.name=room
    def __repr__(self):
        return 'Room %r' % self.name

class TaskLog(db.Model):
    __tablename__ = 'tasklog'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer(), db.ForeignKey('task.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    donetime = db.Column(db.DateTime(), default = datetime.now())

    user =  db.relationship('User')
    task =  db.relationship('Task')

    def __init__(self,task_id,user,value=None,donetime=None):
        self.task_id=task_id
        self.user_id=user.id
        self.donetime=donetime or datetime.now()

class TaskLogFloat(db.Model):
    __tablename__ = 'task_log_float'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer(), db.ForeignKey('task.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    donetime = db.Column(db.DateTime(), default = datetime.now())
    value = db.Column(db.Float())

    user =  db.relationship('User')
    task =  db.relationship('Task')

    def __init__(self, task_id, user, value, donetime=None):
        print(task_id, user, value, donetime)
        self.task_id=task_id
        self.user_id=user.id
        self.value=value
        self.donetime=donetime or datetime.now()

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(256))
    active = db.Column(db.Boolean())
    equipment_id = db.Column(db.Integer(), db.ForeignKey('equipment.id'))
    equipment = db.relationship('Equipment', uselist=False)
    priority = db.Column(db.Integer())
    logging = db.Column(db.Integer(), default=0)
    text = db.relationship('TaskText', uselist=False)
    cycle = db.Column(db.Integer(), default=7)
    cycletype = db.Column(db.Integer(), default=1)
    #Calculated due date
    ddate = db.Column(db.Date(), default=date.today())
    tasklog =  db.relationship('TaskLog')

    def __init__(self,name='',equipment=None,active=False,priority=100,logging=0):
        self.name=name
        self.equipment=equipment
        self.priority=priority
        self.active=active
        self.logging = logtypes.getkey(logging)
    def __repr__(self):
        return '<Task %s: %s>' % (str(self.id) , self.name)
    def CheckRole(self,user,role='Admin'):
        #if task not defined, enybody could edit it
        if self.equipment_id is None: return True
        fac_id=self.equipment.facility_id;
        if role=='Any':
            return any(ur.facility_id==fac_id for ur in user.roles)
        else:
            return any((ur.role.name == role and ur.facility_id==fac_id) for ur in user.roles)

    def Log(self, user, value, donetime=None):
        dblog=logtypes.getdbtype(self.logging)
        if dblog is None:
            return None;
        donetime = donetime or datetime.now()
        log=dblog(self.id, user, value, donetime)
        db.session.add(log)
        self.ddate=cycletypes.next(self.cycletype,self.cycle,donetime)
        db.session.commit()
        return log

    def Priority(self, atdate):
        priority=self.priority * cycletypes.get(self.cycletype).priority(atdate, self.ddate, self.cycle)
        if hasattr(self,'upriority'):
            priority=priority * self.upriority / 100
        return priority
    def SetUserPriority(self,upr):
        self.upriority=upr
        return self

#Request this by task ID as needed
class TaskText(db.Model):
    __tablename__ = 'tasktext'
    id = db.Column(db.Integer(),  db.ForeignKey('task.id'), primary_key=True)
    text = db.Column(db.Text)
    images = db.relationship('TaskImages')

class TaskImages(db.Model):
    def __init__(self, fname):
        self.filename=fname
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer(),  db.ForeignKey('tasktext.id'))
    filename = db.Column(db.String(256))
    keyword = db.Column(db.String(256))

    def __repr__(self):
        return '<TaskImages %d:%r:%r>' % (self.task_id,str(self.keyword), str(self.filename))
