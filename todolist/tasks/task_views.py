from flask import render_template, flash, redirect, url_for, request, abort
from flask_misaka import markdown
from datetime import date
from .. import app, db
from ..auth import current_user, role_required
from . import tasks
from ..database import Task, Room, logtypes, cycletypes, User, UserTasks, UserEquipment, \
                        Equipment, Facility, UserRoles
from .task_models import AllTasksTable, TaskLogForm, LastWeekDate
from . import tasks


@tasks.route('/tasks')
def home():
    tasktype=request.args.get('tsk', 'my') #all, my
    ddtype=request.args.get('dd', 'dd') #DD - duedate, all - all

    wday=LastWeekDate(date.today())
    if tasktype=='all':
        #all tasks user have any access
        tqry = Task.query.filter(Task.active==True).join(Equipment).join(Facility).join(UserRoles).\
                        filter(UserRoles.user_id==current_user.id)
        if ddtype!='all':
            # dd if not all
            tqry = tqry.filter(Task.ddate<=wday)
        tbl=AllTasksTable(tqry.all())
    elif tasktype=='my':
        #Subquery, UserTasks filter they are not in userequipment_table
        # all equipment_is's for current user
        ut_id_sqry = db.session.query(UserEquipment.equipment_id).filter(UserEquipment.user_id==current_user.id)
        tqry_ue = db.session.query(Task,UserEquipment.priority).filter(Task.active==True).join(Equipment).join(UserEquipment).filter(UserEquipment.user_id==current_user.id)
        tqry_ut = db.session.query(Task,UserTasks.priority).filter(Task.active==True).join(UserTasks).filter(~Task.equipment_id.in_(ut_id_sqry)).filter(UserTasks.user_id==current_user.id)

        if ddtype!='all':
            # dd if not all
            tqry_ue=tqry_ue.filter(Task.ddate<=wday)
            tqry_ut=tqry_ut.filter(Task.ddate<=wday)

        tqry=tqry_ut.union(tqry_ue)
        tasks=[t[0].SetUserPriority(t[1]) for t in tqry.all()]
        tbl=AllTasksTable(tasks)
    else:
        flash("Invalid request",'danger')
        return redirect(url_for('tasks.home'))



    return render_template('tasks/tasks_list.html',page='tasks',table=tbl)

@tasks.route('/tasks/popup', methods=['GET','POST'])
def taskpopup():
    #Check if user have access to the task first!
    try:
        taskid = int(request.args.get('id'))
    except:
        flash("Invalid request",'danger')
        return redirect(url_for('tasks.admin'))

    task=Task.query.get(taskid)
    text=task.text
    if task is None:
        flash('Unknown task','warning')
        return redirect(url_for('tasks.admin'))

    if text is None:
        tasktext='No description avaliable.'
    else:
        tasktext=text.text
        for img in text.images:
            tasktext+='\n['+img.keyword+']: '+ url_for('image_files', filename=str(text.id)+'/'+img.filename)

    #All users for this task
    taskusers={}

    ut=UserTasks.query.filter(UserTasks.task_id==task.id).all()
    taskusers.update({u.user.name:u.priority for u in ut})

    ue=UserEquipment.query.filter(UserEquipment.equipment_id==task.equipment_id).all()
    taskusers.update({u.user.name:u.priority for u in ue})

    usrstr=', '.join(["{} [{}]".format(u,p) for (u,p) in taskusers.items()])


    view={'title':task.name,
    'content':markdown(tasktext)
    }

    #details list
    view['details']=[
            ('id',str(task.id)),
            ('equipment',str(task.equipment.name)),
            ('facility',str(task.equipment.facility.name)),
            ('priority',str(task.priority)),
            ('logging',logtypes(task.logging)),
            ('cycle',str(task.cycle)+' '+cycletypes(task.cycletype).tblname),
            ('Due date',str(task.ddate)),
            ('Users',usrstr)
        ]

    return render_template('tasks/task_ajax.html',view=view)


@tasks.route('/tasks/taskdone', methods=['POST'])
def taskdone():
    #Check if user have access to the task first!
    try:
        taskid = int(request.args.get('id'))
    except:
        abort(400)

    task=Task.query.get(taskid)

    if not task.CheckRole(current_user,'Any'):
        #User have no permission on task facility
        #Anybody on facility could do any task, even they not binded to it
        # but does not mean task will show on the list to anybody
        abort(403)

    log=task.Log(current_user,None)

    if log is None:
        abort(500)

    return render_template('tasks/task_done.html')

@tasks.route('/tasks/tasklog', methods=['GET','POST'])
def tasklog():
    #Check if user have access to the task first!
    try:
        taskid = int(request.args.get('id'))
    except:
        print('Bad ID')
        abort(400)

    task=Task.query.get(taskid)

    if not task.CheckRole(current_user,'Any'):
        #User have no permission on task facility
        #Anybody on facility could do any task, even they not binded to it
        # but does not mean task will show on the list to anybody
        abort(403)

    form=TaskLogForm()

    if form.validate_on_submit():
        log=task.Log(current_user,form.value.data)
        if log is not None:
            #201 Created - success - return glif for button
            return render_template('tasks/task_done.html'), 201
        else:
            form.value.errors.append('Database access error')

    #If not post or error in post - act as get, return form
    view={
        'title':task.name,
        'id':taskid
    }
    print('tasklog:get')
    return render_template('tasks/task_ajax_log.html',view=view,form=form)
