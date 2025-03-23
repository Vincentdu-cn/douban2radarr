import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 常量定义
BASE_URL = "https://movie.douban.com/people/140463388/wish"
BASELINE_FILE = "baseline.json"

def load_baseline():
    """加载基线内容"""
    try:
        with open(BASELINE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("基线文件不存在，将创建新文件")
        return {"movie_name": "", "add_date": ""}

def save_baseline(data):
    """保存基线内容"""
    with open(BASELINE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info("基线文件已更新")

def fetch_wishlist():
    """获取豆瓣想看列表"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"获取豆瓣想看列表失败: {e}")
        return None

def n8n_webhook(title, year):
    """调用n8n_webhook"""
    try:
        response = requests.get(
            "http://192.168.199.99:25100/webhook/douban",
            params={"name": title, "year": year},
            timeout=10
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"调用n8n_webhook失败: {e}")
        return None

def parse_movies(html):
    """解析电影信息"""
    soup = BeautifulSoup(html, 'html.parser')
    movies = []
    
    for item in soup.select('.item.comment-item'):
        # 提取电影名称
        title = item.select_one('.title em').text.strip()
        
        # 从日期中提取年份
        date_str = item.select_one('.intro').text.strip()
        year = date_str[:4] if date_str and len(date_str) >= 4 else None
        
        add_date = item.select_one('.date').text.strip()
        
        movies.append({
            "title": title,
            "year": year,
            "add_date": add_date
        })
    
    return movies

def find_new_movies(current_movies, baseline):
    """
    查找新增电影
    
    参数:
        current_movies (list): 当前电影列表，每个元素是包含title, year, add_date的字典
        baseline (dict): 基线内容，包含movie_name和add_date
        
    返回:
        list: 新增电影列表，如果没有新增电影则返回空列表
        
    逻辑说明:
        1. 如果基线内容为空（首次运行），返回全部当前电影
        2. 将add_date转换为datetime对象进行比较
        3. 如果当前第一部电影的add_date <= 基线add_date，返回空列表
        4. 否则，返回所有add_date > 基线add_date的电影
    """
    if not baseline["add_date"]:
        return current_movies
    
    try:
        baseline_date = datetime.strptime(baseline["add_date"], "%Y-%m-%d")
        current_date = datetime.strptime(current_movies[0]["add_date"], "%Y-%m-%d")
        
        if current_date <= baseline_date:
            return []
            
        return [movie for movie in current_movies 
                if datetime.strptime(movie["add_date"], "%Y-%m-%d") > baseline_date]
    except (ValueError, IndexError) as e:
        logging.error(f"日期格式错误或电影列表为空: {e}")
        return []

def main():
    # 加载基线内容
    baseline = load_baseline()
    
    # 获取当前想看列表
    html = fetch_wishlist()
    if not html:
        return
    
    # 解析电影信息
    current_movies = parse_movies(html)
    if not current_movies:
        logging.warning("未解析到任何电影信息")
        return
    
    # 查找新增电影
    new_movies = find_new_movies(current_movies, baseline)
    
    if new_movies:
        logging.info(f"发现{len(new_movies)}部新电影")
        for movie in new_movies:
            # 调用n8n_webhook
            n8n_res = n8n_webhook(movie['title'], movie['year'])
            logging.info(n8n_res)
        
        # 更新基线内容
        new_baseline = {
            "movie_name": current_movies[0]["title"],
            "add_date": current_movies[0]["add_date"]
        }
        save_baseline(new_baseline)
    else:
        logging.info("没有发现新电影")

if __name__ == "__main__":
    main()
