
from mcp.server.fastmcp import FastMCP
import utils
import wrike_api


# Create an MCP server
mcp = FastMCP("Wrike MCP Server")


@mcp.tool()
async def fetch_wrike_task_by_task_permalink(permalink: str) -> str:
    """Fetch wrike task by permalink url """
    task = await wrike_api.fetch_wrike_task_by_permalink(permalink)

    return await wrike_api.format_task_as_markdown(task)

@mcp.tool()
async def fetch_wrike_tasks_assigned_to_me() -> str:
    """Fetch wrike tasks assigned to me """
    tasks = await wrike_api.get_tasks_assigned_to_me()

    return await wrike_api.format_tasks_as_markdown(tasks)

@mcp.tool()
async def fetch_wrike_tasks_from_folder(permalink: str) -> str:
    """Fetch wrike tasks from the folder with the given permalink url"""
    tasks = await wrike_api.get_tasks_from_folder(permalink)

    return await wrike_api.format_tasks_as_markdown(tasks)

@mcp.tool()
async def write_html_comment_to_wrike_task(permalink: str, comment : str) -> str:
    """Write html comment to Wrike task specifed by given permalink url. Comment should be in html format with 
    only following tags <br>,<a>. I you need to mention a user please get his and his name and use the following 
    format <a class="stream-user-id avatar" rel="<user id>">@<full user name></a>"""

    task = await wrike_api.fetch_wrike_task_by_permalink(permalink)
    comment = await wrike_api.add_comment_to_task(task['id'], comment)

    return comment

@mcp.tool()
async def create_wrike_task(title: str, description: str, permalink: str) -> str:
    """Create a new Wrike task in the folder specified by the given permalink url. Description should be in html format
      with only following tags <br>,<h1>, <h2>,<h3>,<h4>,<h5>,<h6>,<strong>,<b>,<em>,<i>,<u>,<s>,<a>,<ol>,<ul>,<li>,
      <table>,<tr>,<td>"""

    folder = await wrike_api.fetch_wrike_folder_by_permalink(permalink)
    folder_id = folder['id']
    permalink = await wrike_api.create_task(title, description, folder_id)

    return permalink


@mcp.tool()
async def get_users_ids(names: list[str]) -> str:
    """When given a list of Wrike users names or parts of names, return the ids of the users with the given full names"""

    users = await utils.search_contacts_by_name(names)
    users_list =  '\n'.join([user['id'] + ' ' + user['fullName'] for user in users])

    return users_list

if __name__ == "__main__":
    mcp.run(transport="stdio")