from config.settings import WEBHOOK_URL
import requests

class WebhookService:
    def __init__(self, api_url: str = WEBHOOK_URL):
        self.api_url = api_url

    def make_message(self, message):
        #Devolver un json estructurado con el mensaje
        return f"Estimado equipo, se ha presentado un error en el sistema: {message}"
    def send_to_webhook(self, data):
        headers = {
            'Content-Type': 'application/json'
        }

        payload = {
            'text': self.make_message(data)
        }
        response = requests.post(self.api_url,  json=payload, headers=headers)
        if response.status_code != 200:
            raise ConnectionError(f"Error en la solicitud: {response.status_code} - {response.text}")
    

