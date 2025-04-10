import json
import os
import wrike_api
from datetime import datetime


async def search_contacts_by_name(names: list[str]):
    today = datetime.now().strftime('%Y-%m-%d')
    
    script_dir = os.path.dirname(__file__)
    cache_file = os.path.join(script_dir, f'cache/contacts_{today}.json')
    contacts = []
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            contacts = json.load(f)
    else:
        contacts = await wrike_api.get_all_contacts()
        with open(cache_file, 'w') as f:
            json.dump(contacts, f)

    matches = []
    for contact in contacts:
        full_name = contact['firstName'] + ' ' + contact['lastName']
        full_name = full_name.lower()
        for name in names:
            name = name.lower()
            if name in full_name:
                matches.append({
                'id': contact['id'],
                'fullName': contact['firstName'] + ' ' + contact['lastName']
                })
                break
    return matches
