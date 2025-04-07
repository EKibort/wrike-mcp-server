from mcp.server.fastmcp import FastMCP
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

if __name__ == "__main__":
    mcp.run(transport="stdio")