from flask import render_template
from flask import jsonify, request, abort
import json
#from .. import app, db
from . import logs
from ..auth import current_user
from .logs_models import LogsTable, LogsFloatTable, LogFloatPlotTable
from ..database import TaskLog, TaskLogFloat, Task,Equipment,Room,Facility,UserRoles


@logs.route('/logs')
def home():
    return done_tbl()

@logs.route('/logs/done')
def done_tbl():

    TaskLogsTbl=LogsTable(TaskLog.query.all())
    Name='donetbl'
    return render_template('logs/logs_tbl.html',page='logs', name=Name, \
        LogTbl=TaskLogsTbl)

@logs.route('/logs/float')
def float_tbl():

    TaskFloatTbl=LogsFloatTable(TaskLogFloat.query.all())
    Name='floattbl'
    return render_template('logs/logs_tbl.html',page='logs', name=Name, \
        LogTbl=TaskFloatTbl)

@logs.route('/logs/plot')
def float_plot():
    FloatLogsData=Task.query.filter(Task.active==True).join(TaskLogFloat)\
        .join(Equipment).join(Room)\
        .join(Facility).join(UserRoles)\
        .filter(UserRoles.user_id==current_user.id).all()

    FloatLogsTbl=LogFloatPlotTable(FloatLogsData)

    Name='floatplot'
    return render_template('logs/logs_plot.html',page='logs', name=Name,
        FloatLogsTbl=FloatLogsTbl)

@logs.route('/logs/api')
def api():
    TaskIds=[]
    tasks=request.args.get('tasks', 'err')
    try:
        tasks=json.loads(tasks)
        for t in tasks:
            TaskIds.append(int(t))
    except:
        abort(400)

    TList=Task.query.filter(Task.active==True).join(Equipment)\
        .join(Facility).join(UserRoles)\
        .filter(UserRoles.user_id==current_user.id)\
        .filter(Task.id.in_(TaskIds))\
        .all()

    plotdata=[]

    for tsk in TList:
        tskplot={"name":"{}: {}".format(tsk.equipment.name,tsk.name)}
        logdata=TaskLogFloat.query.filter(TaskLogFloat.task_id==tsk.id).all()
        dates=[fl.donetime for fl in logdata]
        vals =[fl.value for fl in logdata]
        plot=[[fl.donetime,fl.value] for fl in logdata]
        tskplot["data"]=plot
        tskplot["minx"]=min(dates)
        tskplot["maxx"]=max(dates)
        tskplot["miny"]=min(vals)
        tskplot["maxy"]=max(vals)

        plotdata.append(tskplot)

    return jsonify(plotdata)
