from . import db
from datetime import datetime

class Edital(db.Model):
    __tablename__ = 'editais'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(512), nullable=False)
    data_publicacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_vencimento = db.Column(db.DateTime)
    categoria = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    fonte = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'link': self.link,
            'data_publicacao': self.data_publicacao.isoformat() if self.data_publicacao else None,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'fonte': self.fonte
        }

class Source(db.Model):
    __tablename__ = 'sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(512), nullable=False, unique=True)
    type = db.Column(db.String(20), nullable=False)  # rss, webpage, api
    active = db.Column(db.Boolean, default=True)
    last_scrape = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configurações extras em JSON
    config = db.Column(db.JSON, default=dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'type': self.type,
            'active': self.active,
            'last_scrape': self.last_scrape.isoformat() if self.last_scrape else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'config': self.config or {}
        }
        
    @classmethod
    def create_source(cls, name, url, type='rss', config=None):
        """Helper para criar uma nova fonte com configurações"""
        source = cls(
            name=name,
            url=url,
            type=type,
            config=config or {}
        )
        db.session.add(source)
        try:
            db.session.commit()
            return source
        except Exception as e:
            db.session.rollback()
            raise e
