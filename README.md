# wrike-mcp-server  
A lightweight implementation of the Wrike MCP server to help you integrate Wrike with your favorite LLM tools.

## Overview  
The Wrike MCP (Model Control Protocol) server acts as a bridge between Wrike's project management platform and Language Learning Models (LLMs). It enables AI-powered tools to interact with Wrike data through a set of well-defined API endpoints.

## Features  
- Fetch task details using permalink URLs  
- Retrieve tasks assigned to the authenticated user  
- Get tasks from specific folders  

## Requirements  
- Python 3.x  
- Wrike API token  
- Required Python packages (see `requirements.txt`)  

## Setup  
1. **Clone the repository**  

2. **Create and activate a virtual environment**:  
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # On macOS and Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your client application (example: Cursor IDE) to work with the MCP server**:  
   a. Go to **Settings → Cursor Settings → MCP** and click **Add new global MCP server**  
   
   b. Add the following configuration with the correct paths:  
   ```json
   {
     "mcpServers": {
       "wrike-mcp-server": {
         "command": "/Users/username/wrike-mcp-server/.venv/bin/python /Users/username/wrike-mcp-server/server.py",
         "env": {
           "WRIKE_API_TOKEN": "<YOUR WRIKE API TOKEN>"
         }
       }
     }
   }
   ```

   c. Enable the MCP server  

## Usage  
The server provides several MCP tools to interact with Wrike. Here are some example prompts:

1. **Fetch a specific task**:  
   ```
   Please analyze the following task and provide a short summary: https://www.wrike.com/open.htm?id=12345678
   ```

2. **Get tasks assigned to you**:  
   ```
   Please gather all my Wrike tasks and build a prioritized list with links to each task. Tasks involving my boss John Doe should be treated as more important. Also, include a link to each task under the title.
   ```

3. **Get tasks from a specific folder**:  
   ```
   Please summarize all Wrike tasks from the following folder: https://www.wrike.com/open.htm?id=12345678  
   Please exclude any information about prices and budgets in your output.
   ```

## License  
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
