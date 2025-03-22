from app import db
from datetime import datetime

class ReferenceData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text)  # Comma-separated keywords
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ReferenceData {self.title}>'

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    reference_id = db.Column(db.Integer, db.ForeignKey('reference_data.id'), nullable=True)
    score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reference = db.relationship('ReferenceData', backref=db.backref('assignments', lazy=True))
    
    def __repr__(self):
        return f'<Assignment {self.id}>'
