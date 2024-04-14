from celery import shared_task
import requests


@shared_task
def post_text_to_service(url, data):
    response = requests.post(url, json=data)
    return response.status_code, response.text
