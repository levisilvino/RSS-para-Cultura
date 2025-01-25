from flask import Blueprint, jsonify, request
from .models import Edital, Source, db
from datetime import datetime
from sqlalchemy import or_
from urllib.parse import urlparse
import requests
import feedparser
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

main_bp = Blueprint('main', __name__)

def validate_url(url: str, source_type: str) -> tuple[bool, str]:
    """Validate URL and check if it's accessible and matches the source type"""
    try:
        # Basic URL validation
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return False, "URL inválida"
            
        # Try to access the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # For RSS sources, try to parse the feed directly
        if source_type == 'rss':
            # First try to get the content
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            
            # Try to parse as RSS/Atom feed
            feed = feedparser.parse(response.text)
            
            # Check if it has entries or items (common RSS/Atom elements)
            if hasattr(feed, 'entries') and len(feed.entries) > 0:
                return True, ""
                
            # If no entries found, check for basic RSS/Atom structure
            if hasattr(feed, 'feed') and any([
                hasattr(feed.feed, 'title'),
                hasattr(feed.feed, 'description'),
                hasattr(feed.feed, 'link')
            ]):
                return True, ""
                
            return False, "URL não parece ser um feed RSS/Atom válido"
            
        # For web sources, just check if the URL is accessible
        response = requests.head(url, headers=headers, timeout=5, verify=False)
        response.raise_for_status()
        return True, ""
        
    except requests.exceptions.RequestException as e:
        return False, f"Erro ao acessar URL: {str(e)}"
    except Exception as e:
        return False, f"Erro ao validar URL: {str(e)}"

def get_url_preview(url: str, source_type: str) -> tuple[bool, str, Optional[Dict[str, Any]]]:
    """Get preview information for a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        if source_type == 'rss':
            # First try to get the content
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            
            # Try to parse as RSS/Atom feed
            feed = feedparser.parse(response.text)
            
            # Check if it has entries
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                return False, "Feed RSS não contém entradas", None
            
            # Get feed title or use URL as fallback
            title = ''
            description = ''
            
            if hasattr(feed, 'feed'):
                title = getattr(feed.feed, 'title', '')
                description = getattr(feed.feed, 'description', '')
            
            if not title:
                title = url
            
            # Get recent items for preview
            items = []
            for entry in feed.entries[:5]:  # Show up to 5 recent items
                item_title = getattr(entry, 'title', '')
                item_desc = getattr(entry, 'description', '')
                if not item_desc:
                    item_desc = getattr(entry, 'summary', '')
                
                items.append({
                    'title': item_title,
                    'description': item_desc[:200] + '...' if len(item_desc) > 200 else item_desc,
                    'published': getattr(entry, 'published', ''),
                    'link': getattr(entry, 'link', '')
                })
            
            return True, "", {
                'title': title,
                'description': description,
                'type': 'rss',
                'items': items
            }
        
        else:  # Web page
            response = requests.get(url, headers=headers, timeout=5, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get page title
            title = soup.title.string if soup.title else url
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'] if meta_desc else ''
            
            # Get preview text from first paragraph or div
            preview_text = ''
            for tag in ['p', 'div']:
                element = soup.find(tag)
                if element:
                    preview_text = element.get_text().strip()
                    if preview_text:
                        break
            
            if len(preview_text) > 200:
                preview_text = preview_text[:200] + '...'
            
            return True, "", {
                'title': title,
                'description': description,
                'type': 'web',
                'preview_text': preview_text
            }
            
    except Exception as e:
        return False, f"Erro ao obter preview: {str(e)}", None

@main_bp.route('/api/editais', methods=['GET'])
def get_editais():
    try:
        # Get query parameters
        categoria = request.args.get('categoria')
        search = request.args.get('search')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        print(f"[DEBUG] Recebendo requisição GET /api/editais com parâmetros: categoria={categoria}, search={search}, data_inicio={data_inicio}, data_fim={data_fim}")
        
        # Start with base query
        query = Edital.query
        
        # Apply filters
        if categoria:
            query = query.filter(Edital.categoria == categoria)
        
        if search:
            search_filter = or_(
                Edital.nome.ilike(f'%{search}%'),
                Edital.descricao.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        if data_inicio:
            try:
                data_inicio = datetime.fromisoformat(data_inicio)
                query = query.filter(Edital.data_vencimento >= data_inicio)
            except ValueError as e:
                print(f"[ERROR] Erro ao converter data_inicio: {str(e)}")
                pass
        
        if data_fim:
            try:
                data_fim = datetime.fromisoformat(data_fim)
                query = query.filter(Edital.data_vencimento <= data_fim)
            except ValueError as e:
                print(f"[ERROR] Erro ao converter data_fim: {str(e)}")
                pass
        
        # Order by publication date
        editais = query.order_by(Edital.data_publicacao.desc()).all()
        print(f"[DEBUG] Encontrados {len(editais)} editais")
        
        return jsonify([edital.to_dict() for edital in editais])
    except Exception as e:
        print(f"[ERROR] Erro ao buscar editais: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/categorias', methods=['GET'])
def get_categorias():
    try:
        print("[DEBUG] Recebendo requisição GET /api/categorias")
        categorias = db.session.query(Edital.categoria)\
            .filter(Edital.categoria.isnot(None))\
            .distinct()\
            .order_by(Edital.categoria)\
            .all()
        
        result = [cat[0] for cat in categorias if cat[0]]
        print(f"[DEBUG] Encontradas {len(result)} categorias")
        
        if not result:
            print("[DEBUG] Nenhuma categoria encontrada, retornando lista padrão")
            return jsonify([
                'Edital',
                'Prêmio',
                'Concurso',
                'Música',
                'Teatro',
                'Dança',
                'Cinema',
                'Literatura',
                'Artes Visuais',
                'Patrimônio',
                'Fomento',
                'Formação',
                'Outros'
            ])
            
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] Erro ao buscar categorias: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Source management endpoints
@main_bp.route('/api/sources', methods=['GET'])
def get_sources():
    """Get all sources"""
    try:
        print("[DEBUG] Recebendo requisição GET /api/sources")
        sources = Source.query.order_by(Source.created_at.desc()).all()
        print(f"[DEBUG] Encontradas {len(sources)} fontes")
        return jsonify([source.to_dict() for source in sources])
    except Exception as e:
        print(f"[ERROR] Erro ao buscar fontes: {str(e)}")
        return jsonify({'error': f'Erro ao buscar fontes: {str(e)}'}), 500

@main_bp.route('/api/sources/preview', methods=['POST'])
def preview_source():
    """Get a preview of a source URL"""
    try:
        print("[DEBUG] Recebendo requisição POST /api/sources/preview")
        data = request.get_json()
        if not all(k in data for k in ['url', 'type']):
            return jsonify({'error': 'URL e tipo são obrigatórios'}), 400
            
        url = data['url'].strip()
        if not url:
            return jsonify({'error': 'URL não pode estar vazia'}), 400
            
        # Basic URL validation
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return jsonify({'error': 'URL inválida'}), 400
            
        # Get preview
        success, error_msg, preview_data = get_url_preview(url, data['type'])
        if not success:
            return jsonify({'error': error_msg}), 400
            
        print(f"[DEBUG] Preview gerado com sucesso: {preview_data}")
        return jsonify(preview_data)
        
    except Exception as e:
        print(f"[ERROR] Erro ao gerar preview: {str(e)}")
        return jsonify({'error': f'Erro ao gerar preview: {str(e)}'}), 500

@main_bp.route('/api/sources', methods=['POST'])
def create_source():
    """Create a new source"""
    try:
        print("[DEBUG] Recebendo requisição POST /api/sources")
        data = request.get_json()
        if not all(k in data for k in ['name', 'url', 'type']):
            return jsonify({'error': 'Campos obrigatórios: nome, url e tipo'}), 400
            
        # Clean and validate URL
        url = data['url'].strip()
        if not url:
            return jsonify({'error': 'URL não pode estar vazia'}), 400
            
        # Check if URL already exists
        existing = Source.query.filter_by(url=url).first()
        if existing:
            return jsonify({'error': 'URL já cadastrada'}), 400
            
        # Validate URL and check if it's accessible
        is_valid, error_msg = validate_url(url, data['type'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        source = Source(
            name=data['name'].strip(),
            url=url,
            type=data['type']
        )
        db.session.add(source)
        db.session.commit()
        print(f"[DEBUG] Fonte criada com sucesso: {source.to_dict()}")
        return jsonify(source.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Erro ao criar fonte: {str(e)}")
        return jsonify({'error': f'Erro ao criar fonte: {str(e)}'}), 500

@main_bp.route('/api/sources/<int:source_id>', methods=['PUT'])
def update_source(source_id):
    """Update an existing source"""
    try:
        print(f"[DEBUG] Recebendo requisição PUT /api/sources/{source_id}")
        source = Source.query.get_or_404(source_id)
        data = request.get_json()
        
        if 'url' in data:
            url = data['url'].strip()
            if not url:
                return jsonify({'error': 'URL não pode estar vazia'}), 400
                
            # Check URL uniqueness if it's being changed
            if url != source.url:
                existing = Source.query.filter_by(url=url).first()
                if existing:
                    return jsonify({'error': 'URL já cadastrada'}), 400
                    
                # Validate new URL
                is_valid, error_msg = validate_url(url, data.get('type', source.type))
                if not is_valid:
                    return jsonify({'error': error_msg}), 400
                    
                source.url = url
        
        if 'name' in data:
            source.name = data['name'].strip()
        if 'type' in data:
            source.type = data['type']
        if 'active' in data:
            source.active = data['active']
            
        db.session.commit()
        print(f"[DEBUG] Fonte atualizada com sucesso: {source.to_dict()}")
        return jsonify(source.to_dict())
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Erro ao atualizar fonte: {str(e)}")
        return jsonify({'error': f'Erro ao atualizar fonte: {str(e)}'}), 500

@main_bp.route('/api/sources/<int:source_id>', methods=['DELETE'])
def delete_source(source_id):
    """Delete a source"""
    try:
        print(f"[DEBUG] Recebendo requisição DELETE /api/sources/{source_id}")
        source = Source.query.get_or_404(source_id)
        db.session.delete(source)
        db.session.commit()
        print(f"[DEBUG] Fonte excluída com sucesso: {source_id}")
        return '', 204
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Erro ao excluir fonte: {str(e)}")
        return jsonify({'error': f'Erro ao excluir fonte: {str(e)}'}), 500
