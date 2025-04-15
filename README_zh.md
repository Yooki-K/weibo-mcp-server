# 微博热搜 MCP Server
这是一个基于模型上下文协议 (Model Context Protocol, MCP) 框架的微博热搜数据获取服务器，提供了获取微博热搜榜、热搜详情和评论等功能。

## 功能特性

1. 获取微博热搜榜单
   - 展示热搜排名
   - 显示热搜词
   - 显示热搜指数

2. 获取热搜详细信息
   - 话题分类
   - 话题描述
   - 话题链接
   - 话题主持人信息
   - 统计数据（阅读量、讨论量、互动量、原创量）

3. 获取热搜评论
   - 支持通过热搜链接获取第一条微博或主持人发布的微博的评论
   - 可配置最大评论获取数量
   - 显示评论内容和点赞数

## 安装要求

- Python >=3.10
- 依赖包：
  - requests
  - lxml
  - mcp>=1.0.0

## 安装步骤
### 源码安装
1. 克隆仓库到本地
```bash
get clone https://github.com/Yooki-K/weibo-mcp-server.git
```
2. 安装依赖：
```bash
pip install -r requirements.txt
```
>注意：如果使用`uv run weibo_mcp_server`则会自动安装依赖，无需`pip install`
### pip安装
```bash
pip install weibo-mcp-server
```
## 配置
### 获得微博Cookie
创建一个[微博](https://www.weibo.com/)账户，按下F12打开开发人员工具，获得cookie，如下图：
![获得Cookie](./img/cookie.png)
### 本地运行项目
把这个工具加入到MCP服务器
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
## 许可证
MIT License.
## 贡献
1.复刻（Fork）本仓库
2.创建你的特性分支（`git checkout -b feature/amazing-feature`）
3.提交你的更改（`git commit -m '添加一些很棒的特性'`）
4.推送到分支（`git push origin feature/amazing-feature`）
5.发起拉取请求（`Pull Request`）