# douban2radarr
监控豆瓣”想看“列表，有更新时自动同步到Radarr中。
## 流程
<img width="611" alt="shapes at 25-03-23 15 09 26" src="https://github.com/user-attachments/assets/c8119546-9d94-42d7-96fe-bdbb72f7c287" />

1. 定时获取豆瓣”想看“列表
定时运行douban_wishlist_monitor.py，获取新添加电影，返回name（心之全蚀 / Total Eclipse / 全蚀狂爱(台) / Eclipse totale），year
2. imdbid.py处理name分割，为防止豆瓣中电影名称第一选择和TMDB中电影名称不一致，判断返回title是否在name中，返回ID
3. Radarr添加电影
## n8n流程
除了定时任务和imdbid.py，后面任务在n8n中运行。
![image](https://github.com/user-attachments/assets/47a99759-782b-4af5-a855-0dab0e7fce7f)
