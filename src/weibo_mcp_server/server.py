import random
from typing import Optional
from lxml import etree
import asyncio
import requests
import re,os,json
from urllib.parse import parse_qs
import mcp
import logging
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("weibo_mcp_server")

# Initialize mcp server
app = mcp.server.Server("weiboHotSearch")

# Constants
HotSearchURL = "https://weibo.com/ajax/side/hotSearch"
HotSearchDetailURL = "https://m.s.weibo.com/ajax_topic/detail"
CommentURL = "https://weibo.com/ajax/statuses/buildComments"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"

@app.list_prompts()
async def handle_list_prompts() -> list[mcp.types.Prompt]:
    return []


@app.list_resources()
async def handle_list_resources() -> list[mcp.types.Resource]:
    return []

# options =
class ToolModel(BaseModel):
    @classmethod
    def as_tool(cls):
        return mcp.types.Tool(
            name="Weibo" + cls.__name__,
            description=cls.__doc__,
            inputSchema=cls.model_json_schema()
        )
class GetHotSearch(ToolModel):
    """Get hot search from weibo."""

class GetHotSearchDetail(ToolModel):
    """Get hot search detail by word from weibo. Sometimes the word is not found, that's normal."""
    word: str = Field(description="The word to search for.")

class GetHotSearchCommentByUrl(ToolModel):
    """Get hot search comment by url from weibo."""
    url: str = Field(description="The url to search for.")
    claim_id: str = Field(default=None,description="The id of the claim.")
    max_comments: int = Field(default=40,description="The maximum number of comments to fetch, advised not too large.")

@app.list_tools()
async def list_tools() -> list[mcp.types.Tool]:
    """List available tools."""
    logger.info("Listing available tools")
    tools = [
        GetHotSearch.as_tool(),
        GetHotSearchDetail.as_tool(),
        GetHotSearchCommentByUrl.as_tool()
    ]
    logger.info(f"Available tools: {[tool.name for tool in tools]}")
    return tools

@app.call_tool()
async def call_tool(name:str,arguments:dict|None) -> list[mcp.types.TextContent]:
    """Handle tool execution request."""
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    assert name[:5] == "Weibo", f"Unknown tool: {name}"
    try:
        match name[5:]:
            case "GetHotSearch":
                return get_hot_search()
            case "GetHotSearchDetail":
                word = arguments.get("word")
                return get_hot_search_detail(word)
            case "GetHotSearchCommentByUrl":
                url = arguments.get("url")
                claim_id = arguments.get("claim_id",None)
                max_comments = int(arguments.get("max_comments",40))
                config = get_weibo_config()
                cookie = config["cookie"]
                if cookie is None:
                    raise ValueError("Missing required coockie. Please check the weibo_COOKIE in environment variable.")
                return await get_hot_search_comment_by_url(cookie,url,claim_id,max_comments)
            case _:
                error_msg = f"Unknown tool: {name}"
                logger.error(error_msg)
                return [mcp.types.TextContent(
                    type="text",
                    text=error_msg
                )]
    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        logger.error(error_msg)
        return [mcp.types.TextContent(
            type='text',
            text = error_msg
        )]

def get_hot_search() -> list[mcp.types.TextContent]:
    """Get hot search from weibo."""
    headers = {
        "User-Agent": USER_AGENT,
        "accept": "application/json, text/plain, */*"
    }
    response = requests.get(HotSearchURL, headers=headers)
    data = response.json()['data']['realtime']
    res = []
    for item in data:
        try:
            res.append(mcp.types.TextContent(
                type='text',
                text = f"热搜排名: {item['realpos']}\n热搜词: {item['word']}\n热搜指数: {item['num']}"
            ))
        except Exception as e:
            continue
    return res

def get_hot_search_detail(word: str) -> list[mcp.types.TextContent]:
    """Get hot search detail by word from weibo. Sometimes the word is not found, that's normal.
    
    Args:
        word: The word to search for.
    """
    topic = f'#{word}#'
    headers = {
        "User-Agent": USER_AGENT,
        "accept": "application/json, text/plain, */*"
    }
    params = {
        "q": topic,
        "show_rank_info": 1
    }
    response = requests.get(HotSearchDetailURL, headers=headers, params=params)
    try:
        data = response.json()['data']
        statistics = {
            "阅读量": f"{data['baseData']['sum_all']['r']['val']}{data['baseData']['sum_all']['r']['unit']}",
            "讨论量": f"{data['baseData']['sum_all']['m']['val']}{data['baseData']['sum_all']['m']['unit']}",
            "互动量": f"{data['baseData']['sum_all']['interact']['val']}{data['baseData']['sum_all']['interact']['unit']}",
            "原创量": f"{data['baseData']['sum_all']['ori_m']['val']}{data['baseData']['sum_all']['ori_m']['unit']}"
        }
        detail = {
            "话题分类": data['baseInfo']['object']['category_str'],
            "话题描述": data['baseInfo']['object']['summary'],
            "话题链接": data['baseInfo']['object']['url'],
            "话题主持人": data['baseInfo']['claim_info']['name'],
            "话题主持人ID": data['baseInfo']['claim_info']['id'],
            "统计": json.dumps(statistics,indent=2)
        }
        return [mcp.types.TextContent(
            type='text',
            text = json.dumps(detail,indent=2)
        )]
    except KeyError as e:
        logger.info("There is no detail of this topic.")
        return [mcp.types.TextContent(
            type='text',
            text = json.dumps({
                "话题关键字": word,
                "话题链接": f"https://s.weibo.com/weibo?q={word}"                
            },indent=2)
        )]
    except Exception as e:
        raise ValueError(f"Unable to fetch hot search detail: {str(e)}")

def get_weibo_config() -> dict:
    """Get weibo configuration from environment variable."""
    return {
        "cookie": os.getenv("weibo_COOKIE"),
    }

async def get_hot_search_comment_by_url(cookie:str, url: str, claim_id:str|None, max_comments:int|str|None) -> list[mcp.types.TextContent]:
    """Get hot search comment by url from weibo, max_comments is optional, you can ask user if he/she want to set.
    
    Args:
        cookie: the cookie of user.
        url: The url to search for.
        claim_id: The id of the claim.
        max_comments: The maximum number of comments to fetch, advised not too large.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        'Cookie': cookie
    }
    response = requests.get(url, headers=headers)
    params = {
        "is_reload": 1,
        "id": "",
        "is_show_bulletin": 2,
        "is_mix": 0,
        "count": 10,
        "uid": "",
        "fetch_level": 0,
        "locale": "zh-CN"
    }
    html = etree.HTML(response.text)
    li_forward = html.xpath('//div[@id="pl_feedlist_index"]//div[@class="card-act"]/ul/li[1]/a/@action-data')
    urls = html.xpath('//div[@id="pl_feedlist_index"]//div[@class="from"]/a/@href')
    for i, item in enumerate(li_forward):
        if claim_id is None or f"uid={claim_id}" in item:
            parsed = parse_qs(item)
            params['uid'] = parsed.get('uid', [''])[0]
            params['id'] = parsed.get('mid', [''])[0]
            headers['Referer'] = 'https:' + urls[i]
            break
    if claim_id is not None and (params['uid'] == '' or params['id'] == ''):
        raise ValueError("claim_id is not found.")
    # headers['x-requested-with'] = "XMLHttpRequest"
    comments=[]
    def parse_comment(data:dict)->list[mcp.types.TextContent]:
        for x in data['data']:
            x['text'] = re.sub(r'<img [^>]*alt=\"([^\"]+)\"[^>]*>', r'\1', x['text'])
        return [mcp.types.TextContent(
                type='text',
                text=json.dumps({
                    "内容":x['text'],
                    "点赞数":x['like_counts']
                },indent=2)
            ) for x in data['data']]
    async def get_comment(max_id,comments)->int:
        if max_id is not None:  
            params['max_id'] = max_id
            params.pop('count',None)
        response = requests.get(CommentURL, headers=headers, params=params)
        try:
            data = response.json()
            comments+=parse_comment(data)
            if len(comments) < max_comments:
                if max_comments>100:
                    await asyncio.sleep(random.random()*2+1)
                else:
                    await asyncio.sleep(random.random())
                await get_comment(data['max_id'],comments)
            return data['total_number']
        except Exception as e:
            raise ValueError(f"Server error: {response.text}")
    total_comments = await get_comment(None,comments)
    return [mcp.types.TextContent(
                type='text',
                text=f"总共{total_comments}条评论，获取前{len(comments)}条"
            )]+comments

async def main():
    """Main entry point to run the MCP server."""
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise

if __name__ == "__main__":
    # Initialize and run the server
    asyncio.run(main())
    # asyncio.run(call_tool('WeiboGetHotSearchCommentByUrl',{"url":"https://s.weibo.com/weibo?q=何老师这回是真上桌了","max_comments":"20"}))
    