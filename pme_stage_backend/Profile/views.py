from flask import Blueprint, request, jsonify
from Profile.models import ProfileModel
from Previlege.models import PrevilegeModel
from Profile.utils import add_profile,update_profile,delete_profile
from db import db
profiles = Blueprint("profiles", __name__, url_prefix="/profiles")

@profiles.post('/create')
def create_profile():
    nom = request.json.get('nom', '')
    description = request.json.get('description', '')
    creation_date = request.json.get('creation_date', '')
    # previleges = request.json.get('previleges', [])
    if len(description) > 10:
            return jsonify({
            "error": "description must be less than 10 characters!"
         }),400
    if not (nom and description):
        return jsonify({
            "error": "Please enter valid name and description!"
         }), 400
    if ProfileModel.query.filter_by(nom=nom).first() is not None:
        return jsonify({'error': "Profile already exist!"}), 409

    add_profile(nom, description,creation_date)
    return jsonify({
         'message': "Profile created",
     }), 201

@profiles.get('/')
def get_profile():
    pages = request.args.get('page')
    per_page = 10
    id_profile = request.args.get('id_profile')

    if not pages:
        if id_profile:
            return {'profile': list(map(lambda x: x.serialize(), ProfileModel.query.filter_by(id_profile=id_profile)))}
        else:
            return {'profiles': list(map(lambda x: x.serialize(), ProfileModel.query.all()))}
    else:
        page = int(pages)
        if id_profile:
            return {'profile': list(map(lambda x: x.serialize(), ProfileModel.query.filter_by(id_profile=id_profile).paginate(page, per_page, error_out=False).items))}
        else:
            return {'profiles': list(map(lambda x: x.serialize(), ProfileModel.query.paginate(page, per_page, error_out=False).items))}


@profiles.put('/update/<int:_id_profile>')
def edit_profile(_id_profile):
    _nom = request.json.get('nom', '')
    _description = request.json.get('description', '')
    _creation_date = request.json.get('creation_date', '')

    if not (_id_profile and _nom ):
        return jsonify({
            "error": "Please enter a valid ID and  name!"
         }), 400

    if update_profile(_id_profile, _nom, _description,_creation_date):
        return jsonify({
             'message': "profile updated",
         }), 200
    else:
        return jsonify({'error': "No profile found with the given ID!"}), 404


@profiles.delete('/delete/<int:_id_profile>')
def remove_profile(_id_profile):
    if not (_id_profile):
            return jsonify({
            "error": "Please enter a valid ID!"
         }), 400
    if delete_profile(_id_profile):
        return jsonify({
             'message': "Profile deleted ",
         }), 200
    else:
        return jsonify({'error': "No Profile found with the given ID!"}), 404
    
        
@profiles.post('/assign_profile_to_privileges')
def assign_profile_to_privileges():
    try:
        id_profile = request.json.get('id_profile', '')
        privileges_id = request.json.get('previleges', [])
        
        profile = ProfileModel.query.get(id_profile)
        if not profile:
            return 'Profile not found', 404

        # Fetchi previleges by id 
        previleges = PrevilegeModel.query.filter(PrevilegeModel.id_previlege.in_(privileges_id)).all()
        # Assign the profile to the list of privileges
        profile.previleges.extend(previleges)    
        print(profile)
        # Commit changes 
        db.session.commit()
        return 'Profile assigned to privileges successfully', 200
    except Exception as e:
        db.session.rollback()
        return str(e), 500