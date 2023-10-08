#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api, bcrypt
from models import User, Recipe

import pdb


class Index(Resource):
    def get(self):
        return {"message": "Welcome!"}


class Signup(Resource):
    def post(self):
        json_data = request.get_json()
        username = json_data.get("username")
        password = json_data.get("password")
        image_url = json_data.get("image_url")
        bio = json_data.get("bio")

        if not username:
            return {"message": "Username is required"}, 422

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {"message": "Username is already in use"}, 422

        password_hash = bcrypt.generate_password_hash(password.encode("utf-8")).decode(
            "utf-8"
        )

        new_user = User(
            username=username,
            _password_hash=password_hash,
            image_url=image_url,
            bio=bio,
        )

        db.session.add(new_user)
        db.session.commit()
        serialized_user = new_user.serialize()
        return serialized_user, 201


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.serialize(), 200
            else:
                return {"message": "User not found"}, 404
        else:
            return {}, 401


class Login(Resource):
    def post(self):
        # pdb.set_trace()
        json_data = request.get_json()
        username = json_data.get("username")
        password = json_data.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session["user_id"] = user.id
            return {"message": "Login successful", "username": user.username}, 200
        else:
            return {"message": "Invalid username or password"}, 401


class Logout(Resource):
    def delete(self):
        if "user_id" in session and session["user_id"] != None:
            session["user_id"] = None
            return {}, 204
        else:
            return {"message": "Unauthorized"}, 401


class RecipeIndex(Resource):

    def get(self):
        user_id = session["user_id"]

        if user_id == None:
            return {"message": "Unauthorized"}, 401

        user = User.query.get(user_id)
        if user == None:
            return {"message": "User not found"}, 404

        user_recipes = user.recipes
        serialized_recipes = [recipe.serialize() for recipe in user_recipes]

        return serialized_recipes, 200

    def post(self):
        user_id = session["user_id"]

        json_data = request.get_json()
        title = json_data.get("title")
        instructions = json_data.get("instructions")
        minutes_to_complete = json_data.get("minutes_to_complete")

        if title == None:
            return {'message': 'Invalid data'}, 422
        if len(instructions) < 50:
            return {'message': 'Invalid data'}, 422
        if minutes_to_complete < 0:
            return {'message': 'Invalid data'}, 422
        
        user = User.query.get(user_id)

        if user == None:
            return {"message": "User not found"}, 404

        new_recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user=user,
        )

        db.session.add(new_recipe)
        db.session.commit()

        return new_recipe.serialize(), 201


api.add_resource(Index, "/")
api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(CheckSession, "/check_session", endpoint="check_session")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(Logout, "/logout", endpoint="logout")
api.add_resource(RecipeIndex, "/recipes", endpoint="recipes")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
