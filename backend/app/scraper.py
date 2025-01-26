import feedparser
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
from .models import Edital, Source, db
from flask import current_app
import re
from typing import List, Dict, Optional, Any, Tuple
from urllib.parse import urljoin
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import html
from dateutil import parser as date_parser
import logging
import time

# Desabilitar avisos SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ContentExtractor:
    """Classe base para diferentes estratégias de extração de conteúdo"""
    def extract(self, url: str) -> Tuple[str, Optional[datetime]]:
        raise NotImplementedError

class RSSExtractor(ContentExtractor):
    """Extrai conteúdo de feeds RSS padrão"""
    def extract(self, url: str) -> Tuple[str, Optional[datetime]]:
        feed = feedparser.parse(url)
        entries = []
        for entry in feed.entries:
            title = entry.get('title', '')
            description = entry.get('description', '')
            link = entry.get('link', '')
            date = entry.get('published_parsed')
            if date:
                date = datetime(*date[:6])
            entries.append({
                'title': title,
                'description': description,
                'link': link,
                'date': date
            })
        return entries

class GovBrExtractor(ContentExtractor):
    """Extrator específico para o site do governo"""
    def extract(self, url: str) -> List[Dict]:
        # Remove /RSS do final da URL se presente
        base_url = url.replace('/RSS', '')
        
        # Faz request para a página
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        entries = []
        # Encontra todas as notícias na página
        articles = soup.find_all('article')
        
        for article in articles:
            # Extrai informações básicas
            title_elem = article.find('h2')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            link = title_elem.find('a')['href'] if title_elem.find('a') else None
            if not link:
                continue
                
            # Extrai data da URL ou do conteúdo
            date_match = re.search(r'/(\d{4})/(\d{2})/', link)
            if date_match:
                year, month = map(int, date_match.groups())
                date = datetime(year, month, 1)
            else:
                date = None
                
            # Busca descrição
            description = ''
            desc_elem = article.find('div', class_='summary')
            if desc_elem:
                description = desc_elem.text.strip()
                
            entries.append({
                'title': title,
                'description': description,
                'link': link,
                'date': date
            })
            
        return entries

class WebPageExtractor(ContentExtractor):
    """Extrai conteúdo de páginas web genéricas"""
    def extract(self, url: str) -> List[Dict]:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove tags desnecessárias
        for tag in soup(['script', 'style']):
            tag.decompose()
            
        # Tenta encontrar o conteúdo principal
        content = None
        for selector in ['article', 'main', '.content', '#content']:
            content = soup.select_one(selector)
            if content:
                break
                
        if not content:
            content = soup.body
            
        # Extrai texto limpo
        text = content.get_text(separator='\n').strip()
        
        # Tenta encontrar a data
        date = None
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}\s+de\s+[a-zA-Zç]+\s+de\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date = date_parser.parse(match.group(), fuzzy=True)
                    break
                except:
                    continue
                    
        return [{
            'title': soup.title.string if soup.title else '',
            'description': text[:500],
            'link': url,
            'date': date
        }]

class APIExtractor(ContentExtractor):
    """Extrai conteúdo de APIs REST"""
    def __init__(self, headers=None, params=None):
        self.headers = headers or {}
        self.params = params or {}
        
    def extract(self, url: str) -> List[Dict]:
        response = requests.get(url, headers=self.headers, params=self.params)
        data = response.json()
        
        # Implementação base - deve ser customizada para cada API
        entries = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # Tenta encontrar a lista de items em campos comuns
            for field in ['items', 'data', 'results', 'content']:
                if field in data:
                    items = data[field]
                    break
            else:
                items = [data]
        else:
            items = []
            
        for item in items:
            if isinstance(item, dict):
                title = item.get('title', '')
                description = item.get('description', '')
                link = item.get('link', '')
                date_str = item.get('date') or item.get('created_at') or item.get('published_at')
                
                date = None
                if date_str:
                    try:
                        date = date_parser.parse(date_str)
                    except:
                        pass
                        
                entries.append({
                    'title': title,
                    'description': description,
                    'link': link,
                    'date': date
                })
                
        return entries

class EditalScraper:
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.extractors = {
            'rss': RSSExtractor(),
            'govbr': GovBrExtractor(),
            'webpage': WebPageExtractor(),
            'api': APIExtractor()
        }
        
    def get_extractor(self, source: Source) -> ContentExtractor:
        """Retorna o extrator apropriado para a fonte"""
        if source.type == 'rss':
            if 'gov.br' in source.url:
                return self.extractors['govbr']
            return self.extractors['rss']
        elif source.type == 'webpage':
            return self.extractors['webpage']
        elif source.type == 'api':
            return self.extractors['api']
        else:
            raise ValueError(f"Tipo de fonte não suportado: {source.type}")
            
    def parse_source(self, source: Source) -> List[Dict]:
        """Processa uma fonte e retorna os editais encontrados"""
        try:
            extractor = self.get_extractor(source)
            entries = extractor.extract(source.url)
            
            editais = []
            for entry in entries:
                edital = {
                    'nome': entry['title'],
                    'descricao': entry['description'],
                    'link': entry['link'],
                    'fonte': source.name,
                    'data_publicacao': entry['date'] or datetime.now()
                }
                
                # Tenta extrair data de vencimento e categoria
                data_vencimento = self.extract_data_vencimento(entry['description'])
                if data_vencimento:
                    edital['data_vencimento'] = data_vencimento
                    
                categoria = self.extract_categoria(entry['description'])
                if categoria:
                    edital['categoria'] = categoria
                    
                editais.append(edital)
                
            return editais
            
        except Exception as e:
            self.logger.error(f"Erro ao processar fonte {source.name}: {str(e)}")
            return []

    def _setup_logging(self):
        """Configura logging detalhado"""
        self.logger = logging.getLogger('EditalScraper')
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _create_session(self) -> requests.Session:
        """Cria uma sessão HTTP com retry e timeouts apropriados"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.verify = False
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session

    def clean_text(self, text: str) -> str:
        """Limpa e formata o texto removendo espaços extras e caracteres especiais"""
        if not text:
            return ""
        # Decodifica entidades HTML
        text = html.unescape(text)
        # Remove tags HTML
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove caracteres especiais e espaços extras
        text = re.sub(r'\s+', ' ', text)
        # Remove espaços no início e fim
        return text.strip()

    def extract_date(self, text: str) -> Optional[datetime]:
        """Extrai data do texto usando vários formatos"""
        if not text:
            return None
            
        # Lista de padrões de data comuns em português
        date_patterns = [
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})',  # dd/mm/yyyy ou dd-mm-yyyy
            r'(\d{1,2})\s+de\s+([^\s]+)\s+de\s+(\d{2,4})',  # dd de mês de yyyy
            r'até\s+(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})',  # até dd/mm/yyyy
            r'prazo[:\s]+(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})',  # prazo: dd/mm/yyyy
            r'encerramento[:\s]+(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})',  # encerramento: dd/mm/yyyy
            r'vencimento[:\s]+(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})',  # vencimento: dd/mm/yyyy
        ]

        # Mapeamento de nomes de meses em português
        month_names = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
            'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
            'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
            'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
        }

        text = text.lower()
        
        # Tenta cada padrão de data
        for pattern in date_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    if len(match.groups()) == 3:
                        day, month, year = match.groups()
                        
                        # Converte mês por extenso para número
                        if month.isalpha():
                            if month not in month_names:
                                continue
                            month = month_names[month]
                        
                        # Converte para inteiros
                        day = int(day)
                        month = int(month)
                        year = int(year)
                        
                        # Ajusta o ano se necessário
                        if year < 100:
                            year += 2000 if year < 50 else 1900
                        
                        # Valida a data
                        try:
                            date = datetime(year, month, day)
                            # Ignora datas muito antigas ou muito futuras
                            if date.year >= 2020 and date.year <= 2030:
                                return date
                        except ValueError:
                            continue
                except (ValueError, AttributeError) as e:
                    self.logger.warning(f"Error parsing date: {str(e)}")
                    continue
                    
        return None

    def get_full_content(self, url: str) -> Tuple[Optional[str], Optional[datetime]]:
        """Obtém o conteúdo completo de uma URL com melhor tratamento de erros"""
        try:
            # Configura headers para simular um navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
            }

            # Tenta fazer a requisição com retry e timeout
            for attempt in range(3):
                try:
                    response = self.session.get(
                        url, 
                        headers=headers,
                        timeout=10,
                        verify=False
                    )
                    
                    # Se for erro 520 ou outro erro do servidor, tenta próxima tentativa
                    if response.status_code in [520, 502, 503, 504]:
                        if attempt < 2:  # Se não for a última tentativa
                            time.sleep(1)  # Espera 1 segundo antes de tentar novamente
                            continue
                    
                    response.raise_for_status()
                    break
                except (requests.RequestException, TimeoutError) as e:
                    if attempt == 2:  # Se for a última tentativa
                        raise e
                    time.sleep(1)
            
            # Parse do conteúdo
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove elementos desnecessários
            for elem in soup.select('script, style, nav, header, footer, iframe'):
                elem.decompose()
            
            # Extrai o texto principal
            content = ""
            
            # Tenta diferentes seletores comuns para conteúdo principal
            selectors = [
                'article', '.content', '.article-content', 
                'main', '#main-content', '.main-content',
                '.post-content', '.entry-content'
            ]
            
            for selector in selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    content = main_content.get_text(strip=True)
                    break
            
            # Se não encontrou com seletores, pega todo o body
            if not content:
                content = soup.get_text(strip=True)
            
            # Limpa o conteúdo
            content = self.clean_text(content)
            
            # Extrai possível data da página
            date = None
            date_selectors = [
                'time', '.date', '.post-date', 
                'meta[property="article:published_time"]',
                'meta[name="date"]'
            ]
            
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    try:
                        if date_elem.name == 'meta':
                            date_str = date_elem.get('content')
                        else:
                            date_str = date_elem.get('datetime') or date_elem.get_text()
                        
                        if date_str:
                            date = date_parser.parse(date_str)
                            break
                    except (ValueError, TypeError):
                        continue
            
            return content, date
            
        except Exception as e:
            self.logger.error(f"Error getting content from {url}: {str(e)}")
            return None, None

    def process_feed_entries(self, entries: List[Any], source: Source) -> List[Dict[str, Any]]:
        """Processa múltiplas entradas do feed mantendo o contexto da aplicação"""
        editais = []
        with self.app.app_context():
            for entry in entries:
                try:
                    result = self.process_feed_entry(entry, source)
                    if result:
                        editais.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing entry: {str(e)}")
        return editais

    def process_feed_entry_with_context(self, entry: Any, source: Source) -> Optional[Dict[str, Any]]:
        """Wrapper para processar entrada com contexto da aplicação"""
        with self.app.app_context():
            return self.process_feed_entry(entry, source)

    def process_feed_entry(self, entry: Any, source: Source) -> Optional[Dict[str, Any]]:
        """Processa uma entrada do feed RSS"""
        try:
            # Verifica se entry é None
            if not entry:
                self.logger.error("Entry is None")
                return None

            # Extrai e limpa o título com verificação de None
            title = ""
            if hasattr(entry, 'title') and entry.title:
                title = self.clean_text(entry.title)
            
            if not title:
                self.logger.warning("Entry has no title, skipping")
                return None
            
            # Combina e limpa a descrição e conteúdo com verificação de None
            description = ""
            if hasattr(entry, 'description') and entry.description:
                description = self.clean_text(entry.description)
            
            content = ""
            if hasattr(entry, 'content') and entry.content:
                try:
                    if isinstance(entry.content, list) and len(entry.content) > 0:
                        content_item = entry.content[0]
                        if hasattr(content_item, 'value'):
                            content = self.clean_text(content_item.value)
                except (IndexError, AttributeError) as e:
                    self.logger.warning(f"Error extracting content: {str(e)}")
            
            # Combina todo o conteúdo para busca
            full_text = f"{title} {description} {content}".lower()
            
            # Verifica relevância com base em palavras-chave
            if not self.is_relevant_content(full_text):
                return None
            
            # Processa o link com verificação de None
            link = ""
            if hasattr(entry, 'link') and entry.link:
                link = entry.link
                if not link.startswith(('http://', 'https://')):
                    link = urljoin(source.url, link)
            
            if not link:
                self.logger.warning("Entry has no link, skipping")
                return None
            
            # Obtém conteúdo completo e possível data
            content_full = None
            page_date = None
            
            try:
                content_full, page_date = self.get_full_content(link)
            except Exception as e:
                self.logger.warning(f"Error getting full content, using feed content: {str(e)}")
                # Se falhar ao obter conteúdo completo, usa o conteúdo do feed
                content_full = description or content or title
            
            # Determina a data de vencimento com verificações de None
            data_venc = None
            
            # Tenta extrair a data em ordem de prioridade
            date_sources = [
                (page_date, "página"),
                (self.extract_date(content_full), "conteúdo completo"),
                (self.extract_date(description), "descrição"),
                (self.extract_date(title), "título")
            ]
            
            for date, source_name in date_sources:
                if date:
                    data_venc = date
                    self.logger.info(f"Data encontrada no {source_name}: {date}")
                    break
            
            # Tenta usar a data de publicação como fallback
            if not data_venc and hasattr(entry, 'published_parsed'):
                try:
                    if entry.published_parsed:
                        data_venc = datetime(*entry.published_parsed[:6])
                        self.logger.info(f"Usando data de publicação: {data_venc}")
                except (AttributeError, TypeError, ValueError) as e:
                    self.logger.warning(f"Error parsing published date: {str(e)}")
            
            # Se ainda não tem data, usa data atual + 30 dias
            if not data_venc:
                data_venc = datetime.now() + timedelta(days=30)
                self.logger.info(f"Usando data padrão: {data_venc}")
            
            # Prepara a descrição final
            final_description = content_full or description or title
            if final_description and len(final_description) > 500:
                final_description = final_description[:497] + "..."
            
            # Prepara a data de publicação
            data_publicacao = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    data_publicacao = datetime(*entry.published_parsed[:6])
                except (TypeError, ValueError) as e:
                    self.logger.warning(f"Error parsing publication date: {str(e)}")
            
            return {
                'nome': title,
                'link': link,
                'descricao': final_description,
                'data_vencimento': data_venc,
                'data_publicacao': data_publicacao,
                'categoria': self.extract_categoria(content_full or description or ""),
                'fonte': source.name
            }
        except Exception as e:
            self.logger.error(f"Error processing entry: {str(e)}")
            return None

    def is_relevant_content(self, text: str) -> bool:
        """Verifica se o conteúdo é relevante baseado em palavras-chave"""
        keywords = {
            # Prioridade alta (precisa ter pelo menos uma)
            'high_priority': [
                'edital', 'chamada pública', 'seleção', 'concurso',
                'prêmio', 'inscrição', 'inscrições'
            ],
            # Prioridade média (precisa ter pelo menos duas)
            'medium_priority': [
                'cultura', 'cultural', 'arte', 'artista', 'artístico',
                'música', 'teatro', 'dança', 'cinema', 'literatura',
                'patrimônio', 'museu', 'biblioteca', 'exposição'
            ],
            # Prioridade baixa (aumenta relevância)
            'low_priority': [
                'fomento', 'incentivo', 'financiamento', 'patrocínio',
                'apoio', 'lei rouanet', 'proac', 'fundo', 'recurso'
            ]
        }
        
        # Verifica palavras de alta prioridade
        if any(keyword in text for keyword in keywords['high_priority']):
            return True
        
        # Conta palavras de média prioridade
        medium_count = sum(1 for keyword in keywords['medium_priority'] if keyword in text)
        if medium_count >= 2:
            return True
        
        # Se tem uma palavra de média prioridade e pelo menos uma de baixa
        if medium_count >= 1 and any(keyword in text for keyword in keywords['low_priority']):
            return True
        
        return False

    def parse_rss_feed(self, source: Source) -> List[Dict[str, Any]]:
        """Parse um feed RSS com melhor tratamento de erros"""
        try:
            self.logger.info(f"Iniciando parse do feed: {source.url}")
            
            # Verifica se a URL é válida
            if not source.url:
                self.logger.error("URL da fonte é vazia")
                return []
            
            # Faz a requisição com retry automático
            try:
                response = self.session.get(source.url, timeout=15)
                response.raise_for_status()
                feed_content = response.text
            except Exception as e:
                self.logger.error(f"Erro ao fazer requisição para {source.url}: {str(e)}")
                return []
            
            if not feed_content:
                self.logger.error(f"Conteúdo vazio do feed: {source.url}")
                return []
            
            # Parse do feed com verificação de erros
            try:
                feed = feedparser.parse(feed_content)
            except Exception as e:
                self.logger.error(f"Erro ao fazer parse do feed {source.url}: {str(e)}")
                return []
            
            if not feed:
                self.logger.error(f"Feed vazio após parse: {source.url}")
                return []
            
            if not hasattr(feed, 'entries'):
                self.logger.error(f"Feed não contém entradas: {source.url}")
                return []
            
            if not feed.entries:
                self.logger.info(f"Feed não tem novas entradas: {source.url}")
                return []

            # Processa entradas em chunks para melhor performance
            chunk_size = 5
            all_editais = []
            entries = [e for e in feed.entries if e is not None]
            
            for i in range(0, len(entries), chunk_size):
                chunk = entries[i:i + chunk_size]
                with ThreadPoolExecutor(max_workers=chunk_size) as executor:
                    futures = [
                        executor.submit(self.process_feed_entry_with_context, entry, source)
                        for entry in chunk
                    ]
                    
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                            if result:
                                all_editais.append(result)
                        except Exception as e:
                            self.logger.error(f"Erro ao processar entrada do feed: {str(e)}")
            
            self.logger.info(f"Concluído parse do feed {source.url}. Encontrados {len(all_editais)} editais.")
            return all_editais
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer parse do feed {source.url}: {str(e)}")
            return []

    def parse_rss_feeds(self) -> int:
        """Parse todos os feeds RSS ativos e retorna o número de novos editais"""
        try:
            with self.app.app_context():
                # Obtém todas as fontes RSS ativas
                sources = Source.query.filter_by(type='rss', active=True).all()
                
                if not sources:
                    self.logger.warning("No active RSS sources found")
                    return 0
                
                self.logger.info(f"Found {len(sources)} active RSS sources")
                total_new = 0
                
                # Processa cada fonte
                for source in sources:
                    try:
                        editais = self.parse_rss_feed(source)
                        
                        # Filtra editais já existentes
                        new_editais = []
                        for edital in editais:
                            exists = Edital.query.filter_by(
                                link=edital['link']
                            ).first() is not None
                            
                            if not exists:
                                new_editais.append(edital)
                        
                        # Adiciona novos editais ao banco
                        for edital in new_editais:
                            try:
                                new_edital = Edital(**edital)
                                db.session.add(new_edital)
                            except Exception as e:
                                self.logger.error(f"Error adding edital: {str(e)}")
                                continue
                        
                        # Atualiza timestamp do último scrape
                        source.last_scrape = datetime.now()
                        
                        # Commit das mudanças
                        try:
                            db.session.commit()
                            total_new += len(new_editais)
                            self.logger.info(f"Added {len(new_editais)} new editais from {source.name}")
                        except Exception as e:
                            self.logger.error(f"Error committing changes: {str(e)}")
                            db.session.rollback()
                    
                    except Exception as e:
                        self.logger.error(f"Error processing source {source.name}: {str(e)}")
                        db.session.rollback()
                        continue
                
                return total_new
                
        except Exception as e:
            self.logger.error(f"Error in parse_rss_feeds: {str(e)}")
            return 0

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
