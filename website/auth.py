from flask import Blueprint,render_template,request,flash,redirect,url_for
from website.models2 import Business
from . import db2
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required,logout_user,current_user

auth = Blueprint('auth',__name__)

@auth.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password =request.form.get('password')
        user = Business.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password,password):
                flash("Logged in Successfully!",category='success')
                login_user(user,remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect password. Try again!",category='error')
        else:
            flash('Email doesn\'t exist.',category='error')
    
    return render_template("login.html",user =current_user)

@auth.route('/sign_up',methods = ['GET','POST'])
def sign_up():
    if request.method == 'POST':
        bname = request.form.get('bname')
        firstname = request.form.get('firstname')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = Business.query.filter_by(email = email).first()
        b_name = Business.query.filter_by(bname = bname).first()

        if b_name:
            flash('Business Name already exists.',category='error')
        elif user:
            flash('Email already exists.',category='error')
        elif len(email)<4:
            flash('Email must be greater than 4 characters',category ='error')
        elif len(firstname)<2 :
            flash('Name should be greater than 1 character',category ='error')
        elif password1 != password2:
            flash('passwords don\'t match.',category ='error')
        elif len(password1)<7:
            flash('password is too short',category ='error')
        else:
            new_user = Business(email=email,
                                bname = bname,
                                Firstname =firstname,
                                password = generate_password_hash(password1,method ='pbkdf2:sha256'))
            db2.session.add(new_user)
            db2.session.commit()
            flash('Accout created successfully!',category ='success')
            login_user(new_user,remember=True)
            return redirect(url_for('views.home'))            
    return render_template("sign_up.html",user =current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
