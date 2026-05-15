from datetime import datetime
from app import db

skill_hero = db.Table('skill_hero',
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True),
    db.Column('hero_id', db.Integer, db.ForeignKey('heroes.id'), primary_key=True)
)

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    skill_type = db.Column(db.String(20), default='普通技')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': [self.skill_type]
        }

class Hero(db.Model):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    camp = db.Column(db.String(20), default='群')
    hp = db.Column(db.Integer, default=4)
    tag = db.Column(db.String(20), default='标')
    created_at = db.Column(db.DateTime, default=datetime.now)

    skills = db.relationship('Skill', secondary=skill_hero, backref='heroes')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'camp': self.camp,
            'hp': self.hp,
            'skills': [s.name for s in self.skills]
        }

class SkillPool(db.Model):
    __tablename__ = 'skill_pool'

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(50), nullable=False)
    hero_name = db.Column(db.String(50), nullable=True)
    added_at = db.Column(db.DateTime, default=datetime.now)

class CurrentSkill(db.Model):
    __tablename__ = 'current_skills'

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(50), nullable=False)
    skill_type = db.Column(db.String(20), default='武将技')
    acquired_from = db.Column(db.String(50))
    acquired_at = db.Column(db.DateTime, default=datetime.now)

class Marker(db.Model):
    __tablename__ = 'markers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {'name': self.name, 'count': self.count}

class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    card_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.card_type,
            'description': self.description
        }

class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    equip_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.equip_type,
            'description': self.description,
            'is_active': self.is_active
        }

class GameState(db.Model):
    __tablename__ = 'game_state'

    id = db.Column(db.Integer, primary_key=True)
    current_hero = db.Column(db.String(50))
    current_hp = db.Column(db.Integer, default=4)
    max_hp = db.Column(db.Integer, default=4)
    current_hero_skills = db.Column(db.Text)
    selected_markers = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class HeroPool(db.Model):
    __tablename__ = 'hero_pool'

    id = db.Column(db.Integer, primary_key=True)
    hero_name = db.Column(db.String(50), nullable=False)
    pool_hero_name = db.Column(db.String(50), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.now)

class HeroMarkerPool(db.Model):
    __tablename__ = 'hero_marker_pool'

    id = db.Column(db.Integer, primary_key=True)
    hero_name = db.Column(db.String(50), nullable=False)
    marker_name = db.Column(db.String(50), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.now)

class HeroDetail(db.Model):
    __tablename__ = 'hero_details'

    id = db.Column(db.Integer, primary_key=True)
    hero_name = db.Column(db.String(50), nullable=False, unique=True)
    avatar_url = db.Column(db.String(255))
    rating = db.Column(db.Float, default=0)
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)