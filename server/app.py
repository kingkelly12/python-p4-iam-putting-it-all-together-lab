#!/usr/bin/env python3

from flask import request, session, Flask
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        if not username or not password:
            return {'error': 'Username and password are required.'}, 422

        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )
        try:
            user.password_hash = password  # triggers hashing
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 201
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Username already exists.'}, 422
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 422

    # ... other routes ...

    return app

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }, 200
        return {'error': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            session['user_id'] = user.id
            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200
        return {'error': 'Invalid username or password.'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
            return '', 204
        return {'error': 'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401

        recipes = Recipe.query.all()
        recipe_list = []
        for recipe in recipes:
            recipe_list.append({
                'id': recipe.id,
                'title': recipe.title,
                'instructions': recipe.instructions,
                'minutes_to_complete': recipe.minutes_to_complete,
                'user': {
                    'id': recipe.user.id,
                    'username': recipe.user.username,
                    'image_url': recipe.user.image_url,
                    'bio': recipe.user.bio
                }
            })
        return recipe_list, 200

    def post(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401

        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=session['user_id']
            )
            db.session.add(recipe)
            db.session.commit()
            user = User.query.get(recipe.user_id)
            return {
                'id': recipe.id,
                'title': recipe.title,
                'instructions': recipe.instructions,
                'minutes_to_complete': recipe.minutes_to_complete,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }
            }, 201
        except IntegrityError as e:
            db.session.rollback()
            return {'error': 'Database integrity error.'}, 422
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)