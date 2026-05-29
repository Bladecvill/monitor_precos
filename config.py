import os
from dotenv import load_dotaenv

load_dotaenv()

DB_NAME = os.getenv("DB_NAME", "precos.db")
SCRAPE_INTERVAL_MINUTES = int(os.getenv("SCRAPE_INTERVAL_MINUTES"), "60")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "5512997803661")
WHATSAPP_ENABLE = os.getenv("WHATSAPP_ENABLE", "false").lower == "true"
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0")
REQUEST_TIMEOUT = 15
REQUEST_RETRY = 3
DEFAUT_HEADERS = {"User-Agent": USER_AGENT, "Acept-Language": "pt-BR"}

PRODUCTS = [
    {
        "nome": "ASRock X670E PG Lightning Support AMD AM5 RYZEN 7000 Series Processadores Placa-mãe",
        "url": "https://www.amazon.com.br/ASRock-Phantom-Gaming-X670E-Motherboard/dp/B0BGPH2LQJ/ref=sr_1_2?crid=3VC21KPLPWTAI&dib=eyJ2IjoiMSJ9.Y2yfIFqmjlxZIjj757Ex0QGeMcGAXb6jiFwCP-if1go-org8XoTOcpen2NLXAgGxAIe4KTBzecsBIHunthtpCTb-wP3SRgeHmYnaiwj8g-vdApLjsft8H6fmOBMKdAeU_IyyzU1NlfLSxuhiqKvJqQAJbBf49GYSgsiCgfG2PWYiKGmMzPhKywPWpXsMNCLKL-w2Tp298BOdbDjm9IdKuPiOZEWa8iZkkIKrDLwZm5khS9mHtNg8xQRxz7HvBAwGCO0yPZGlOza9VVPW0ausTH6psrdgy4W2KQOBsHlmDt8.6hH4pjwxKK2ekokWi7kWJAOeD3d6X9n-nDh1jfBVBd0&dib_tag=se&keywords=x670e&qid=1779929415&sprefix=X670%2Caps%2C317&sr=8-2&ufe=app_do%3Aamzn1.fos.95de73c3-5dda-43a7-bd1f-63af03b14751&th=1",
        "site": "amazon",
        "seletor_preco": "span.a-price-whole",
        "seletor_nome": "#productTitle",
        "categoria": "Placa-mae",
    },
]

DEFAULT_ALERT_LIMITS = {
    "ASRock X670E PG Lightning Support AMD AM5 RYZEN 7000 Series Processadores Placa-mãe": 2100
}