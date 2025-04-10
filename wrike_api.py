import httpx
import os
from bs4 import BeautifulSoup
import datetime


WRIKE_API_BASE_URL = 'https://www.wrike.com/api/v4'


# Get API token from environment variables
WRIKE_API_TOKEN = os.getenv('WRIKE_API_TOKEN')
if not WRIKE_API_TOKEN:
    raise ValueError("WRIKE_API_TOKEN not found in environment variables. Please check your .env file.")


def get_common_headers():
    return {
        'Authorization': f'bearer {WRIKE_API_TOKEN}',
        'Content-Type': 'application/json'
    }


async def fetch_wrike_task_by_permalink(permalink: str):

    params = {
        'permalink': permalink,
        'fields': '["customFields","parentIds","authorIds","responsibleIds","description"]'
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            WRIKE_API_BASE_URL + '/tasks',
            headers=get_common_headers(),
            params=params
        )
        response.raise_for_status()
        tasks_json = response.json()
        return tasks_json['data'][0]

async def fetch_wrike_folder_by_permalink(permalink: str):

    params = {
        'permalink': permalink,
        'fields': '["customFields","description"]'
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            WRIKE_API_BASE_URL + '/folders',
            headers=get_common_headers(),
            params=params
        )
        response.raise_for_status()
        folder_json = response.json()
        return folder_json['data'][0]

async def fetch_wrike_folders_by_ids(folder_ids: list):
    if not folder_ids:
        return []
    
    params = {
        # 'fields': '["customFields","description"]'
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                WRIKE_API_BASE_URL + '/folders/'+','.join(folder_ids),
                headers=get_common_headers(),
                params=params
            )
            response.raise_for_status()
            folder_json = response.json()
            return folder_json['data']
    except Exception as e:
        print(f"Error fetching folders {folder_ids}: {str(e)}")
        # Return a list of empty folder objects for each requested ID
        return [{"id": folder_id, "title": ""} for folder_id in folder_ids]

async def fetch_comments_by_task_id(task_id: str):
    params = {
        'plainText': 'true',
        'fields': '["type"]'
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            WRIKE_API_BASE_URL + '/tasks/'+task_id+'/comments',
            headers=get_common_headers(),
            params=params
        )
        response.raise_for_status()
        comments_json = response.json()
        comments = comments_json['data']
        comments.reverse()
        return comments
    

def clean_html(text: str) -> str:
    """Clean HTML tags and entities from text using BeautifulSoup."""
    if not text:
        return "No description available"
    
    soup = BeautifulSoup(text, 'html.parser')
    return ' '.join(soup.stripped_strings)


async def format_task_as_markdown(task: dict) -> str:
    """Format task data as markdown text."""
    title = task.get('title', 'No Title')
    description = clean_html(task.get('description'))
    responsible_contacts = await get_contacts(task.get('responsibleIds'))
    responsible_contacts_names = [contact['firstName'] + ' ' + contact['lastName'] for contact in responsible_contacts]

    author_contacts = await get_contacts(task.get('authorIds'))
    author_contacts_names = [contact['firstName'] + ' ' + contact['lastName'] for contact in author_contacts]

    folder_ids = task.get('parentIds')
    folders = await fetch_wrike_folders_by_ids(folder_ids)
    folder_names = [folder['title'] for folder in folders]

    comments = await fetch_comments_by_task_id(task.get('id'))
    comments_text = ''
    for comment in comments:
        date_time =comment.get('createdDate')
        text = comment.get('text')
        author_contact = await get_contacts([ comment.get('authorId')])
        author_name = author_contact[0]['firstName'] + ' ' + author_contact[0]['lastName']
        comment_text = f'### Commented by {author_name} at {date_time}: {text}\n'
        comments_text += comment_text


    markdown = f"""# {title}

## Description
{description}

## Additional Information
- **Folders**: {', '.join(folder_names)}
- **ID**: {task.get('id', 'N/A')}
- **Authors**: {', '.join(author_contacts_names)}
- **Assignee**: {', '.join(responsible_contacts_names)}
- **Permalink url**: {task.get('permalink', 'N/A')}
- **Status**: {task.get('status', 'N/A')}
- **Created**: {task.get('createdDate', 'N/A')}
- **Updated**: {task.get('updatedDate', 'N/A')}

"""
    if comments_text:
        markdown += '## Comments\n'
        markdown += comments_text

    return markdown

async def format_tasks_as_markdown(tasks: list) -> str:
    markdown = ""
    for task in tasks:
        markdown += '----------------------------------------\n'
        markdown += await format_task_as_markdown(task)
    return markdown

async def get_all_contacts():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            WRIKE_API_BASE_URL + '/contacts',
            headers=get_common_headers()
        )
        return response.json()['data']

async def get_contacts(ids: list):
    if not ids:
        return []
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            WRIKE_API_BASE_URL + '/contacts/'+','.join(ids),
            headers= get_common_headers(),
        )
        return response.json()['data']
    
async def who_am_i():
     async with httpx.AsyncClient() as client:
        response = await client.get(
            WRIKE_API_BASE_URL + '/contacts?me',
            headers= get_common_headers()
        )
        return response.json()['data'][0]
     

    
async def get_tasks_assigned_to_me():
    contact = await who_am_i()
    my_id = contact['id']

    updated_dates = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime('%Y-%m-%dT%H:%M:%SZ') + ',' + datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')  
    
    
    params = {
        'responsibles': f'[{my_id}]',
        'fields': '["customFields","parentIds","authorIds","responsibleIds","description"]',
        'sortField': 'UpdatedDate',
        'sortOrder': 'Desc',
        'status': 'Active',
        'updatedDate':  updated_dates
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            WRIKE_API_BASE_URL + '/tasks',
            headers=get_common_headers(),
            params=params
        )

        return response.json()['data']
    
    
async def get_tasks_from_folder(permalink: str):

    folder = await fetch_wrike_folder_by_permalink(permalink)
    folder_id = folder['id']

    params = {
        'descendants': 'true',
        'fields': '["customFields","parentIds","authorIds","responsibleIds","description"]',
        'sortField': 'UpdatedDate',
        'sortOrder': 'Desc',
        # 'status': 'Active',
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            WRIKE_API_BASE_URL + '/folders/'+folder_id+'/tasks',
            headers=get_common_headers(),
            params=params
        )

        return response.json()['data']
    
async def add_comment_to_task(task_id: str, html_text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            WRIKE_API_BASE_URL + '/tasks/'+task_id+'/comments',
            headers=get_common_headers(),
            json={'text': html_text}
        )
        return response.json()['data'][0]['text']
    

async def create_task(title: str, description: str, folder_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            WRIKE_API_BASE_URL + '/folders/'+folder_id+'/tasks',
            headers=get_common_headers(),
            json={'title': title, 'description': description}
        )
        return response.json()['data'][0]['permalink'] 