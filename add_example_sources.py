from backend.app import create_app
from backend.app.models import Source

# Lista de fontes de exemplo
SOURCES = [
    # RSS Feeds padrão
    {
        'name': 'STJ Notícias',
        'url': 'https://res.stj.jus.br/hrestp-c-portalp/RSS.xml',
        'type': 'rss'
    },
    
    # Páginas do Governo (usando GovBrExtractor)
    {
        'name': 'Cultura e Esportes',
        'url': 'https://www.gov.br/pt-br/noticias/cultura-artes-historia-e-esportes',
        'type': 'webpage',
        'config': {
            'extractor': 'govbr',
            'categoria': 'Cultura'
        }
    },
    {
        'name': 'Educação e Pesquisa',
        'url': 'https://www.gov.br/pt-br/noticias/educacao-e-pesquisa',
        'type': 'webpage',
        'config': {
            'extractor': 'govbr',
            'categoria': 'Educação'
        }
    },
    {
        'name': 'Ciência e Tecnologia',
        'url': 'https://www.gov.br/pt-br/noticias/ciencia-e-tecnologia',
        'type': 'webpage',
        'config': {
            'extractor': 'govbr',
            'categoria': 'Ciência'
        }
    },
    
    # Exemplo de API REST
    {
        'name': 'Brasil API - Feriados',
        'url': 'https://brasilapi.com.br/api/feriados/v1/2024',
        'type': 'api',
        'config': {
            'headers': {
                'User-Agent': 'Mozilla/5.0'
            },
            'date_field': 'date',
            'title_field': 'name',
            'description_field': 'type'
        }
    },
    
    # Exemplo de página web genérica
    {
        'name': 'FAPESP',
        'url': 'https://fapesp.br/oportunidades',
        'type': 'webpage',
        'config': {
            'selectors': {
                'articles': '.opportunity-item',
                'title': 'h3',
                'description': '.description',
                'date': '.date'
            }
        }
    }
]

def add_sources():
    app = create_app()
    with app.app_context():
        print("Adicionando fontes de exemplo...")
        
        for source_data in SOURCES:
            try:
                # Verifica se a fonte já existe
                existing = Source.query.filter_by(url=source_data['url']).first()
                if not existing:
                    Source.create_source(
                        name=source_data['name'],
                        url=source_data['url'],
                        type=source_data['type'],
                        config=source_data.get('config', {})
                    )
                    print(f"Adicionada fonte: {source_data['name']}")
                else:
                    print(f"Fonte já existe: {source_data['name']}")
                    
            except Exception as e:
                print(f"Erro ao adicionar fonte {source_data['name']}: {str(e)}")
                continue
        
        print("\nFontes adicionadas com sucesso!")

if __name__ == '__main__':
    add_sources()
