from flask import Blueprint, request, jsonify,session
from User.models import UserModel
from Entreprise.models import Entreprise
from Profile.models import ProfileModel
from Previlege.models import PrevilegeModel
from passlib.hash import bcrypt
import bcrypt
from sqlalchemy.exc import IntegrityError
from db import db
from flask_mail import Message
from mail_utils import mail
import json
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import (get_jwt,
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import bcrypt
from User.utils import generate_reset_token,send_reset_email
from werkzeug.security import generate_password_hash,check_password_hash
from User.utils import add_user,update_user,delete_user,generate_random_password
import random
import string
profile = Blueprint("profile", __name__, url_prefix="/profile")
user = Blueprint("user", __name__, url_prefix="/users")


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    disallowed_characters = ["'",'/','.',',','~','"','`',';',':','\\', '(', ')', '|', '[', ']', '{', '}', '=', '+', '*', '?', '$', '^', '&','>','<']
    
    while True:
        password = ''.join(random.choice(characters) for _ in range(length))
        if all(char not in password for char in disallowed_characters):
            return password
def generate_password_hash_scrypt(password):
    return generate_password_hash(password, method='scrypt')
@user.post('/register')
def signup_user():
    try:
        print(request.json)
        nom = request.json.get('nom', None)
        prenom = request.json.get('prenom', None)
        email = request.json.get('email', None)
        description = request.json.get('description', None)
        profile_id = request.json.get('profile_id', None)
        reset_token = request.json.get('reset_token', None)
        # previleges = request.json.get('previleges', None)
        
        if not email:
            return 'Missing email', 400
        # Generate a random password for the user
        random_password  = generate_random_password()
        password_hashed =generate_password_hash_scrypt(random_password)
        profile = ProfileModel.query.get(profile_id)
        if not profile:
            return 'Profile not found', 400
        add_user(nom, prenom, email,password_hashed, description, profile_id,reset_token)  # Pass the password_hash
        # Send the confirmation email with the generated password
        recipients = [email]
        msg = Message(
            'SignUP Confirmation !',
            sender='malek.chiha@esprit.tn',
            recipients=recipients
        )
        msg.body = f'Hello {prenom} {nom},\n\nWelcome to our plateforme!\n Here he is your password : {random_password} and you will be logging in with an {profile.nom} profile '
        mail.send(msg)
        return {"message": "User added successfully"}, 200
    except IntegrityError:
        # the rollback func reverts the changes made to the db
        db.session.rollback()
        return 'User Already Exists', 400
    except AttributeError:
        return 'Provide an Email and Password in JSON format in the request body', 400


@user.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response
@user.post('/login')
def login_user():
    try:
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        
        if not email: 
            return 'Missing email', 400
        if not password:
            return 'Missing password', 400
        
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            return 'User Not Found!', 404   
       # Check if the user is already logged in
        if 'email' in session and session['email'] == email:
            return {'message': 'You are already logged in', 'email': email}
        session['email'] = email
        print("Compare passwords: ",check_password_hash(user.password_hash,password))
        if check_password_hash(user.password_hash,password):
        # Verify the provided password
        #    access_token = create_access_token(identity=UserModel['user.id_user'])
           access_token = create_access_token(identity={"id_user": user.id_user})
           return {"access_token": access_token,'email': email,'password': password}, 200
        else:
            return 'Invalid Login Info!', 400
    except AttributeError:
        return 'Provide an Email and Password in JSON format in the request body', 400
    
@user.get('/logout')
def logout():
	if 'email' in session:
		session.pop('email', None)
	return jsonify({'message' : 'You successfully logged out'})

@user.get('/getusers')
def get_user():
    pages = request.args.get('page')
    per_page = 10
    id_user = request.args.get('id_user')

    if not pages:
        if id_user:
            return {'user': list(map(lambda x: x.serialize(), UserModel.query.filter_by(id_user=id_user)))}
        else:
            return {'users': list(map(lambda x: x.serialize(), UserModel.query.all()))}
    else:
        page = int(pages)
        if id_user:
            return {'user': list(map(lambda x: x.serialize(), UserModel.query.filter_by(id_user=id_user).paginate(page, per_page, error_out=False).items))}
        else:
            return {'users': list(map(lambda x: x.serialize(), UserModel.query.paginate(page, per_page, error_out=False).items))}



@user.put('/update/<int:_id_user>')
def edit_user(_id_user):
    _nom = request.json.get('nom', None)
    _prenom = request.json.get('prenom', None)
    _email = request.json.get('email', None)
    _description = request.json.get('description', None)
    _profile_id = request.json.get('profile_id', None)
    _reset_token = request.json.get('reset_token', None)

    if not (_id_user and _nom ):
        return jsonify({
            "error": "Please enter a valid ID and  name!"
         }), 400
          
    if update_user(_id_user, _nom,_prenom,_email, _description,_profile_id,_reset_token):
        return jsonify({'message': "user updated",}), 200
    else:
        return jsonify({'error': "No user found with the given ID!"}), 404


@user.delete('/delete/<int:_id_user>')
def remove_user(_id_user):
    if not (_id_user):
            return jsonify({
            "error": "Please enter a valid ID!"
         }), 400
    if delete_user(_id_user):
        return jsonify({
             'message': "user deleted ",
         }), 200
    else:
        return jsonify({'error': "No user found with the given ID!"}), 404
    
@user.post('/assign_user_to_privileges')
def assign_user_to_privileges():
    try:
        user_id = request.json.get('id_user', '')
        previlege_id = request.json.get('previleges', [])
        
        user = UserModel.query.get(user_id)
        if not profile:
            return 'user not found', 404
        # Fetchi previleges by id 
        previleges = PrevilegeModel.query.filter(PrevilegeModel.id_previlege.in_(previlege_id)).all()
        # Assign the profile to the list of privileges
        user.previleges.extend(previleges)    
        print(user)
        # Commit changes 
        db.session.commit()
        return 'user assigned to privileges successfully', 200
    except Exception as e:
        db.session.rollback()
        return str(e), 500

# @user.get("/currentuser")
# @jwt_required()
# def get_current_user():
#     id_user = get_jwt_identity()
#     print(id_user)
#     return jsonify({
#         "message": "successfully retrieved user profile",
#         "user": list(map(lambda x: x.serialize(), UserModel.query.filter_by(id_user=id_user))),
#         "data": id_user
#     })
 
@user.get("/currentuser")
@jwt_required()
def get_current_user():
    current_user = get_jwt_identity()  # Assuming this contains the JWT identity payload

    user_id = current_user.get('id_user')  # Extract the user ID from the payload
    if user_id is None:
        return jsonify({"message": "User ID not found in JWT identity"}), 400

    user = UserModel.query.filter_by(id_user=user_id).first()
    if user:
        user_data = {
            "id_user": user.id_user,
            "nom": user.nom,
            "prenom": user.prenom,
            "email": user.email,
            "description": user.description,
            "creation_date": user.creation_date,
            "profile_id": user.profile_id
        }
        return jsonify({
            "message": "successfully retrieved user profile",
            "user": user_data
        })
    else:
        return jsonify({"message": "User not found"}), 404
     

    
    
@user.post('/forgot_password')
def forgot_password():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Please provide your email address'}), 400

    # Check if the email belongs to a registered user
    user = UserModel.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

   # Generate a reset token and save it in the user's record
    reset_token = generate_reset_token()
    user.reset_token = reset_token
    db.session.commit()

    # Send the reset token to the user's email
    send_reset_email(user.email)

    return jsonify({'message': 'Password reset email sent successfully','reset_token':reset_token}), 200


@user.post('/reset_password')
def reset_password():
    reset_token = request.headers.get('resetToken')
    print("Received Reset Token:", reset_token)
    data = request.json
    password = data.get('password')

    if not password or not reset_token:
        return jsonify({'error': 'Please provide a new password and reset_token'}), 400

    # Find the user by the reset token
    user = UserModel.query.filter_by(reset_token=reset_token).first()
    if not user:
        return jsonify({'error': 'Invalid reset token'}), 400

    # Reset the user's password and clear the reset token
    user.password_hash = generate_password_hash(password, method='sha256')
    user.reset_token = None
    db.session.commit()
    return jsonify({'message': 'Password reset successfully'}), 200

@user.post('/assign_user_to_enterprises')
def assign_user_to_enterprises():
    try:
        data = request.json
        id_user = data.get('id_user')
        enterprise_ids = request.json.get('enterprises', [])

        if id_user is None or enterprise_ids is None:
            return {"error": "Missing required data"}, 400

        user = UserModel.query.get(id_user)
        if not user:
            return {"error": "User not found"}, 404

        enterprises = Entreprise.query.filter(Entreprise.id_Entreprise.in_(enterprise_ids)).all()
        if not enterprises:
            return {"error": "Enterprises not found"}, 404
        print("User:", user)
        print("Enterprises:", enterprises)

        # Update user's enterprises
        # user.entreprises = entreprises

        # Print user.entreprises before committing
        print("User Enterprises before commit:", user.entreprises)
        user.entreprises = enterprises
        # user.entreprises.append(enterprises)  # Assign the first entreprise
        db.session.flush()
        db.session.commit()

        # Print user.entreprises after committing
        print("User Enterprises after commit:", user.entreprises)

        return {"message": "Enterprises assigned to user successfully"}, 200

    except Exception as e:
        db.session.rollback()  # Rollback changes in case of error
        return {"error": str(e)}, 500





