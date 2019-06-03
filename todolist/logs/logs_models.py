
from flask_table import Table, Col, DatetimeCol

###########################################
########  Forms
###########################################




###########################################
########  Tables
###########################################

class LogsTable(Table):
    #allow_sort = True #Done over javascript
    classes = ['table', 'logstable']
    html_attrs = {'id':'LogTable'}
    #html_attrs = {'id':'TaskTable'}

    id=Col('Id')
    task = Col('Task','task.name')
    user = Col('User','user.name')
    donetime = DatetimeCol('Done at')


class LogsFloatTable(Table):
    #allow_sort = True #Done over javascript
    classes = ['table', 'logstable']
    html_attrs = {'id':'LogTable'}
    #html_attrs = {'id':'TaskTable'}

    id=Col('Id')
    task = Col('Task','task.name')
    user = Col('User','user.name')
    donetime = DatetimeCol('Done at')
    value = Col('Val')

class CheckboxPlaceholder(Col):
    def td_format(self, item):
        return ""

class LogFloatPlotTable(Table):
    classes = ['table', 'logstable']
    html_attrs = {'id':'LogTable'}

    chk=CheckboxPlaceholder('','id')
    id=Col('Id','id')
    task = Col('Task','name')
    equipment = Col('Equipment','equipment.name')
    room = Col('Room','equipment.room.name')
