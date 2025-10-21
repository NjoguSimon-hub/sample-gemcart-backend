from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app import db
from app.models.user import User
from app.schemas.user_schema import UserSchema, UserRegistrationSchema, UserLoginSchema
from app.utils.decorators import role_required
from app.services.email_service import send_verification_email

class AuthRegister(Resource):
    """
    User Registration
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
            first_name:
              type: string
            last_name:
              type: string
            role:
              type: string
              enum: [customer, seller]
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error
    """
    
    def post(self):
        schema = UserRegistrationSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            role=data.get('role', 'customer')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        send_verification_email(user.email, user.username)
        
        access_token = create_access_token(identity=user.id)
        user_schema = UserSchema()
        
        return {
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user_schema.dump(user)
        }, 201

class AuthLogin(Resource):
    """
    User Login
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    
    def post(self):
        schema = UserLoginSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']):
            if not user.is_active:
                return {'message': 'Account is deactivated'}, 401
            
            access_token = create_access_token(identity=user.id)
            user_schema = UserSchema()
            
            return {
                'message': 'Login successful',
                'access_token': access_token,
                'user': user_schema.dump(user)
            }, 200
        
        return {'message': 'Invalid credentials'}, 401

class AuthProfile(Resource):
    """
    Get User Profile
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: User profile
      401:
        description: Unauthorized
    """
    
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return {'message': 'User not found'}, 404
        
        user_schema = UserSchema()
        return {'user': user_schema.dump(user)}, 200
    
    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return {'message': 'User not found'}, 404
        
        data = request.json
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        
        db.session.commit()
        
        user_schema = UserSchema()
        return {
            'message': 'Profile updated successfully',
            'user': user_schema.dump(user)
        }, 200