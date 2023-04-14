from flask import Blueprint, flash, url_for, \
    redirect, render_template, request, session, jsonify, make_response
from flask_login import login_user, current_user, logout_user
import jwt
import datetime
from functools import wraps
from app.config import SECRET_KEY
from app.models import User
from app import db

user_blueprint = Blueprint('user', __name__, template_folder="templates", static_folder="templates/static")


@user_blueprint.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == "POST":
        params = request.get_json()
        email = params['email']
        username = params['username']

        # Check if the email or username is already registered
        existing_email = User.query.filter_by(email=email).first()
        existing_username = User.query.filter_by(username=username).first()

        if existing_email:
            # Return an error message
            return make_response(jsonify({"error": "Email already registered"}), 400)

        if existing_username:
            # Return an error message
            return make_response(jsonify({"error": "Username already taken"}), 400)

        user = User(
            username=username,
            email=email,
            password=params['password']
        )

        db.session.add(user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    return jsonify()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'token is missiiiiing'}), 403

        # try:
        data = jwt.decode(token, SECRET_KEY,algorithms=['HS256'])
        # except:
        #     return jsonify({'message': 'token is invaliiiiiiiid!'}), 403
        return f(data,*args, **kwargs)
    return decorated



@user_blueprint.route('/me')
@token_required
def me(data):

    current_useri = User.find_by_email(data['user']['email'])
    user_information = ''
    for x,y in data.items():
        if x == "user":
            user_information = y

    print("iuseris info", user_information)
    # print(current_useri)

    # token = request.headers.get('Authorization')

    return user_information


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    params = request.get_json()
    user = User.find_by_email(params['email'])

    if user is not None and user.check_password(params['password']):

         token = jwt.encode({
             "sub": str(user.id),
             "user":{
             "id": user.id,
             "username": user.username,
             "email": user.email}, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=50)}, SECRET_KEY)


         return jsonify({
             'token': token,
             'user': {
                 'username': user.username,
                 'email': user.email,
                 'id': user.id
             }
        })

    return make_response("could not veriy", 401, {"WWW-Authenticate": 'basic realm="login requeired"'})







@user_blueprint.route('/updateUser', methods=['GET', 'POST', 'UPDATE', 'PUT'])
def updateUser():
    paramsFromFront = request.get_json()
    token = request.headers.get('Authorization')

    InfoAboutUser = jwt.decode(token, SECRET_KEY)

    print("paramsebi",paramsFromFront)
    print('es dataa ukve decokidrebuli', InfoAboutUser)

    user = User.find_by_email(InfoAboutUser['user']['email'])

    if user is not None and user.check_password(paramsFromFront['password']):
        upId = InfoAboutUser['user']['id']

        my_data_update = User.query.get(upId)

        my_data_update.username = paramsFromFront["username"]
        my_data_update.email = paramsFromFront["email"]

        db.session.add(my_data_update)
        db.session.commit()

        return jsonify({
            "result": "succsesfully updated"
        })

    return make_response("could not update", 401)


