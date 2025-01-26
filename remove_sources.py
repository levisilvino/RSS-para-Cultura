from backend.app import create_app, db
from backend.app.models import Source

app = create_app()

with app.app_context():
    # Remove todas as fontes que não são as originais
    sources = Source.query.filter(
        ~Source.url.in_([
            'https://www.gov.br/pt-br/noticias/RSS',
            'https://res.stj.jus.br/hrestp-c-portalp/RSS.xml',
            'https://www.gov.br/governodigital/pt-br/noticias/RSS'
        ])
    ).all()
    
    for source in sources:
        print(f"Removendo fonte: {source.name}")
        db.session.delete(source)
    
    db.session.commit()
    print("\nFontes removidas com sucesso!")
