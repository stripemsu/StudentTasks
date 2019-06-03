from flask import render_template, flash, redirect, url_for, request
from .. import app, db
from ..auth import current_user
from . import admin
from ..database import User, UserRoles, Role, Facility, Room, Equipment
from .adm_models import UserEditForm, UserAddForm, UserAddRole, UserRemoveRole, FacilityEditForm, RoomEditForm, EquipmentEditForm, \
                        UserTable, FacilitiesTable, RoomsTable, EquipmentTable

@admin.route('/admin/users')
@admin.route('/admin/users/list')
def home():
    sort = request.args.get('sort', 'id')
    reverse = (request.args.get('direction', 'asc') == 'desc')

    if sort=='link' or sort == 'roles': sort='id'
    if reverse:
        query=User.query.order_by(sort+' desc')
    else:
        query=User.query.order_by(sort)
    
    tbl=UserTable(query.all(),sort_by=sort,sort_reverse=reverse)
    return render_template('admin/users_list.html',page='Admin',table=tbl)
    

@admin.route('/admin/user/edit', methods=['GET','POST'])
def useredit():
    try:
        userid = int(request.args.get('id'))
    except:
        flash("Invalid request",'danger')
        return redirect(url_for('home'))

    user = User.query.filter_by(id=userid).first()
    if user is None:
        flash("Invalid user",'danger')
        return redirect(url_for('home'))

    if request.values.get('submit') == 'Update':
        userform = UserEditForm(request.values)
        if not userform.validate():
            flash("Data is not valid",'danger')
        else:
            #update data
            user.nickname=userform.nickname.data
            db.session.commit()
            flash("User data updated. id=%d, netid: %s, nick: %s"%(user.id, user.username, user.nickname),'info')
    else:
        #New form
        userform = UserEditForm()
        userform.nickname.data = user.nickname

    #Add roles
    if request.values.get('submit') == 'Add role':
        roleform = UserAddRole(request.values)
    else:
        roleform = UserAddRole()

    #populate facility and roles list
    #current user should be facility admin to add users to the facility
    #for new form and validate purpose
    roleform.facility.choices=[]
    cu_roles=UserRoles.query.filter_by(user_id=current_user.id).filter(Role.name=='Admin').all()
    for role in cu_roles:
        roleform.facility.choices.append((role.facility_id, role.facility.name))
    roles=Role.query.all()
    roleform.role.choices=[]
    for role in roles:
        roleform.role.choices.append((role.id, role.name))
    
    if request.values.get('submit') == 'Add role':
        if not roleform.validate():
            flash("Data is not valid",'danger')
        else:
            #check if this role already exist
            urole=UserRoles.query.filter_by(user_id=user.id,role_id=roleform.facility.data,facility_id=roleform.role.data).first()
            if urole is not None:
                flash('User already have this role','warning')
            else:
                urole=UserRoles(roleform.facility.data,roleform.role.data)
                user.roles.append(urole)
                db.session.commit()
                flash("Role '%s' at facility '%s' been added"%(urole.role.name,urole.facility.name),'info')
                if not user.active:
                    user.active=True
                    db.session.commit()

    if request.values.get('submit') == 'Remove role':
        urolesform=UserRemoveRole(request.values)
    else:
        urolesform=UserRemoveRole()
    urolesform.role.choices=[]
    uroles=UserRoles.query.filter_by(user_id=user.id).all()
    urole=None #do not delete anything
    for role in uroles:
        urolesform.role.choices.append((role.id,role.facility.name+':'+role.role.name))
    if request.values.get('submit') == 'Remove role':
        if not urolesform.validate():
            flash("Data is not valid",'danger')
        else:
            # Check role exists, and delete it if it will not be None
            urole=UserRoles.query.filter_by(id=urolesform.role.data,user_id=user.id).first()
            if urole is None:
                flash("Data is not valid",'danger')
            #Check if you deleting Admin Role
            elif urole.role == 'Admin':
                count = UserRoles.query.filter_by(facility_id=urole.facility_id,role_id=urole.role_id).count()
                if count > 1:
                    flash("We counted %d admins in %s facility, So we could delete admin rights of user '%s'."%(count,urole.facility.name,user.name),'info')
                else:
                    flash("This is a last Admin in %s facility. We could not delete it."%urole.facility.name,'warning')
                    urole=None
            else:
                cu_role=UserRoles.query.filter_by(user_id=current_user.id,facility_id=urole.facility.id).filter(Role.name=='Admin').first()
                if cu_role is None:
                    flash("You have no permitt to delete this Role",'warning')
                    urole=None

        if urole is not None:
            db.session.delete(urole)
            db.session.commit()
            flash("Role removed",'info')
            urolesform.role.choices = [x for x in urolesform.role.choices if x[0] != urolesform.role.data]
            if len(urolesform.role.choices)==0:
                user.active=False
                db.session.commit()
                flash("User disabled",'info')
       
    return render_template('admin/users_edit.html',page='Admin',userdata=user,form=userform,roles=roleform,userroles=urolesform)

@admin.route('/admin/user/add', methods=['GET','POST'])
def useradd():
    if request.values.get('submit') == 'Add':
        form = UserAddForm(request.values)

        if not form.validate():
            flash("Data is not valid",'danger')
            return render_template('admin/users_add.html',form=form)
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash("User %s, id=%d, nick: %s already exist"%(user.username,user.id,user.nickname),'warning')
            return render_template('users_add.html',form=form)

        user = User(username=form.username.data, nick=form.nickname.data, active=False)
        print("adding User %s, nick: %s"%(user.username,user.nickname))
        db.session.add(user)
        db.session.commit()

        flash("User id=%d, netid: %s, nick: %s has been added."%(user.id, user.username, user.nickname),'info')
        print('User id',str(user.id),', net_id',str(user.username))
    
        return redirect(url_for('admin.useredit', id=user.id ))

    
    form = UserAddForm()
    return render_template('admin/users_add.html',page='Admin',form=form)

################################################################################################
################################################################################################
################################################################################################

class vAdmListData:
	 name=''
	 add=''
	 ajaxlink=''

class vAdmEditData:
    base=''
    action=''
    db=None
    Form=None
    def on_new(self, form, item): pass

def vAdmEdit(Data):
    try:
        itemid = int(request.args.get('id', -1))
    except:
        flash("Invalid request",'danger')
        return redirect(url_for(Data.base))
        
    if itemid>=0:
        item=Data.db.query.get(itemid)
    else:
        item=None
    
    form=Data.Form(obj=item)
    if hasattr(form,'fillChoices'):
        form.fillChoices(current_user)

    if form.validate_on_submit():
        if item is None:
            #Create new
            item = Data.db()
            form.populate_obj(item)
            db.session.add(item)
            Data.on_new(form,item)
#            db.session.commit()
#            form.populate_obj(item)
        else:
            form.populate_obj(item)
        db.session.commit()
        return redirect(url_for(Data.base))    

    form.id=itemid
    form.formaction=url_for(Data.action, id=form.id)
    return render_template('admin/listajax.html',form=form)

################################################################################################

##### Facilities #####

@admin.route('/admin/facilities')
def facilities():
    data=vAdmListData()
    data.name='Facilities'
    data.add='Add facility'
    data.ajaxlink='admin.facilityedit'
    tbl=FacilitiesTable(Facility.AllMayAdmin(current_user))
    return render_template('admin/listadmin.html',page='Admin',table=tbl,ListData=data)
        
@admin.route('/admin/facilities/edit', methods=['GET','POST'])
def facilityedit():
    data=vAdmEditData()
    data.base='admin.facilities'
    data.action='admin.facilityedit'
    data.db=Facility
    data.Form=FacilityEditForm
    
    def f_on_new(form,item): 
        admrole=Role.query.filter(Role.name=='Admin').one()
        ur=UserRoles(item.id,admrole.id)
        current_user.roles.append(ur)
        
    data.on_new = f_on_new

    return vAdmEdit(data)

##### Rooms #####
	
@admin.route('/admin/rooms')
def rooms():
    data=vAdmListData()
    data.name='Rooms'
    data.add='Add room'
    data.ajaxlink='admin.roomsedit'

    tbl=RoomsTable(Room.query.order_by('id').all())
    return render_template('admin/listadmin.html',page='Admin',table=tbl,ListData=data)

@admin.route('/admin/rooms/edit', methods=['GET','POST'])
def roomsedit():
    data=vAdmEditData()
    data.base='admin.rooms'
    data.action='admin.roomsedit'
    data.db=Room
    data.Form=RoomEditForm
    
    return vAdmEdit(data)

##### Equipment #####
    
@admin.route('/admin/equipment')
def equipment():
    data=vAdmListData()
    data.name='Equipment'
    data.add='Add equipment'
    data.ajaxlink='admin.equipmentedit'

    tbl=EquipmentTable(Equipment.AllMayAdmin(current_user))
    return render_template('admin/listadmin.html',page='Admin',table=tbl,ListData=data)
        
@admin.route('/admin/equipment/edit', methods=['GET','POST'])
def equipmentedit():
    data=vAdmEditData()
    data.base='admin.equipment'
    data.action='admin.equipmentedit'
    data.db=Equipment
    data.Form=EquipmentEditForm

    def e_on_new(form,item): 
        db.session.commit()
        form.populate_obj(item)
        
    data.on_new = e_on_new
    
    return vAdmEdit(data)    
