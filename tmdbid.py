"""
TMDB电影ID查询API服务
通过电影名称查询TMDB电影ID，支持年份过滤
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseSettings
import aiohttp
from typing import Optional, Dict
from dotenv import load_dotenv
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 加载.env文件中的环境变量
load_dotenv()

class Settings(BaseSettings):
    """配置类，用于管理API密钥等设置"""
    TMDB_API_KEY: str = os.getenv("TMDB_API_KEY")  # 从环境变量获取TMDB API密钥

settings = Settings()

# 创建FastAPI应用实例
app = FastAPI(
    title="TMDB Movie ID API",
    description="通过电影名称查询TMDB电影ID的API服务",
    version="1.0.0"
)

class TMDBClient:
    """TMDB API客户端封装类"""
    def __init__(self, api_key: str):
        """初始化TMDB客户端
        Args:
            api_key (str): TMDB API密钥
        """
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"  # TMDB API基础URL
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"  # 认证头信息
        }

    async def search_movie(self, name: str, year: Optional[str] = None) -> Optional[Dict]:
        """搜索电影信息
        Args:
            name (str): 电影名称
            year (Optional[str]): 发行年份（可选）
        Returns:
            Optional[Dict]: 返回匹配的电影信息，如果没有找到则返回None
        """
        # 记录原始name
        logger.info(f"原始name: {name}")
        
        # 分割name，取第一个
        search_name = name.split("/")[0].strip()
        
        url = f"{self.base_url}/search/movie"
        params = {
            "query": search_name,
            "include_adult": "false",  # 排除成人内容
            "language": "zh",  # 使用中文
            "page": 1  # 第一页
        }
        if year:
            params["year"] = year  # 添加年份过滤条件

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["results"]:
                        # 验证title是否包含在原始name中
                        result = data["results"][0]
                        if result["title"] in name:
                            logger.info(f"查询成功: {result}")
                            return result
                        else:
                            logger.warning(f"查询结果不匹配: {result['title']} 不在 {name} 中")
                            return None
                    else:
                        logger.warning("未找到匹配的电影")
                else:
                    logger.warning(f"API请求失败，状态码: {response.status}")
                return None

# 初始化TMDB客户端
tmdb_client = TMDBClient(settings.TMDB_API_KEY)

@app.get("/movie")
async def get_movie_id(name: str, year: str = None):
    """获取电影ID的API接口
    Args:
        name (str): 电影名称
        year (str): 发行年份（可选）
    Returns:
        dict: 包含电影ID、标题和年份的字典
    Raises:
        HTTPException: 如果未找到电影或发生错误
    """
    try:
        movie_data = await tmdb_client.search_movie(name, year)
        quality = 7  # 英文电影，quality为7，表示设置为Customized
        if not movie_data:
            raise HTTPException(status_code=404, detail="[Info] Movie not found!")
        if movie_data['original_language'] != "en":
            quality = 9
        return {
            "id": movie_data["id"],  # 电影ID
            "title": movie_data["title"],  # 电影标题
            "year": movie_data["release_date"][:4] if movie_data["release_date"] else None,  # 发行年份
            "quality": quality  # 当非英文时，quality为8，表示设置为1080P-Language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # 启动FastAPI服务
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=26000)
