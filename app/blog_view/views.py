import json
from sqlalchemy import create_engine

from flask import Blueprint, render_template, flash, request, jsonify, session,redirect, url_for,abort,make_response
from app import db
from app.models import Toast, User
import base64
import re
from app.extentions import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extentions import db, jwt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, verify_jwt_in_request
)

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






#     params = request.get_json()
#     delId = params['id']
#     my_data = Blog.query.get(delId)
#
#     db.session.delete(my_data)
#     db.session.commit()
#     print(delId)
#     return jsonify({
#         "id": delId
#     })
#
#
#
#
# @blog_blueprint.route('/update', methods=['GET', 'POST'])
# def update():
#     params = request.get_json()
#     upId = params['id']
#
#     my_data_update = Blog.query.get(upId)
#
#     print(params)
#
#     my_data_update.country = params["country"]
#     my_data_update.capital_city = params["capital_city"]
#     my_data_update.flag = params["flag"]
#     my_data_update.date = params["date"]
#     my_data_update.Text = params["Text"]
#
#
#
#
#     db.session.add(my_data_update)
#     db.session.commit()
#     return render_template('home.html')
#
#
