import feedparser
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from .models import Edital, Source, db
from flask import current_app
import re
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin
import urllib3

# Desabilitar avisos SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EditalScraper:
    def __init__(self, app=None):
        self.app = app
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def extract_date(self, text: str) -> Optional[datetime]:
        """Extrai data de um texto em português"""
        if not text:
            return None
            
        # Padrões comuns de data em português
        patterns = [
            r'(\d{2}/\d{2}/\d{4})',  # dd/mm/yyyy
            r'(\d{1,2}\s+de\s+[^\s]+\s+de\s+\d{4})',  # dd de mês de yyyy
            r'até\s+(\d{2}/\d{2}/\d{4})',  # até dd/mm/yyyy
            r'prazo.*?(\d{2}/\d{2}/\d{4})',  # prazo... dd/mm/yyyy
            r'(\d{2}\s+[^\s]+\s+\d{4})'  # dd month yyyy (formato Câmara)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    if '/' in date_str:
                        return datetime.strptime(date_str, '%d/%m/%Y')
                    else:
                        # Converter mês em português para número
                        months = {
                            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                            'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
                            'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
                            'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
                        }
                        
                        date_str = date_str.lower()
                        for month_name, month_num in months.items():
                            date_str = date_str.replace(month_name, str(month_num))
                        
                        # Tenta diferentes formatos de data
                        for fmt in ['%d %m %Y', '%d de %m de %Y']:
                            try:
                                return datetime.strptime(date_str, fmt)
                            except ValueError:
                                continue
                except ValueError:
                    pass
        return None

    def get_full_content(self, url: str) -> Optional[str]:
        """Obtém o conteúdo completo de uma página de edital"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove tags de script e style
            for script in soup(['script', 'style']):
                script.decompose()
                
            return ' '.join(soup.stripped_strings)
        except Exception as e:
            current_app.logger.error(f"Error getting content from {url}: {str(e)}")
            return None

    def parse_rss_feed(self, source: Source) -> List[Dict[str, Any]]:
        """Parse um feed RSS"""
        try:
            # Fazer a requisição seguindo redirecionamentos
            response = self.session.get(source.url, timeout=10)
            response.raise_for_status()
            
            # Usar o feedparser com a URL final após redirecionamentos
            feed = feedparser.parse(response.text)
            editais = []
            
            if not hasattr(feed, 'entries'):
                current_app.logger.error(f"No entries found in RSS feed {source.url}")
                return []
            
            keywords = [
                # Editais e oportunidades
                'edital', 'chamada pública', 'seleção', 'concurso', 'prêmio',
                'inscrição', 'inscrições', 'oportunidade', 'participação',
                # Cultura e arte
                'cultura', 'cultural', 'arte', 'artista', 'artístico',
                'música', 'teatro', 'dança', 'cinema', 'literatura',
                'patrimônio', 'museu', 'biblioteca', 'exposição',
                # Financiamento e apoio
                'fomento', 'incentivo', 'financiamento', 'patrocínio', 'apoio',
                'lei rouanet', 'proac', 'fundo', 'recurso'
            ]
            
            for entry in feed.entries:
                try:
                    # Verifica se o título ou descrição contém palavras-chave
                    title = entry.title.lower() if hasattr(entry, 'title') else ''
                    description = entry.description.lower() if hasattr(entry, 'description') else ''
                    
                    # Tenta obter o conteúdo de várias formas
                    content = ''
                    if hasattr(entry, 'content'):
                        try:
                            content = entry.content[0].value.lower()
                        except (IndexError, AttributeError):
                            pass
                    
                    # Combina todo o conteúdo para busca
                    full_text = f"{title} {description} {content}"
                    
                    # Verifica se alguma palavra-chave está presente
                    if any(keyword.lower() in full_text for keyword in keywords):
                        # Tenta extrair a data de vencimento de várias fontes
                        data_venc = None
                        content_full = content or description
                        
                        # Tenta extrair a data do conteúdo completo
                        if content_full:
                            data_venc = self.extract_date(content_full)
                        
                        # Se não encontrou no conteúdo, tenta obter o conteúdo completo da página
                        if not data_venc and hasattr(entry, 'link'):
                            page_content = self.get_full_content(entry.link)
                            if page_content:
                                data_venc = self.extract_date(page_content)
                                content_full = page_content
                        
                        # Usa a data de publicação como fallback
                        if not data_venc and hasattr(entry, 'published_parsed'):
                            try:
                                data_venc = datetime(*entry.published_parsed[:6])
                            except (AttributeError, TypeError):
                                pass
                        
                        link = entry.link if hasattr(entry, 'link') else ''
                        if not link.startswith(('http://', 'https://')):
                            link = urljoin(source.url, link)
                        
                        editais.append({
                            'nome': entry.title,
                            'link': link,
                            'descricao': content_full[:500] + '...' if content_full and len(content_full) > 500 else content_full,
                            'data_vencimento': data_venc,
                            'data_publicacao': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else None,
                            'categoria': self.extract_categoria(content_full) if content_full else None,
                            'fonte': source.name
                        })
                except Exception as e:
                    current_app.logger.error(f"Error processing entry from {source.url}: {str(e)}")
                    continue
            
            return editais
            
        except Exception as e:
            current_app.logger.error(f"Error parsing RSS feed {source.url}: {str(e)}")
            return []

    def extract_categoria(self, text: str) -> Optional[str]:
        """Extrai categoria do texto baseado em palavras-chave"""
        if not text:
            return None
            
        text = text.lower()
        
        categorias = {
            'Música': ['música', 'musical', 'músico', 'musicista', 'concerto', 'show'],
            'Teatro': ['teatro', 'teatral', 'dramaturgia', 'cênico', 'espetáculo'],
            'Dança': ['dança', 'bailarino', 'coreografia'],
            'Cinema': ['cinema', 'audiovisual', 'filme', 'curta-metragem'],
            'Literatura': ['literatura', 'livro', 'escritor', 'poesia', 'conto'],
            'Artes Visuais': ['artes visuais', 'exposição', 'galeria', 'artista plástico'],
            'Patrimônio': ['patrimônio', 'histórico', 'cultural', 'preservação'],
            'Fomento': ['fomento', 'incentivo', 'financiamento', 'patrocínio'],
            'Formação': ['formação', 'workshop', 'oficina', 'curso', 'capacitação'],
        }
        
        for categoria, keywords in categorias.items():
            if any(keyword in text for keyword in keywords):
                return categoria
                
        if 'edital' in text:
            return 'Edital'
        elif 'prêmio' in text:
            return 'Prêmio'
        elif 'concurso' in text:
            return 'Concurso'
            
        return 'Outros'

    def parse_rss_feeds(self) -> int:
        """Processa todas as fontes ativas"""
        current_app.logger.info("Iniciando processamento de feeds RSS...")
        sources = Source.query.filter_by(active=True).all()
        current_app.logger.info(f"Encontradas {len(sources)} fontes ativas")
        
        total_new = 0
        
        for source in sources:
            try:
                current_app.logger.info(f"Processando fonte: {source.name} ({source.url})")
                
                # Parse do feed RSS
                editais = self.parse_rss_feed(source)
                
                # Adiciona novos editais ao banco
                for edital_data in editais:
                    # Verifica se o edital já existe
                    existing = Edital.query.filter_by(link=edital_data['link']).first()
                    if not existing:
                        edital = Edital(
                            nome=edital_data['nome'],
                            link=edital_data['link'],
                            descricao=edital_data['descricao'],
                            data_vencimento=edital_data['data_vencimento'],
                            data_publicacao=edital_data['data_publicacao'],
                            categoria=edital_data['categoria'],
                            fonte=edital_data['fonte']
                        )
                        db.session.add(edital)
                        total_new += 1
                
                db.session.commit()
                current_app.logger.info(f"Encontrados {len(editais)} editais em {source.name}")
                
            except Exception as e:
                current_app.logger.error(f"Erro ao processar fonte {source.name}: {str(e)}")
                db.session.rollback()
                continue
        
        return total_new
