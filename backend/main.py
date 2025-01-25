import urllib3
urllib3.disable_warnings()

from app import create_app
from app.scraper import EditalScraper
from apscheduler.schedulers.background import BackgroundScheduler

app = create_app()
scraper = EditalScraper(app)

def scheduled_job():
    """Function to run scheduled scraping"""
    try:
        num_new = scraper.parse_rss_feeds()
        app.logger.info(f"Scheduled scraping completed. Added {num_new} new editais.")
    except Exception as e:
        app.logger.error(f"Error in scheduled scraping: {str(e)}")

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
