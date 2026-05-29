import logging, threading, time
import schedule
from config import PRODUCTS, SCRAPE_INTERVAL_MINUTES
from scraper import scrape_todos
from database import insert_precos_batch
from alerts import verificar_alertas

def _job():
    resultados = scrape_todos(PRODUCTS)
    if resultados: 
        insert_precos_batch(resultados)
    verificar_alertas()

def start_scheduler_thread(intervalo=SCRAPE_INTERVAL_MINUTES):
    _job()  # Coleta imediata ao iniciar
    schedule.every(intervalo).minutes.do(_job)
    
    def loop():
        while True: 
            schedule.run_pending()
            time.sleep(1)
            
    t = threading.Thread(target=loop, daemon=True, name='scheduler')
    t.start()
    return t