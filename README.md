# Weibo Hot Search MCP Server
This is a Weibo hot search data acquisition server based on the Model Context Protocol (MCP) framework, providing functions to fetch Weibo hot search list, hot search details, and comments.

## Features

1. Get Weibo Hot Search List
   - Display hot search rankings
   - Show hot search keywords
   - Show hot search index

2. Get Hot Search Details
   - Topic category
   - Topic description
   - Topic link
   - Topic claim information
   - Statistics (reads, discussions, interactions, original posts)

3. Get Hot Search Comments
   - Support getting comments from the first Weibo post or claim's post through hot search link
   - Configurable maximum comment fetch count
   - Display comment content and like count

## Requirements

- Python >=3.10
- Dependencies:
  - requests
  - lxml
  - mcp>=1.0.0

## Installation
### Installation from sources
1. Clone the repository
```bash
git clone https://github.com/Yooki-K/weibo-mcp-server.git
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
>Note: If using `uv run weibo_mcp_server`, dependencies will be installed automatically, no need for `pip install`
### Installation from Pypi
```bash
pip install weibo-mcp-server
```

## Configuration
### Get Weibo Cookie
Create a [Weibo](https://www.weibo.com/) account, press F12 to open developer tools, and get the cookie as shown below:
![Get Cookie](./img/cookie.png)

### Run Project Locally
Add this tool to the MCP server

#### Cursor
On Windows: `C:/Users/YOUR_USER/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "weibo": {
      "command": "uv",
      "args": [
         "--directory",
         "path/to/weibo-mcp-server",
         "run",
         "weibo_mcp_server"
      ],
      "env":{
        "weibo_COOKIE": YOUR_WEIBO_COOKIE
      }
    }
  }
}
```

#### Claude
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`
```json
"weibo": {
    "command": "uv",
    "args": [
      "--directory",
      "/path/to/weibo-mcp-server",
      "run",
      "weibo_mcp_server"
    ],
    "env": {
      "weibo_COOKIE": YOUR_WEIBO_COOKIE
    }
  }
```

## License
MIT License - see LICENSE file for details.
## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 
