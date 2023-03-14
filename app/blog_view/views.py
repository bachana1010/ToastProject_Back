import json

from flask import Blueprint, render_template, flash, request, jsonify, session,redirect, url_for
from app import db
from app.models import Toast
from werkzeug.utils import secure_filename
import os
from io import BytesIO
from werkzeug.datastructures import FileStorage







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


    creat_toast = Toast(
        title=data['title'],
        content=data['content'],
        img=binary_data,
        input = array_input
    )

    db.session.add(creat_toast)
    db.session.commit()
    return "123"


#
#
# @blog_blueprint.route('/read', methods=['GET', 'POST'])
# def read():
#         read = Blog.query.all()
#         list = []
#         for item in read:
#             sb_list = {
#                 'id': item.id,
#                 'Text': item.Text,
#                 'capital_city': item.capital_city,
#                 'country': item.country,
#                 'date': item.date,
#                 "flag": item.flag
#             }
#             list.append(sb_list)
#
#         return jsonify({"data": list})
#
#
#
# @blog_blueprint.route('/delete', methods=['POST', 'GET'])
# def delete_blog():
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
