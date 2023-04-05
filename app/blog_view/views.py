import json
from sqlalchemy import create_engine

from flask import Blueprint, render_template, flash, request, jsonify, session,redirect, url_for,abort,make_response, sessions
from app import db
from app.models import Toast, User, Comment
import jwt as pyjwt
from app.config import SECRET_KEY


import base64
import re
from app.extentions import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extentions import db, jwt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, verify_jwt_in_request,)
from flask_jwt_extended.exceptions import NoAuthorizationError





toast_blueprint = Blueprint('toast_blueprint', __name__,
                                 template_folder="templates",
                                 static_folder="templates/static")



@toast_blueprint.route('/create', methods=['GET', 'POST'])
def create():

    #array
    fruits = json.loads(request.form.get('fruits'))

    array_input = json.dumps(fruits)

    data = json.loads(request.form.get('data'))
    #photo
    file = request.files['photo']
    binary_data = file.read()
    # id
    user__id = json.loads(request.form.get('user_id'))
    user_id = int(user__id)


    user = User.query.get(user_id)
    print(user)
    print(user.toasts)
    for toast in user.toasts:
        print(toast.user_id)

    creat_toast = Toast(
        title=data['title'],
        content=data['content'],
        img=binary_data,
        input = array_input,
        user_id = user_id
    )

    db.session.add(creat_toast)
    db.session.commit()
    return jsonify({"message": "succsesfully added toast"})


@toast_blueprint.route('/list', methods=['GET', 'POST'])
def get_toast_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    data = Toast.query.paginate(page, per_page)

    offset = (page - 1) * per_page
    limit = per_page
    toast_info = Toast.query.offset(offset).limit(limit).all()
    #
    toasts = []
    for toast in toast_info:
        toast_dict = toast.to_dict()
        # Encode the `photo` field as base64
        if toast_dict.get('img'):
            toast_dict['img'] = base64.b64encode(toast_dict['img']).decode('utf-8')
        toasts.append(toast_dict)

    # Return the list of objects as JSON
    return jsonify({'data': toasts,
                    'total_pages': data.pages})
#


@toast_blueprint.route('/MyToast', methods=['GET', 'POST'])
@jwt_required()
def get_my_toast():
    user_id = get_jwt_identity()
    authorized_toasts = Toast.query.filter_by(user_id=user_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    data = authorized_toasts.paginate(page, per_page)

    offset = (page - 1) * per_page
    limit = per_page
    toast_info = authorized_toasts.order_by(Toast.id.desc()).offset(offset).limit(limit).all()

    toasts = []
    for toast in toast_info:
        toast_dict = toast.to_dict()
        # Encode the `photo` field as base64
        if toast_dict.get('img'):
            toast_dict['img'] = base64.b64encode(toast_dict['img']).decode('utf-8')
        toasts.append(toast_dict)

    # Return the list of objects as JSON
    return jsonify({'data': toasts,
                    'total_pages': data.pages})























def check_authorization():
    token = request.headers.get('Authorization')
    if not token or token != 'your_token_here':
        abort(401)


def before_request():
    check_authorization()


@toast_blueprint.route('/delete/id/<int:id>', methods=['POST', 'GET', 'DELETE'])
@jwt_required()
def delete_toast(id):
    toast = Toast.query.get(id)
    print(id)
    if toast:

        user_id = get_jwt_identity()  # Get user id from JWT token

        if toast.user_id == int(user_id):  # Check if the user is the owner of the toast
            toast.delete1()  # Call the delete method on the toast object
            return jsonify({'message': 'Toast deleted successfully'})
        else:
            return jsonify(
                {'message': 'Unauthorized'}), 401  # Return 401 if the user is not authorized to delete the toast
    else:
        return jsonify({'message': 'Toast not found'}), 404  # Return 404 if the toast is not found




@toast_blueprint.route('/toasts/<int:toast_id>/comments', methods=["POST"])
def add_comment(toast_id):
    content = request.json.get("content", None)
    if not content:
        return jsonify({"error": "Content is required"}), 400

    toast = Toast.query.get(toast_id)
    if not toast:
        return jsonify({"error": "Toast not found"}), 404

    # Get the JWT token from the request header
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = None

    if token:
        try:
            # Decode the JWT token and get the user's ID
            payload = pyjwt.decode(token, SECRET_KEY,algorithms=["HS256"])
            user_id = payload["user"]["id"]
            print("Token: ", token)  # Add this print statement
            print("Secret key: ", SECRET_KEY)  # Add this print statement
        except pyjwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

    comment = Comment(content=content, toast_id=toast_id, user_id=user_id)
    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.to_dict()), 201

@toast_blueprint.route('/toasts/<int:toast_id>/comments', methods=['GET'])
def get_comments(toast_id):
    toast = Toast.query.get(toast_id)
    if not toast:
        return jsonify({'error': 'Toast not found'}), 404

    comments = [comment.to_dict() for comment in toast.comments]
    return jsonify(comments)
