from flask import Blueprint, render_template, request, redirect, jsonify
from connectors.mysql_connector import engine

from models.user import User
from sqlalchemy import select, or_
from sqlalchemy.orm import sessionmaker
from flask_login import login_user, logout_user
from flask_jwt_extended import create_access_token
from validator.user import userSchema
from flask_login import current_user, login_required

user_routes = Blueprint('user_routes',__name__)

@user_routes.route("/users/register", methods=['POST'])
def do_registration():
    schemas = userSchema()

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    NewUser = User(username=username, email=email)
    NewUser.set_password(password)

    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    session.begin()
    try:
        session.add(NewUser)
        session.commit()
    
    except Exception as e:
        print (e)
        session.rollback()
        return { "message": "Failed register"}
    userjsonify = schemas.dump(NewUser)
    return { "message": "Success register", "data": userjsonify }

@user_routes.route("/users/login", methods=['POST'])
def do_login():
    connection = engine.connect()
    Session = sessionmaker(bind=connection)
    session = Session()

    try:
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        match_user = session.query(User).filter(User.email == email).first()

        if not match_user:
            return jsonify({"message": "User not found"}), 404

        if not match_user.check_password(password):
            return jsonify({"message": "Incorrect password"}), 401

        login_user(match_user, remember=False)
        return jsonify({"message": "Login success"}), 200

    except Exception as e:
        return jsonify({"message": f"Login Failed: {str(e)}"}), 500
    
@user_routes.route("/users/<int:id>", methods=['PUT'])
@login_required
# @jwt_required
def product_update(id):

    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    session.begin()
    schemas = userSchema()
    user = session.query(User).filter(User.id==id).first()
    try:
        
        user.username = request.form['username']
        user.email = request.form['email']
        user.set_password(request.form['password'])

        session.add(user)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        return { "message": "Fail to Update data"}

    userjsonify = schemas.dump(user)
    
    return { "message": "Success updating data", "data": userjsonify }
    
# @user_routes.route("/logout", methods=['GET'])
# def user_logout():
#     logout_user()
#     return redirect('/login')

# @user_routes.route("/loginjwt", methods=['POST'])
# def do_user_login_JWT():

#     connection = engine.connect()
#     Session = sessionmaker(connection)
#     session = Session()

#     session.begin
#     try:
#         match_user = session.query(User).filter(User.email==request.form['email']).first()

#         if match_user == None:
#             return { "message": "Email not registered"}
        
#         #check password
#         if not match_user.check_password(request.form['password']):
#             return { "message": "Incorrect password"}
        
#         access_token = create_access_token(identity=match_user.id, additional_claims={"name": match_user.name, "role": match_user.role})
#         return jsonify({"access_token": access_token})
    
#     except Exception as e:
#         session.rollback()
#         return { "message": "Failed login"}