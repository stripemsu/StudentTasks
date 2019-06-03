import ldap3
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import InputRequired
from todolist import db, app
from ..database import User

def ldap_login(username, password):
    cstr='CN=%s,OU=Txstate Users,DC=matrix,DC=txstate,DC=edu' % username
    try:
        serv=ldap3.Server(app.config['LDAP_PROVIDER_URL'], get_info=ldap3.ALL)
        conn=ldap3.Connection(serv,cstr,password)
        if not conn.bind():
            return None;
    except ldap3.core.exceptions.LDAPBindError as e:
        print(e.message['info'])
        if type(e.message) == dict and e.message.has_key('desc'):
            print(e.message['desc'])
        else:
            print(e)
        return None

    user = User.query.filter_by(username=username).first()
    if (user is None) or (not user.is_active):
        return None
    if user.email is None:
        basedn = 'OU=Txstate Users,DC=matrix,DC=txstate,DC=edu'
        searchFilter ="(&(objectCategory=Person)(sAMAccountName=%s))"%username
        searchAttribute = ['mail','displayName']
        try:
            if not conn.search(basedn,searchFilter,ldap3.SUBTREE,attributes=searchAttribute):
                raise()
            data = conn.response[0]['attributes']
            user.email=data['mail'];
            if user.nickname is None or user.nickname == '':
                user.nickname=data['displayName']
            db.session.commit()
        except:
            print('Ldapsearch error')

        conn.unbind()
    return user

class LoginForm(FlaskForm):
    username = TextField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
    remember = BooleanField('Remember me')
