import os

import requests


CONNECTOR_URL = os.environ.get('BOT_CONNECTOR_URL')
WEBHOOK = '/webhooks/training_model'

class IntentManipulation:
    def get_all_intents(self, page):
        res = requests.get(f'{CONNECTOR_URL}{WEBHOOK}/intent?page={page}', headers={
            'Accept': 'application/json'
        })
    
        return res.json()
    
    def get_intent_by_name(self, intent):
        res = requests.get(f'{CONNECTOR_URL}{WEBHOOK}/intent/{intent}', headers={
            'Accept': 'application/json',
        })

        return res.json()
    
    def create_intent(self, intent):
        res = requests.post(f'{CONNECTOR_URL}{WEBHOOK}/intent', headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }, json=intent)

        return res
    
    def edit_intent_examples(self, intent, examples):
        res = requests.patch(f'{CONNECTOR_URL}{WEBHOOK}/intent/{intent}/change/examples', headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }, json=examples)

        return res


class ResponseManipulation:
    def get_all_responses(self, page):
        res = requests.get(f'{CONNECTOR_URL}{WEBHOOK}/response?page={page}', headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

        return res
