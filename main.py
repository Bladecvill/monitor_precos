import logging, subprocess, sys
from database import init_db
from scheduler import start_scheduler_thread
from config import SCRAPE_INTERVAL_MINUTES

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

def main():
    init_db()
    start_scheduler_thread(SCRAPE_INTERVAL_MINUTES)
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py',
                    '--server.headless=true'])

if __name__ == '__main__':
    main()