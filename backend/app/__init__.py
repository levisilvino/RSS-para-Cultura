from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure SQLite database
    base_dir = Path(__file__).resolve().parent.parent
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{base_dir}/cultura_alerta.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()
        
        # Configurar o scheduler para executar o scraper periodicamente
        from .scraper import EditalScraper
        scheduler = BackgroundScheduler()
        
        def run_scraper():
            with app.app_context():
                scraper = EditalScraper(app)
                scraper.parse_rss_feeds()
        
        # Executar o scraper a cada 15 minutos
        scheduler.add_job(run_scraper, 'interval', minutes=15)
        scheduler.start()
        
        # Executar o scraper imediatamente na inicialização
        run_scraper()
    
    return app
