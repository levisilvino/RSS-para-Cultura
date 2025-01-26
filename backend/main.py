import urllib3
urllib3.disable_warnings()

from app import create_app, db
from app.scraper import EditalScraper
from apscheduler.schedulers.background import BackgroundScheduler
from flask import jsonify
from flask_cors import CORS
from flask_migrate import Migrate

app = create_app()
CORS(app, resources={r"/api/*": {"origins": "*"}})
migrate = Migrate(app, db)

def create_scraper():
    """Cria uma instância do scraper com o contexto da aplicação"""
    return EditalScraper(app)

scraper = create_scraper()

def scheduled_job():
    """Function to run scheduled scraping"""
    with app.app_context():
        try:
            num_new = scraper.parse_rss_feeds()
            app.logger.info(f"Scheduled scraping completed. Added {num_new} new editais.")
            return num_new
        except Exception as e:
            app.logger.error(f"Error in scheduled scraping: {str(e)}")
            return 0

@app.route('/api/update-feeds', methods=['POST'])
def update_feeds():
    """Endpoint to manually trigger RSS feed updates"""
    try:
        num_new = scheduled_job()
        return jsonify({
            'success': True,
            'message': f'Feed update completed. Added {num_new} new editais.'
        }), 200
    except Exception as e:
        app.logger.error(f"Error updating feeds: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error updating feeds: {str(e)}'
        }), 500

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Endpoint to clear all cached editais"""
    try:
        with app.app_context():
            # Delete all records from the editais table
            num_deleted = Edital.query.delete()
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Cache limpo com sucesso. {num_deleted} editais foram removidos.'
            }), 200
    except Exception as e:
        app.logger.error(f"Error clearing cache: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao limpar cache: {str(e)}'
        }), 500

# Set up scheduler for periodic RSS feed checks
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, 'interval', hours=6)
scheduler.start()

if __name__ == '__main__':
    # Initial feed parse
    with app.app_context():
        try:
            scraper.parse_rss_feeds()
        except Exception as e:
            app.logger.error(f"Error in initial feed parse: {str(e)}")
    
    # Start the Flask application
    app.run(debug=True, port=5000)
