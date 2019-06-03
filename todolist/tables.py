from flask import Markup, escape
from flask_table import LinkCol, Col
from flask_table.html import element
from datetime import datetime, date
from .database import cycletypes

class ModalIdBtnCol(LinkCol):
    def_args = {}
    def td_contents(self, item, attr_list):
        attrs = {'data-target':self.endpoint, 'data-myid':item.id,'type':"button",'class':"btn btn-info btn-xs",'data-toggle':"modal"}
        attrs.update(self.anchor_attrs)
        text = self.td_format(self.text(item, attr_list))
        return element('button',attrs=attrs, content=text, escape_content=False)

class IdBtnCol(LinkCol):
    def_args = {}
    def td_contents(self, item, attr_list):
        attrs = {'data-id':item.id,'type':"button",'class':"btn btn-info btn-xs {}".format(Markup.escape(self.endpoint))}
        attrs.update(self.anchor_attrs)
        text = self.td_format(self.text(item, attr_list))
        return element('button',attrs=attrs, content=text, escape_content=False)

class TaskTagCol(Col):
    def td_format(self, item):
        itemstr=str(escape(item))
        cntr=0
        finalstr=""
        while True:
            tagpos=itemstr.find('#',cntr)
            if tagpos==-1:break
            finalstr+=itemstr[cntr:tagpos]
            cntr=itemstr.find(' ',tagpos)
            if cntr==-1:
                tagstr=itemstr[tagpos:]
                cntr=len(itemstr)
            else:
                tagstr=itemstr[tagpos:cntr]
            finalstr+='<span class="label label-info">{}</span>'.format(tagstr)
        finalstr+=itemstr[cntr:]
        return Markup(finalstr)

class NameCol(Col):
    def td_format(self, item):
        return Markup.escape(item.name)

class TaskDaysLeftCol(Col):
    def td_contents(self, item, attr_list):
        return Markup.escape((item.ddate-date.today()).days)

class TaskCurrPriorityCol(Col):
    def td_contents(self, item, attr_list):
        return Markup.escape(int(item.Priority(date.today())))

class TaskDoneCol(Col):
    def_args = {}
    def __init__(self, name, endpoint, logendpoint, **kwargs):
        super(TaskDoneCol, self).__init__(name, **kwargs)
        self.logendpoint=logendpoint
        self.endpoint=endpoint

    def td_contents(self, item, attr_list):
        #item is Task
        elements=[]
        #add fire mark
        if date.today() >= item.ddate:
            #delayed
            if date.today() > cycletypes.next(item.cycletype,item.cycle,item.ddate):
                #delayed more then twice
                elements.append(element('span ',attrs={'class':'glyphicon glyphicon-fire gly-spin color-red'}))
            else:
                #delayed a bit
                elements.append(element('span ',attrs={'class':'glyphicon glyphicon-bell color-yellow'}))

        if item.logging==0:
            #No logging required, making just a link send via ajax
            attrs = {'data-id':item.id,'type':"button",'class':"btn btn-primary btn-xs {}".format(self.endpoint)}
            text = 'Done'
            elements.append(element('button',attrs=attrs, content=text, escape_content=False))
        else:
            #we should show modal window and collect data
            attrs = {'data-logid':item.id,'type':"button",'class':"btn btn-success btn-xs {}".format(self.logendpoint)}
            text = 'Log...'
            elements.append(element('button',attrs=attrs, content=text, escape_content=False))
        return ''.join(elements)
