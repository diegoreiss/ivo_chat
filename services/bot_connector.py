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
    
    def get_all_intents_names(self):
        res = requests.get(f'{CONNECTOR_URL}{WEBHOOK}/intent/names', headers={
            'Accept': 'application/json'
        })

        return res.json()
    
    def get_all_available_intents_names(self):
        res = requests.get(f'{CONNECTOR_URL}{WEBHOOK}/intent/names/available', headers={
            'Accept': 'application/json'
        })

        return res
    
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
    
    def get_all_responses_names(self):
        res = requests.get(f'{CONNECTOR_URL}{WEBHOOK}/response/names', headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

        return res
    
    def create_response(self, response):
        res = requests.post(f'{CONNECTOR_URL}{WEBHOOK}/response', headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }, json=response)

        return res
    
    def edit_response_examples(self, response_name, texts):
        res = requests.patch(f'{CONNECTOR_URL}{WEBHOOK}/response/{response_name}/change/texts', headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }, json=texts)

        return res


class StoriesManipulation:
    def get_all_stories(self):
        res = requests.get(f'{CONNECTOR_URL}{WEBHOOK}/stories', headers={
            'Accept': 'application/json',
        })

        return res
    
    def create_story(self, story):
        res = requests.post(f'{CONNECTOR_URL}{WEBHOOK}/stories', headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }, json=story)

        return res
    
    def change_story_steps(self, story, step):
        res = requests.patch(f'{CONNECTOR_URL}{WEBHOOK}/stories/{story}/change/steps', headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }, json=step)

        return res
