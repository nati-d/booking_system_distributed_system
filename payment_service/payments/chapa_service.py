import requests
import os

class ChapaService:
    CHAPA_URL = "https://api.chapa.co/v1/transaction/initialize"
    SECRET_KEY = os.getenv('CHAPA_SECRET_KEY')

    @staticmethod
    def initialize_payment(payload):
        headers = {
            'Authorization': f'Bearer {ChapaService.SECRET_KEY}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(ChapaService.CHAPA_URL, json=payload, headers=headers)
            return response.json()  # Return JSON response
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
