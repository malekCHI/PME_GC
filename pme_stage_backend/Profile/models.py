from db import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

class ProfileModel(db.Model):
    __tablename__ = "profiles"
    id_profile = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(), unique=True,  nullable=False)
    description = db.Column(db.String())
    creation_date = db.Column(db.DateTime, default=datetime.utcnow) 
    previleges = db.relationship("PrevilegeModel", secondary="profile_previlege", back_populates="profiles")
    
    def __init__(self,nom,description,creation_date):
        self.nom = nom
        self.description = description
        self.creation_date = creation_date
    
    def serialize(self,visited=None):
        visited = visited or set()
        if self in visited:
            return {'id_profile': self.id_profile}

        visited.add(self)
        return {
                'id_profile': self.id_profile,
                'nom': self.nom,
                'description': self.description,
                'creation_date': self.creation_date.strftime("%d-%b-%Y"),
                'previleges': list(map(lambda previlege: previlege.serialize(visited), self.previleges)),
                }
       
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

