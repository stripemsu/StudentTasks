import os
from flask import render_template, flash, redirect, url_for, request
from flask_misaka import markdown
from .. import app, db
from ..auth import current_user, roles_required
from werkzeug.utils import secure_filename
from wtforms import SelectField
from ..database import Task, Room, TaskText, Equipment, User, Facility, TaskImages, UserRoles, Role, UserEquipment, UserTasks
from .task_models import AdmTasksTable, EqBindTable, TaskBindTable, \
                TaskEditForm, TaskTextEditForm, PickUserForm, TableIconCol
from . import tasks

@tasks.route('/tasks/admin')
@roles_required('Admin','Supervisor') #Any of
def admin():
    query = Task.query.join(Equipment).join(Facility)
    #query = db.session.query(Task,Facility).join(Equipment).join(Facility)

    tbl=AdmTasksTable(query.all())
    return render_template('tasks/tasks_list.html',page='Admin',table=tbl)

@tasks.route('/tasks/admin/edit',methods=['GET','POST'])
@roles_required('Admin','Supervisor')
def edit():
    try:
        itemid = int(request.args.get('id', -1))
    except:
        flash("Invalid request",'danger')
        return redirect(url_for('tasks.admin'))
    item=None;text=None;form=None

    if itemid>=0:
        item=Task.query.get(itemid)
    if item is None: item=Task()
    text=item.text
    if text is None: text=TaskText()

    #If user is Admin, and can edit current task
    if item.CheckRole(current_user):
        if request.values.get('form',None)=='task':
            form = TaskEditForm(obj=item)
            form.fillChoices(current_user)
            #do not care if it was submitted, or if form valid
            #user have permissions to see it
            btn=request.values.get('submit',None)
            if btn == 'BackBtn':
                return redirect(url_for('tasks.admin'))
            elif btn == 'ReloadTaskBtn':
                form = TaskEditForm({},obj=item)
                form.fillChoices(current_user)
                form.id=itemid
            #Been is submitted
            elif form.validate_on_submit():
                if btn == 'SaveBtn' and form.validate():
                    if item.id is None:
                        form.populate_obj(item)
                        db.session.add(item)
                        db.session.commit()
                        itemid=item.id
                    form.populate_obj(item)
                    form.id=itemid
                    db.session.commit()
                    form.fillChoices(current_user)
                    flash('Data saved','success')
        else:
            form = TaskEditForm({},obj=item)
            form.fillChoices(current_user)
            form.id=itemid
    else:
        form=None
    #endif
    #If user is Admin or just a Supervisor, he could edit task text & images
    #others could not get into the method

    if request.values.get('form',None)=='text':
        textform = TaskTextEditForm(obj=text)
        #been is_submitted()
        if textform.validate_on_submit():
            btn=request.values.get('submit',None)
            if btn == 'BackBtn':
                return redirect(url_for('tasks.admin'))
            elif btn == 'ViewTextBtn':
                pass;
            elif btn == 'SaveTextBtn':
                if text.id is None:
                    text.id=itemid
                    db.session.add(text)
                textform.populate_obj(text)
                db.session.commit()
                flash('Text saved','success')
            elif btn == 'ReloadTextBtn':
                textform = TaskTextEditForm({},obj=text)
    else:
        #Not this form submitted
        textform = TaskTextEditForm({},obj=text)

    textform.id=itemid
    #end of task text

    #If text.id is not none, it exists in db and we can work with images
    images=None
    mdtext=textform.text.data or ''
    if text.id is not None:
        #print(list(text.images))
        images=[]
        #task images
        for img in text.images:
            images.append((img.keyword,img.filename))
            mdtext+='\n['+img.keyword+']: '+ url_for('image_files', filename=str(text.id)+'/'+img.filename)
            #print(url_for('image_files', filename=str(text.id)+'/'+img.filename))

    #end of task images
    view={  'id':str(itemid),
            'name':item.name if item is not None else 'New Task',
            'text':markdown(mdtext),
            'images':images
    }

    return render_template('tasks/tasks_edit.html',page='Admin',form=form,textform=textform,view=view)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['jpg','jpeg','png']

@tasks.route('/tasks/admin/imgupload',methods=['POST'])
@roles_required('Admin','Supervisor')
def imgupload():
    try:
        itemid = int(request.args.get('id', -1))
    except:
        flash("Invalid request",'danger')
        return redirect(url_for('tasks.admin'))

    if 'image' not in request.files:
        flash('No file part','danger')
        return redirect(url_for('tasks.edit',id=itemid))
    formfile = request.files['image']
    if not formfile:
        flash('Strange file upload error','danger')
        return redirect(url_for('tasks.edit',id=itemid))
    if formfile.filename == '':
        flash('No selected file','danger')
        return redirect(url_for('tasks.edit',id=itemid))
    if not allowed_file(formfile.filename):
        flash('File not allowed','warning')
        return redirect(url_for('tasks.edit',id=itemid))

    item=None;text=None
    if itemid>=0:
        item=Task.query.get(itemid)
        text=TaskText.query.get(itemid)
    if itemid<0 or text is None:
        flash("Error. Save data before uploading files",'warning')
        return redirect(url_for('tasks.edit'))

    formfname = secure_filename(formfile.filename)

    fdir = os.path.join(app.config['IMAGE_FOLDER'],str(itemid))
    try:
        os.mkdir(fdir)
    except OSError:
        pass;

    f = os.path.join(app.config['IMAGE_FOLDER'],str(itemid), formfname)
    #overwrite file if exists
    try:
        os.remove(f)
    except OSError:
        pass;
    formfile.save(f)

    nImg=None
    nImglink = request.values.get('imglink', None)

    for img in text.images:
        if img.filename == formfname:
            nImg=img;
            #print('DBG file found: ',formfname)
            break;
    if nImg is None:
        nImg=TaskImages(formfname)
        text.images.append(nImg)

        #print('DBG new file: ',formfname)

    imgkw=set()
    for img in text.images:
        imgkw.add(img.keyword)

    if nImglink in imgkw:
        flash('Keyword not unique. Using default.','warning')
        nImglink=None

    if nImglink is None or nImglink=='':
        i=1;
        while('img'+str(i) in imgkw):i+=1
        nImglink='img'+str(i)

    nImg.keyword=nImglink
    db.session.commit()

    flash('File "'+formfname+'" uploaded successfully.','success')
    return redirect(url_for('tasks.edit',id=itemid))

####################################################################
####################################################################
class vGiveViewData:
    name=''
    def __init__(self,name):
        self.name=name

# View page
@tasks.route('/tasks/admin/usereq',methods=['GET'])
@roles_required('Admin')
def userequipment():
    view=vGiveViewData('User to Equipment')

    #Make drop-down with list of users you can admin
    admrole = db.aliased(UserRoles)
    query = User.query.join(UserRoles).join(Facility).join(admrole).join(Role).\
                filter(admrole.user_id==current_user.id).\
                filter(Role.name=='Admin')

    #Make list of users you may admin
    view.pickuser=PickUserForm()
    view.pickuser.usersfield.choices=[(u.id,u.name) for u in query.all()]

    #Make equipment table for selected user (first one)
    view.table=EqBindTable(eqmarks(view.pickuser.usersfield.choices[0][0]))
    view.ajaxtable = url_for('tasks.userequipment_table')
    view.ajaxtoggle = url_for('tasks.userequipment_toggle')
    return render_template('tasks/tasks_give.html',page='Admin',view=view)


@tasks.route('/tasks/admin/usertsk',methods=['GET','POST'])
@roles_required('Admin')
def usertask():
    view=vGiveViewData('User to Task')

    #Make drop-down with list of users you can admin
    admrole = db.aliased(UserRoles)
    query = User.query.join(UserRoles).join(Facility).join(admrole).join(Role).\
                filter(admrole.user_id==current_user.id).\
                filter(Role.name=='Admin')

    #Make list of users you may admin
    view.pickuser=PickUserForm()
    view.pickuser.usersfield.choices=[(u.id,u.name) for u in query.all()]

    #Make tasks table for selected user (first one)
    view.table=TaskBindTable(taskmarks(view.pickuser.usersfield.choices[0][0]))

    view.ajaxtable = url_for('tasks.usertask_table')
    view.ajaxtoggle = url_for('tasks.usertask_toggle')

    return render_template('tasks/tasks_give.html',page='Admin',view=view)

# Table formatting function

def eqmarks(user_id):
    #selected for user
    UserEq=UserEquipment.query.filter(UserEquipment.user_id==user_id).all()
    UserEqDict={e.equipment_id:e for e in UserEq} #dict id:UserEquipment

    admrole = db.aliased(UserRoles)
    Eq=Equipment.query.join(Facility).join(UserRoles).join(admrole).join(Role).\
                    filter(UserRoles.user_id==user_id).\
                    filter(admrole.user_id==current_user.id).\
                    filter(Role.name=='Admin')

    return [   {'id':e.id,
                'bind': UserEqDict.get(e.id,'N'),
                'equipment':e.name,
                'facility':e.facility.name,
                'room':e.room.name }
               for e in Eq.all()
            ]

def taskmarks(user_id):
    #selected for user - via Equipment
    UserEqTask=db.session.query(Task.id).join(Equipment).join(UserEquipment).filter(UserEquipment.user_id==user_id)
    #eq_task=[t.id for t in UserEqTask] #list of Task id via UserEquipment
    #print(UserEqTask.all())
    eq_task=list(t[0] for t in UserEqTask.all())

    #UserTasks selected for user
    UserTsks=UserTasks.query.filter(UserTasks.user_id==user_id).all()
    u_task={t.task_id:t for t in UserTsks}

    admrole = db.aliased(UserRoles)
    Tasks=Task.query.join(Equipment).join(Facility).join(UserRoles).join(admrole).join(Role).\
                filter(Task.active==True).\
                filter(UserRoles.user_id==user_id).\
                filter(admrole.user_id==current_user.id).\
                filter(Role.name=='Admin').all()

    bnd=lambda task: 'E' if task.id in eq_task else u_task.get(task.id, 'N')

    return [   {'id':t.id,
                'bind': bnd(t),
                'task': t.name,
                'equipment':t.equipment.name,
                'facility':t.equipment.facility.name,
                'room':t.equipment.room.name }
               for t in Tasks
            ]

# Table AJAX
@tasks.route('/tasks/admin/usereqtbl',methods=['GET','POST'])
@roles_required('Admin')
def userequipment_table():
    try:
        userid = int(request.args.get('user', None))
    except:
        flash("Invalid request",'danger')
        return redirect(url_for('tasks.userequipment'))

    #Check we can admin this user
    admrole = db.aliased(UserRoles)
    query = User.query.join(UserRoles).join(Facility).join(admrole).join(Role).\
                filter(User.id==userid).\
                filter(admrole.user_id==current_user.id).\
                filter(Role.name=='Admin')
    if query.one_or_none() is None:
        flash("Invalid request",'danger')
        return redirect(url_for('tasks.userequipment'))

    table=EqBindTable(eqmarks(userid))
    return render_template('tasks/tasks_giveajax.html',data=table)

@tasks.route('/tasks/admin/usertsktbl',methods=['GET','POST'])
@roles_required('Admin')
def usertask_table():
    try:
        userid = int(request.args.get('user', None))
    except:
        flash("Invalid request",'danger')
        return redirect(url_for('tasks.userequipment'))

    #Check we can admin this user
    admrole = db.aliased(UserRoles)
    query = User.query.join(UserRoles).join(Facility).join(admrole).join(Role).\
                filter(User.id==userid).\
                filter(admrole.user_id==current_user.id).\
                filter(Role.name=='Admin')
    if query.one_or_none() is None:
        flash("Invalid request",'danger')
        return redirect(url_for('tasks.usertask'))

    table=TaskBindTable(taskmarks(userid))
    return render_template('tasks/tasks_giveajax.html',data=table)

#Toggle AJAX

@tasks.route('/tasks/admin/usereqtgl',methods=['GET','POST'])
@roles_required('Admin')
def userequipment_toggle():
    try:
        userid = int(request.args.get('user', None))
        lineid = int(request.args.get('line', None))
        prior = int(request.args.get('pr'))
    except:
        return TableIconCol.td_format(None, 'F')
    if userid is None or lineid is None:
        return TableIconCol.td_format(None, 'F')

    #Check we can admin this user
    admrole = db.aliased(UserRoles)
    userquery = User.query.join(UserRoles).join(Facility).join(admrole).join(Role).\
                filter(User.id==userid).\
                filter(admrole.user_id==current_user.id).\
                filter(Role.name=='Admin')
    TglUser=userquery.one_or_none()
    if TglUser is None:
        return TableIconCol.td_format(None, 'F')

    #Check we can admin this equipment
    Eq = Equipment.query.get(lineid)
    if Eq is None or not Eq.MayAdmin(current_user):
        return TableIconCol.td_format(None, 'F')

    ue=UserEquipment.query.filter(UserEquipment.user_id==TglUser.id).filter(UserEquipment.equipment_id==lineid).one_or_none()

    if ue is None:
        ue=UserEquipment(Eq,prior)
        TglUser.userequipment.append(ue)
        db.session.commit()
        return TableIconCol.td_format(None, ue)
    else:
        #remove
        db.session.delete(ue)
        db.session.commit()
        return TableIconCol.td_format(None, 'N')

@tasks.route('/tasks/admin/usertsktgl',methods=['GET','POST'])
@roles_required('Admin')
def usertask_toggle():
    try:
        userid = int(request.args.get('user', None))
        lineid = int(request.args.get('line', None))
        prior = int(request.args.get('pr'))
    except:
        return TableIconCol.td_format(None, 'F')
    if userid is None or lineid is None:
        return TableIconCol.td_format(None, 'F')

    #check this task not bind over equipment
    eqtask = Task.query.join(Equipment).join(UserEquipment).\
                filter(Task.id==lineid).\
                filter(UserEquipment.user_id==userid)
    if eqtask.one_or_none() is not None:
        #Keep grey equipment mark
        return TableIconCol.td_format(None, 'E')

    #Check we can admin this user
    admrole = db.aliased(UserRoles)
    userquery = User.query.join(UserRoles).join(Facility).join(admrole).join(Role).\
                filter(User.id==userid).\
                filter(admrole.user_id==current_user.id).\
                filter(Role.name=='Admin')
    TglUser=userquery.one_or_none()
    if TglUser is None:
        return TableIconCol.td_format(None, 'F')

    #Check we can admin this task
    task=Task.query.get(lineid)
    if task is None or not task.CheckRole(current_user):
        return TableIconCol.td_format(None, 'F')

    ut=UserTasks.query.filter(UserTasks.user_id==TglUser.id).filter(UserTasks.task_id==lineid).one_or_none()

    if ut is None:
        ut=UserTasks(task,prior)
        TglUser.usertasks.append(ut)
        db.session.commit()
        return TableIconCol.td_format(None, ut)
    else:
        #remove
        db.session.delete(ut)
        db.session.commit()
        return TableIconCol.td_format(None, 'N')
