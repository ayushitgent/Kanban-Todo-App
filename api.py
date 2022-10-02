from dataclasses import fields
from re import X
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from datetime import datetime
from marshmallow import Schema, fields, ValidationError, pre_load


from app import app,db

ma = Marshmallow(app)
api = Api(app)


from app import User,Card,Task_lis

class CardSchema(ma.Schema):
    id=fields.Int(dump_only=True)
    title=fields.Str()
    content=fields.Str()
    created=fields.Str()
    deadline=fields.Str()
    is_completed=fields.Str()
    completed_time=fields.Str()
    task_id=fields.Int()
        
class Task_lisSchema(ma.Schema):
    list_id=fields.Int()
    list_name=fields.Str()   
    
        
class UserSchema(ma.Schema):
    id=fields.Int(dump_only=True)
    name=fields.Str()




user_schema = UserSchema()
users_schema = UserSchema(many=True)
tasklist_schema=Task_lisSchema()
tasklists_schema=Task_lisSchema(many=True)
card_schema=CardSchema()
cards_schema=CardSchema(many=True)

class UserList(Resource):
    def get(self):#get all the available users and their ids
        users = User.query.all()
        x= users_schema.dump(users)
        return {"Users": x}

    def post(self):
        new_user = User(
            name=request.json['name']
        )
        db.session.add(new_user)
        db.session.commit()
        return user_schema.dump(new_user)



class User_List(Resource):
    def get(self, id):
        user = User.query.get_or_404(id)
        return user_schema.dump(user)

    def put(self, id):
        user = User.query.get_or_404(id)

        if 'name' in request.json:
            user.name = request.json['name']
        # if 'content' in request.json:
        #     post.content = request.json['content']

        db.session.commit()
        return user_schema.dump(user)

    def delete(self, id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return user_schema.dump(user), 204

class Tasklis(Resource):
    def get(self,user_id):#get all the available users and their ids
        task = Task_lis.query.filter_by(user_id=user_id).all()
        x= tasklists_schema.dump(task)
        return {"Task lists": x}

    def post(self,user_id):
        new_list = Task_lis(
            list_name=request.json['list_name'],user_id=user_id
        )
        db.session.add(new_list)
        db.session.commit()
        return tasklist_schema.dump(new_list)



class Task_list(Resource):
    def get(self,user_id, list_id):
        task = Task_lis.query.get_or_404(list_id)
        return tasklist_schema.dump(task)

    def put(self, user_id,list_id):
        task = Task_lis.query.get_or_404(list_id)

        if 'list_name' in request.json:
            task.list_name = request.json['list_name']
        db.session.commit()
        return tasklist_schema.dump(task)

    def delete(self, user_id,list_id):
        task = Task_lis.query.get_or_404(list_id)
        db.session.delete(task)
        db.session.commit()
        return tasklist_schema.dump(task), 204
    
class Cardlist(Resource):
    def get(self,user_id,list_id):#get all the available users and their ids
        card = Card.query.filter_by(task_id=list_id).all()
        x= cards_schema.dump(card)
        return {"cards": x}

    def post(self,user_id,list_id):
        card = Card(
            title=request.json['title'],task_id=list_id,
            content=request.json['content'],
            deadline=request.json['deadline']
        )
        db.session.add(card)
        db.session.commit()
        return card_schema.dump(card)



class Card_list(Resource):
    def get(self, id):
        card = Card.query.get_or_404(id)
        return card_schema.dump(card)

    def put(self, id):
        card = Card.query.get_or_404(id)

        if 'deadline' in request.json:
            card.deadline = request.json['deadline']
        if 'title' in request.json:
            card.title = request.json['title']
        if 'content' in request.json:
            card.content = request.json['content']
        if 'is_completed' in request.json:
            card.is_completed = request.json['is_completed']
        if 'task_id' in request.json:
            card.task_id = request.json['task_id']
        db.session.commit()
        return card_schema.dump(card)

    def delete(self,id):
        card = Card.query.get_or_404(id)
        db.session.delete(card)
        db.session.commit()
        return card_schema.dump(card), 204







api.add_resource(UserList, '/users')
api.add_resource(User_List, '/users/<int:id>')
api.add_resource(Tasklis, '/<int:user_id>/task_list')
api.add_resource(Task_list, '/<int:user_id>/task_list/<int:list_id>')
api.add_resource(Cardlist, '/<int:user_id>/<int:list_id>/card')
api.add_resource(Card_list, '/card/<int:id>')



if __name__ == '__main__':
    
    db.create_all()
    app.run(debug=True,port="5001")
