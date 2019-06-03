from . import db
from .dbmodel import *

def fill_users():
    #First user from Config
    user=User(app.config['FIRST_ADMIN_USER'], None)
    db.session.add(user);

    db.session.commit()

    #Some department
    fac=Facility('ARSC')
    db.session.add(fac);

    db.session.commit()

    #Roles
    role1=Role('User','Basic user role')
    db.session.add(role1);

    role2=Role('Supervisor','Intermidiate role')
    db.session.add(role2)

    role3=Role('Admin','Administrative role')
    db.session.add(role3)

    db.session.commit()

    #User-Roles magic
    ur=UserRoles(fac.id,role3.id)
    user.roles.append(ur)

    db.session.commit()

def fill_tasks():
    rfm1202=Room('RFM 1202');db.session.add(rfm1202)
    rfm1203=Room('RFM 1203');db.session.add(rfm1203)
    sup171=Room('Supp 171');db.session.add(sup171)

    fac=Facility.query.first()

    eqip1 = Equipment('Room RFM1202',rfm1202,fac)
    eqip2 = Equipment('Room RFM1203',rfm1203,fac)
    eqip3 = Equipment('Room SUP171',sup171,fac)
    eqip4 = Equipment('SEM FEI',rfm1202,fac)

    db.session.add(eqip1)
    db.session.add(eqip2)
    db.session.add(eqip3)
    db.session.add(eqip4)

    t1=Task('Wipe the floors',eqip1,True)
    db.session.add(t1)
    t2=Task('Wipe the floors',eqip2,True)
    db.session.add(t2)
    t3=Task('Close rotating door',eqip3,True)
    db.session.add(t3)

    t4=Task('Log Ni tank pressure',eqip4,True,logging='Float')
    db.session.add(t4)

    db.session.commit()


def refill_db():
    if False:
        #Drop tables
        db.reflect()
        db.drop_all()
        db.session.commit()
        print('**********************************')
        print('***  You have no data anymore  ***')
        print('**********************************')

    try:
        user=User.query.first()
        if user is not None:
            return
    except:
        pass;

    db.create_all()
    db.session.commit()

    fill_users()
    #fill_tasks()
