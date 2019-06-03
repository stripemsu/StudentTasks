from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, BooleanField, SubmitField, SelectField, RadioField
from wtforms import validators
from todolist import db, app

from ..database import Facility, Room

from flask import url_for,Markup
from flask_table import Table, Col, BoolCol, ButtonCol, LinkCol
from ..tables import ModalIdBtnCol, NameCol

###########################################
########  Forms
###########################################  

class UserEditForm(FlaskForm):
    nickname = TextField('User Nickname', [validators.InputRequired()])    
    submit = SubmitField("Update")
    
class UserAddForm(FlaskForm):
    username = TextField('TXState ID', [validators.Length(min=2, max=10,message='2')])
    nickname = TextField('User Nickname')    
    submit = SubmitField("Add")

class UserAddRole(FlaskForm):
    facility = SelectField('Facility', choices=[], coerce=int, validators=[validators.Required()])
    role = SelectField('Role', choices=[], coerce=int, validators=[validators.Required()])
    submit = SubmitField("Add role")

class UserRemoveRole(FlaskForm):
    role = RadioField('Roles', choices=[], coerce=int, validators=[validators.Required()])
    submit = SubmitField("Remove role")

class FacilityEditForm(FlaskForm):
    name = TextField('Facility', [validators.InputRequired()])    
    submit = SubmitField("Save")
    id=-1
    formname='Facility'
    formaction=None
    def fieldslst(self):
        yield self.name

class RoomEditForm(FlaskForm):
    name = TextField('Room', [validators.InputRequired()])    
    submit = SubmitField("Save")
    id=-1
    formname='Room'
    formaction=None
    def fieldslst(self):
        yield self.name

class EquipmentEditForm(FlaskForm):
    name = TextField('Equipment', [validators.InputRequired()])    
    room_id = SelectField('Room', choices=[], coerce=int, validators=[validators.Required()])
    facility_id = SelectField('Facility', choices=[], coerce=int, validators=[validators.Required()])
    submit = SubmitField("Save")
    id=-1
    formname='Room'
    formaction=None
    def fieldslst(self):
        yield self.name
        yield self.room_id
        yield self.facility_id
        
    def fillChoices(self,user):
        self.facility_id.choices=[(f.id, f.name) for f in Facility.AllMayAdmin(user)]
        self.room_id.choices=[(room.id, room.name) for room in Room.query.all()]
    

###########################################
########  Tables
########################################### 

class RolesCol(Col):
    def td_format(self, content):
        roles=[]
        for role in content:
            roles.append(role.facility.name+' : '+role.role.name)
        return '<br>'.join(roles)
            
class UserTable(Table):
    allow_sort = True
    classes = ['table', 'usertable']
    
    id=Col('id')
    username=Col('TXState ID')
    link=ButtonCol('Edit', 'admin.useredit', url_kwargs=dict(id='id'))
    nickname=Col('Name')
    email=Col('e-mail')
    roles=RolesCol('Roles')
    active=BoolCol('Active')

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction =  'desc'
        else:
            direction = 'asc'
        return url_for('admin.home', sort=col_key, direction=direction)    

class FacilitiesTable(Table):
    classes = ['table']
    id=Col('id')
    name=Col('Facility')
    btn=ModalIdBtnCol('Edit', '#ModalEdit')

class RoomsTable(Table):
    classes = ['table']
    id=Col('id')
    name=Col('Room')
    btn=ModalIdBtnCol('Edit','#ModalEdit')
    
class EquipmentTable(Table):
    classes = ['table']
    id=Col('id')
    name=Col('Equipment')
    room=NameCol('Room')
    facility=Col('Facility')
    btn=ModalIdBtnCol('Edit','#ModalEdit')
