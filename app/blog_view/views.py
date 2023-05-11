import json
from sqlalchemy import create_engine

from flask import Blueprint, render_template, flash, request, jsonify, session,redirect, url_for,abort,make_response, sessions
from app import db
from app.models import Toast, User, Comment, UserLikeDislike,todo
import jwt as pyjwt
from jwt import ExpiredSignatureError
from jwt import ExpiredSignatureError as JWTExpiredSignatureError

from app.config import SECRET_KEY
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

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
    # toast_info = Toast.query.offset(offset).limit(limit).all()
    toast_info = Toast.query.order_by(Toast.id.desc()).offset(offset).limit(limit).all()

    #
    toasts = []
    for toast in toast_info:
        toast_dict = toast.to_dict()
        toast_dict['author'] = toast.to_dict()  # This line adds the author's information to the toast_dict

        if toast_dict['img'] and isinstance(toast_dict['img'], bytes):
            toast_dict['img'] = base64.b64encode(toast_dict['img']).decode('utf-8')

        toasts.append(toast_dict)

    # Return the list of objects as JSON
    return jsonify({'data': toasts,
                    'total_pages': data.pages})
#


@toast_blueprint.route('/detail/id/<int:id>', methods=['GET', 'POST'])
def detail_page(id):
    toast = Toast.query.get(id)

    if toast:
        # Increment views count
        toast.views += 1
        db.session.commit()

        # Return the toast details
        return jsonify({"success": True, "data": toast.to_dict()})
    else:
        return jsonify({"success": False, "message": "Toast not found"}), 404



@toast_blueprint.route('/MyToast', methods=['GET', 'POST'])
@jwt_required()
def get_my_toast():
    print("get_toast_list() called")

    user_id = get_jwt_identity()
    print(f"User ID: {user_id}")

    authorized_toasts = Toast.query.filter_by(user_id=user_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # calculate the total number of pages
    total_items = authorized_toasts.count()
    total_pages = (total_items - 1) // per_page + 1

    # get the toasts for the current page
    toast_info = authorized_toasts.order_by(Toast.id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    toasts = []
    for toast in toast_info:
        toast_dict = toast.to_dict()

        # Encode the `photooo` field as base64
        if toast_dict.get('img'):
            try:
                # Check if the `img` field is already a base64 encoded string
                base64.b64decode(toast_dict['img'], validate=True)
            except binascii.Error:
                # If not, then encode it as base64
                toast_dict['img'] = base64.b64encode(toast_dict['img']).decode('utf-8')

        toasts.append(toast_dict)

    total_views = sum([toast['views'] for toast in toasts])
    total_likes = sum([toast['likes'] for toast in toasts])

    # Return the list of objects as JSON
    return jsonify({'data': toasts,
                    'total_pages': total_pages,
                    'total_views': total_views,
                    'total_likes': total_likes,
                    'number_of_toasts': total_items})















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


@toast_blueprint.route('/toggle-like/<int:content_id>', methods=['POST'])
def toggle_like_content(content_id):
    token = request.headers.get('Authorization')
    print("Received token:", token)  # Add this line

    if token:
        user_id = decode_token(token.split(' ')[1])
        print("Decoded user ID:", user_id)  # Add this line

        if user_id is None:
            return jsonify({"error": "Invalid token."}), 401
        content = Toast.query.get_or_404(content_id)

        user_like_dislike = UserLikeDislike.query.filter_by(user_id=user_id, content_id=content_id).first()

        if user_like_dislike:
            if user_like_dislike.status == 'like':
                content.likes -= 1
                db.session.delete(user_like_dislike)
            else:
                content.likes += 1
                content.dislikes -= 1
                user_like_dislike.status = 'like'
            db.session.commit()
        else:
            new_user_like_dislike = UserLikeDislike(user_id=user_id, content_id=content_id, status='like')
            content.likes += 1
            db.session.add(new_user_like_dislike)
            db.session.commit()

        return jsonify({'likes': content.likes, 'dislikes': content.dislikes,
                        'status': user_like_dislike.status if user_like_dislike else 'none'})
    return jsonify({"error": "Invalid token."}), 401

@toast_blueprint.route('/toggle-dislike/<int:content_id>', methods=['POST'])
def toggle_dislike_content(content_id):


    token = request.headers.get('Authorization')
    print("Received token:", token)  # Add this line

    if token:
        user_id = decode_token(token.split(' ')[1])
        print("Decoded user ID:", user_id)  # Add this line

        if user_id is None:
            return jsonify({"error": "Invalid token."}), 401
        content = Toast.query.get_or_404(content_id)

        user_like_dislike = UserLikeDislike.query.filter_by(user_id=user_id, content_id=content_id).first()

        if user_like_dislike:
            if user_like_dislike.status == 'dislike':
                content.dislikes -= 1
                db.session.delete(user_like_dislike)
            else:
                content.dislikes += 1
                content.likes -= 1
                user_like_dislike.status = 'dislike'
            db.session.commit()
        else:
            new_user_like_dislike = UserLikeDislike(user_id=user_id, content_id=content_id, status='dislike')
            content.dislikes += 1
            db.session.add(new_user_like_dislike)
            db.session.commit()

        return jsonify({'likes': content.likes, 'dislikes': content.dislikes,
                        'status': user_like_dislike.status if user_like_dislike else 'none'})
    return jsonify({"error": "Invalid token."}), 401


#
@toast_blueprint.route('/update/<int:id>', methods=['POST'])
@jwt_required()
def update_toast(id):
    # Get the Toast object using the provided id (the toast_id, not user_id)
    toastForUpdate = Toast.query.get(id)

    # Get chips from the front
    chips = json.loads(request.form.get('fruits'))
    array_input = json.dumps(chips)

    # Get data from the front
    data = json.loads(request.form.get('data'))

    # # Get the image file from the front
    # file = request.files['image']
    # binary_data = file.read()

    # Check if the toast exists
    if toastForUpdate:
        # Get user_id from JWT token
        user_id = get_jwt_identity()

        # Check if the user is the owner of the toast
        # Compare the JWT user_id with the user_id associated with the Toast object
        if toastForUpdate.user_id == int(user_id):
            # The user is authorized to update the Toast

            # Update the Toast object with the new data
            toastForUpdate.title = data["title"]
            toastForUpdate.content = data["content"]
            toastForUpdate.input = array_input
            # Check if the 'image' key is present in the request.files dictionary
            if 'image' in request.files:
                # Get the image file from the front
                file = request.files['image']
                binary_data = file.read()
                # Update the image only if it's not None
                if binary_data:
                    toastForUpdate.img = binary_data

            # Save the updated Toast object to the database
            db.session.commit()

            return jsonify({'message': 'Toast updated successfully'})
        else:
            # The user is not authorized to update the Toast
            return jsonify({'message': 'Unauthorized'}), 401
    else:
        # The Toast object was not found
        return jsonify({'message': 'Toast not found'}), 404


def decode_token(token):
        if token:
            try:
                # Decode the JWT token and get the user's ID
                payload = pyjwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                print("Decoded payload:", payload)  # Add this line
                return payload["user"]["id"]

            except pyjwt.ExpiredSignatureError:
                return None
            except pyjwt.InvalidTokenError:
                return None


