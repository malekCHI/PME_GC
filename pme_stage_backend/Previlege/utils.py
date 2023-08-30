from functools import wraps

from Previlege.models import PrevilegeModel


def get_all_previlege():
     return {'previlege': list(map(lambda x: x.serialize(), PrevilegeModel.query.all()))}

 
def get_previlege(_id_previlege):
    return {'previlege': list(map(lambda x: x.serialize(), PrevilegeModel.query.filter_by(id_previlege=_id_previlege).first()))}


def add_previlege(nom, description,creation_date,profiles):
    previlege = PrevilegeModel(nom=nom,description=description,creation_date=creation_date,profiles=profiles) 
    previlege.save_to_db()


def update_previlege(_id_previlege, _nom,_description,_creation_date):
    previlege_to_update = PrevilegeModel.query.filter_by(id_previlege=_id_previlege).first()
    if previlege_to_update:
        previlege_to_update.nom = _nom
        previlege_to_update.description = _description
        previlege_to_update.creation_date = _creation_date
        previlege_to_update.save_to_db()
        return True
    return False
   
def delete_previlege(_id_previlege):
    previlege_delete=PrevilegeModel.query.filter_by(id_previlege=_id_previlege).first()
    if previlege_delete:
        previlege_delete.delete_from_db() 
        return True
    return False      
