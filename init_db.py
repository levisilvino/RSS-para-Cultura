from backend.app import create_app, db
from backend.app.models import Source, Edital

def init_db():
    app = create_app()
    with app.app_context():
        # Recria todas as tabelas
        db.drop_all()
        db.create_all()
        print("Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    init_db()
