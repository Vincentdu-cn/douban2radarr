"""
通过TMDB ID添加电影
"""
"""
Curl 格式
curl -X 'POST' \
  'https://radarr.cn/api/v3/movie?apikey=$radarr_key' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "add_movie",
    "qualityProfileId": 7,
    "tmdbId": 36834,
    "rootFolderPath": "/video/Movies",
    "addOptions": {
        "ignoreEpisodesWithFiles": true,
        "ignoreEpisodesWithoutFiles": true,
        "monitor": "movieOnly",
        "searchForMovie": false,
        "addMethod": "manual"
    }
}'
"""

import requests
import os

# 设置 API 密钥
radarr_key = os.getenv('RADARR_KEY')  # 假设 API 密钥存储在环境变量中

# 请求的 URL
url = 'https://radarr.cn/api/v3/movie'

# 请求头
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# 请求体，对应手动添加电影时需要设置的选项
data = {
    "title": "add_movie",
    # qualityProfileId可自定义配置电影质量
    "qualityProfileId": 7,
    "tmdbId": 36834,
    "rootFolderPath": "/video/Movies",
    "addOptions": {
        "ignoreEpisodesWithFiles": True,
        "ignoreEpisodesWithoutFiles": True,
        "monitor": "movieOnly",
        "searchForMovie": False,
        "addMethod": "manual"
    }
}

# 发送 POST 请求
response = requests.post(url, headers=headers, json=data, params={'apikey': radarr_key})

# 打印响应
print(response.status_code)
print(response.json())
