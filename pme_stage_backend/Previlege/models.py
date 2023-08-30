from db import db
from datetime import datetime
class PrevilegeModel(db.Model):
    __tablename__ = "previlege"
    id_previlege = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(), unique=True,  nullable=False)
    description = db.Column(db.String())
    creation_date = db.Column(db.DateTime, default=datetime.utcnow) 
    profiles = db.relationship("ProfileModel", secondary="profile_previlege", back_populates="previleges")
    users = db.relationship("UserModel", secondary="user_previlege", back_populates="previleges")

    def __init__(self,nom,description,creation_date,profiles):
        self.nom = nom
        self.description = description
        self.creation_date = creation_date
        self.profiles = profiles
    
    def serialize(self,visited=None):
        visited = visited or set()
        if self in visited:
            return {'id_previlege': self.id_previlege}

        visited.add(self)
        return {
                'id_previlege': self.id_previlege,
                'nom': self.nom,
                'description': self.description,
                'creation_date': self.creation_date.strftime("%d-%b-%Y"),
                'profiles': list(map(lambda profile: profile.serialize(visited), self.profiles)),
                'users': list(map(lambda user: user.serialize(visited), self.users)),
                }
       
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    
    #   join many to many 
class profile_previlege(db.Model):
    __tablename__ = 'profile_previlege'
    id_profile = db.Column(db.Integer, db.ForeignKey('profiles.id_profile'), primary_key=True)
    id_previlege = db.Column(db.Integer, db.ForeignKey('previlege.id_previlege'), primary_key=True)