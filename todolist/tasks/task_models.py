from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import TextField, BooleanField, TextAreaField, SelectField, SubmitField,\
                    IntegerField, DateField, validators, FloatField, HiddenField
from wtforms.validators import InputRequired, DataRequired, Length, Optional
from todolist import db, app
from datetime import date,datetime,timedelta

# import things
from flask import url_for, Markup
from flask_table import Table, Col, BoolCol, ButtonCol, LinkCol, DateCol, OptCol
from ..tables import NameCol, TaskDoneCol, IdBtnCol, TaskTagCol, TaskCurrPriorityCol, TaskDaysLeftCol
from ..database import Equipment, cycletypes, logtypes, UserEquipment, UserTasks

def LastWeekDate(day):
    return day+timedelta(days=6-day.weekday())

###########################################
########  Forms
###########################################

class TaskEditForm(FlaskForm):

    name = TextField('Task name', [DataRequired(),Length(min=4,max=256)])
    #text = TextAreaField('Task text', [Optional()])
    active = BooleanField('Active', [Optional()])
    equipment_id = SelectField('Equipment',[DataRequired()], choices=[], coerce=int )
    priority = IntegerField('Priority',[DataRequired()] )
    cycle = IntegerField('Cycle',[DataRequired()] )
    cycletype = SelectField('Cycle type',[DataRequired()], choices=cycletypes.field_choices(), coerce=int )
    logging = SelectField('Log value',[Optional()], choices=logtypes.field_choices(), coerce=int )
    ddate = DateField('Due date (Y-m-d)', format='%Y-%m-%d')

    id=-1
    formname='Task'
    idfield = 'id-active' #'id', 'id-active'
    def fieldslst(self):
        yield self.name
        yield self.equipment_id
        yield self.priority
        yield self.cycletype
        yield self.cycle
        yield self.logging
        yield self.ddate

    def buttons(self):
        yield ("BackBtn",'↩ Back', 'info')
        yield ("SaveBtn","Save")
        yield ("ReloadTaskBtn","Reload",'warning')

    def fillChoices(self,user):
        self.equipment_id.choices=list((eq.id,eq.name) for eq in Equipment.AllMayAdmin(user))
        if self.ddate.data==None:self.ddate.data=date.today()

class TaskTextEditForm(FlaskForm):
    text = TextAreaField('Task text', [Optional()], default='', render_kw={'rows':'12'})

    id=-1
    formname='Task text'
    idfield = 'no' #'id', 'id-active'

    def fieldslst(self):
        yield self.text
    def buttons(self):
        yield ("BackBtn",'↩ Back', 'info')
        yield ("ViewTextBtn","View")
        yield ("SaveTextBtn","Save")
        yield ("ReloadTextBtn","Reload",'warning')

class ImageUploadForm(FlaskForm):
    image = FileField(validators=[FileRequired()])

class PickUserForm(FlaskForm):
    usersfield=SelectField('User to bind',choices=[])
    priority=IntegerField('Set priority',default=100)

class TaskLogForm(FlaskForm):
    value=FloatField('Float value to log',[InputRequired()])


###########################################
########  Tables
###########################################

class AllTasksTable(Table):
    #allow_sort = True #Done over javascript
    classes = ['table', 'taskstable']
    html_attrs = {'id':'TaskTable'}
    order = 6 #colomn number to order by, first col is 0

    id=Col('Id')
    link=IdBtnCol('More','TaskDesc')
    name=TaskTagCol('Task')
    #active=BoolCol('Active')
    equipment=NameCol('Equipment')
    room=NameCol('Room', attr='equipment.room')
    daysleft=TaskDaysLeftCol('Days left', th_html_attrs={'class':'col-md-1'})
    Priority=TaskCurrPriorityCol('Priority')
    #cycle=Col('Cycle')
    mark=TaskDoneCol('Mark','TaskDone','TaskLog') #,td_html_attrs={'id':'#TaskMark'}
    #ddate=DateCol('Due date')

class AdmTasksTable(Table):
    #allow_sort = True #Done over javascript
    classes = ['table', 'taskstable', 'admin']
    html_attrs = {'id':'TaskTable'}

    id=Col('Id')
    active=BoolCol('Active')
    equipment=NameCol('Equipment',th_html_attrs={'class':'col-md-2'})
    name=TaskTagCol('Task',th_html_attrs={'class':'col-md-3'})
    priority=Col('Priority')
    facility=Col('Facility',attr_list=['equipment','facility'],th_html_attrs={'class':'col-md-1'})
    cycle=Col('Ccl')
    cycletype = OptCol('CType', th_html_attrs={'class':'col-md-1'}, choices=cycletypes.table_choices())
    logging = OptCol('Logging', th_html_attrs={'class':'col-md-1'}, choices=logtypes.table_choices())
    link=LinkCol('Edit','tasks.edit',url_kwargs=dict(id='id'),th_html_attrs={'class':'col-md-1'})
    ddate=DateCol('DueDate',th_html_attrs={'class':'col-md-1'})

class TableIconCol(OptCol):
    def td(self, item, attr):
        itemid=None
        if type(item)==dict:
            itemid=item['id'];
        else:
            itemid=item.id;
        self.td_html_attrs.update({'data-myid':itemid,'id':'ToggleBtn'})
        return super().td(item, attr)
    def td_format(self, content):
        #Content could be UserEquipment or UserTasks
        if content == None:
            return '<span class="glyphicon glyphicon-ban-circle" aria-hidden="true"></span>'
        if isinstance(content,str):
            if content == 'N':
                return '<span class="glyphicon glyphicon-unchecked" aria-hidden="true"></span>'
            elif content == 'E':
                return '<span class="glyphicon glyphicon-scale color-grey" aria-hidden="true"></span>'
            elif content == 'F':
                return '<span class="glyphicon glyphicon-ban-circle" aria-hidden="true"></span>'
            else:
                return '<span class="glyphicon glyphicon-link" aria-hidden="true"></span>'
        if isinstance(content,UserEquipment):
            return '<span class="glyphicon glyphicon-scale color-green" aria-hidden="true"></span> %i'%content.priority
        if isinstance(content,UserTasks):
            return '<span class="glyphicon glyphicon-ok-circle color-green" aria-hidden="true"></span> %i'%content.priority

class EqBindTable(Table):
    classes = ['table', 'table-hover', 'admin' ]
    id=Col('id')
    bind=TableIconCol('Bind')
    equipment=Col('Equimpent')
    facility=Col('Facility')
    room=Col('Room')

class TaskBindTable(Table):
    classes = ['table', 'taskstable']
    html_attrs = {'id':'TaskTable'}
    id=Col('id')
    bind=TableIconCol('Bind')
    task=Col('Task')
    equipment=Col('Equimpent')
    facility=Col('Facility')
    room=Col('Room')
