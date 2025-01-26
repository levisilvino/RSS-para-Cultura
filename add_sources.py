from backend.app import create_app, db
from backend.app.models import Source

# Lista de fontes RSS do governo
SOURCES = [
    {
        'name': 'Serviços para o Cidadão',
        'url': 'https://www.gov.br/pt-br/noticias/servicos-para-o-cidadao/RSS'
    },
    {
        'name': 'COP30',
        'url': 'https://www.gov.br/pt-br/noticias/cop30/RSS'
    },
    {
        'name': 'Forças Armadas',
        'url': 'https://www.gov.br/pt-br/noticias/forcas-armadas/RSS'
    },
    {
        'name': 'Meio Ambiente e Clima',
        'url': 'https://www.gov.br/pt-br/noticias/meio-ambiente-e-clima/RSS'
    },
    {
        'name': 'Viagens e Turismo',
        'url': 'https://www.gov.br/pt-br/noticias/viagens-e-turismo/RSS'
    },
    {
        'name': 'Finanças e Gestão Pública',
        'url': 'https://www.gov.br/pt-br/noticias/financas-impostos-e-gestao-publica/RSS'
    },
    {
        'name': 'Assistência Social',
        'url': 'https://www.gov.br/pt-br/noticias/assistencia-social/RSS'
    },
    {
        'name': 'Justiça e Segurança',
        'url': 'https://www.gov.br/pt-br/noticias/justica-e-seguranca/RSS'
    },
    {
        'name': 'Educação e Pesquisa',
        'url': 'https://www.gov.br/pt-br/noticias/educacao-e-pesquisa/RSS'
    },
    {
        'name': 'Cultura e Esportes',
        'url': 'https://www.gov.br/pt-br/noticias/cultura-artes-historia-e-esportes/RSS'
    },
    {
        'name': 'Saúde',
        'url': 'https://www.gov.br/pt-br/noticias/saude-e-vigilancia-sanitaria/RSS'
    },
    {
        'name': 'Trabalho e Previdência',
        'url': 'https://www.gov.br/pt-br/noticias/trabalho-e-previdencia/RSS'
    },
    {
        'name': 'Energia e Mineração',
        'url': 'https://www.gov.br/pt-br/noticias/energia-minerais-e-combustiveis/RSS'
    },
    {
        'name': 'Ciência e Tecnologia',
        'url': 'https://www.gov.br/pt-br/noticias/ciencia-e-tecnologia/RSS'
    },
    {
        'name': 'Comunicação',
        'url': 'https://www.gov.br/pt-br/noticias/comunicacao/RSS'
    },
    {
        'name': 'Agricultura e Pecuária',
        'url': 'https://www.gov.br/pt-br/noticias/agricultura-e-pecuaria/RSS'
    },
    {
        'name': 'Trânsito e Transportes',
        'url': 'https://www.gov.br/pt-br/noticias/transito-e-transportes/RSS'
    }
]

def add_sources():
    app = create_app()
    with app.app_context():
        print("Adicionando fontes RSS...")
        for source_data in SOURCES:
            # Verifica se a fonte já existe
            existing = Source.query.filter_by(url=source_data['url']).first()
            if not existing:
                source = Source(
                    name=source_data['name'],
                    url=source_data['url'],
                    type='rss',
                    active=True
                )
                db.session.add(source)
                print(f"Adicionada fonte: {source_data['name']}")
            else:
                print(f"Fonte já existe: {source_data['name']}")
        
        try:
            db.session.commit()
            print("\nTodas as fontes foram adicionadas com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"\nErro ao adicionar fontes: {str(e)}")

if __name__ == '__main__':
    add_sources()
