from backend.app import create_app
from backend.app.models import Source

app = create_app()

with app.app_context():
    sources = Source.query.filter_by(type='rss', active=True).all()
    print('Fontes RSS ativas:')
    for source in sources:
        print(f'- {source.name}: {source.url}')
