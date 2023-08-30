from Entreprise.models import Entreprise 
from flask import request
from sqlalchemy.orm import validates
from sqlalchemy import exc
from sqlalchemy import func
from db import db
                                
def get_all_Entreprises():
    return {'entreprise': list(map(lambda x: x.serialize(), Entreprise.query.all()))}

 
def get_entreprise(_id_Entreprise):
    return {'entreprise': list(map(lambda x: x.serialize(), Entreprise.query.filter_by(_id_Entreprise=_id_Entreprise).first()))}
next_available_id = 1
def add_entreprise(nom, adresse, description,email,tel,lien_logo):
    max_id = db.session.query(func.max(Entreprise.id_Entreprise)).scalar()
    next_id = max_id + 1 if max_id is not None else 1
    entreprise = Entreprise(id_Entreprise=next_id,nom=nom,adresse=adresse,description=description,email=email,tel=tel,lien_logo=lien_logo) 
    entreprise.save_to_db()
    
    
def update_entreprise(_id_Entreprise, _nom,_adresse,_description,_email,_tel,_lien_logo):
    entreprise_to_update = Entreprise.query.filter_by(id_Entreprise=_id_Entreprise).first()
    if entreprise_to_update:
        entreprise_to_update.nom = _nom
        entreprise_to_update.adresse = _adresse
        entreprise_to_update.description = _description
        entreprise_to_update.email = _email
        entreprise_to_update.tel = _tel
        entreprise_to_update.lien_logo = _lien_logo
        entreprise_to_update.save_to_db()
        return True
    return False
   
# def delete_entreprise(_id_Entreprise):
#     entreprise_to_delete=Entreprise.query.filter_by(id_Entreprise=_id_Entreprise).first()
#     if entreprise_to_delete:
#         entreprise_to_delete.delete_from_db() 
#         return True
#     return False      


def delete_entreprise(_id_Entreprise):
    entreprise_to_delete = Entreprise.query.filter_by(id_Entreprise=_id_Entreprise).first()
    if entreprise_to_delete:
        deleted_id = entreprise_to_delete.id_Entreprise
        entreprise_to_delete.delete_from_db()

        # Obtenez la liste des entreprises après l'ID spécifié
        entreprises_a_mettre_a_jour = Entreprise.query.filter(Entreprise.id_Entreprise > deleted_id).all()

        # Mettez à jour les ID des entreprises suivantes
        new_id = deleted_id
        for entreprise in entreprises_a_mettre_a_jour:
            entreprise.id_Entreprise = new_id
            new_id += 1
            entreprise.save_to_db()

        return True
    return False
