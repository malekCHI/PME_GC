from functools import wraps
from flask import request
from Profile.models import ProfileModel
from Previlege.models import PrevilegeModel


def get_all_profiles():
    return {'profile': list(map(lambda x: x.serialize(), ProfileModel.query.all()))}

 
def get_profile(_id_profile):
    return {'profile': list(map(lambda x: x.serialize(), ProfileModel.query.filter_by(id_profile=_id_profile).first()))}


def add_profile(nom, description,creation_date):
    profile = ProfileModel(nom=nom,description=description,creation_date=creation_date) 
    profile.save_to_db()


def update_profile(_id_profile, _nom,_description,_creation_date):
    profile_to_update = ProfileModel.query.filter_by(id_profile=_id_profile).first()
    if profile_to_update:
        profile_to_update.nom = _nom
        profile_to_update.description = _description
        profile_to_update.creation_date = _creation_date
        profile_to_update.save_to_db()
        return True
    return False
   
def delete_profile(_id_profile):
    profile_delete=ProfileModel.query.filter_by(id_profile=_id_profile).first()
    if profile_delete:
        profile_delete.delete_from_db() 
        return True
    return False      
