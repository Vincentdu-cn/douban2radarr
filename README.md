# douban2radarr
监控豆瓣”想看“列表，有更新时自动同步到Radarr中。
## 介绍
<img width="666" alt="shapes at 25-03-24 15 34 41" src="https://github.com/user-attachments/assets/091e49e8-b57d-4dde-99f0-1926fd2c81e3" />

1. 定时获取豆瓣”想看“列表
定时运行douban_wishlist_monitor.py，获取新添加电影，返回name（心之全蚀 / Total Eclipse / 全蚀狂爱(台) / Eclipse totale），year
2. imdbid.py处理name分割，为防止豆瓣中电影名称第一选择和TMDB中电影名称不一致，判断返回title是否在name中，返回ID
3. Radarr添加电影
## n8n流程
除了定时任务和imdbid.py，后面任务在n8n中运行。
![image](https://github.com/user-attachments/assets/149829fc-ca20-429c-8b0e-ec85c274abe7)

## [重写整个流程通过n8n实现](https://github.com/Vincentdu-cn/douban2radarr/blob/main/n8n/README.md)
- 从baseline.json提取基线信息
- 获取豆瓣“想看”,解析HTML提取电影信息
- 对比列表中第一个电影的add_date和基线add_date，如果有更新，则更新add_date基线文件，
  并开始循环遍历每部电影，JSON格式{"movie_name": Array, "year": Int, "add_date": String}
- 二层循环遍历数组movie_name（["心之全蚀","Total Eclipse","全蚀狂爱(台)","Eclipse totale"]）
- 传入movie_name和year去请求TMDB API，判断第一个结果的original_title是否包含在movie_name.ToString中，
  直到匹配到后请求Radarr API加入电影
