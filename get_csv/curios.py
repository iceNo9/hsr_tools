# scrape_curios.py
import csv
import requests
from bs4 import BeautifulSoup

# 目标 URL
URL = "https://wiki.biligame.com/sr/%E5%A5%87%E7%89%A9%E4%B8%80%E8%A7%88%EF%BC%88%E5%B7%AE%E5%88%86%EF%BC%89"

# 请求页面
response = requests.get(URL)
response.encoding = 'utf-8'
html = response.text

# 解析页面
soup = BeautifulSoup(html, "html.parser")

# 找到所有数据行
rows = soup.find_all("tr", class_="divsort")

data_list = []

for row in rows:
    # 获取每行 data-param
    name = row.get("data-param1", "").strip()  # 英雄类别
    mode = row.get("data-param1", "").strip()  # 模式
    tag = row.get("data-param4", "").replace(",", " / ").strip()
    get_method = row.get("data-param3", "").strip()
    version = row.get("data-param5", "").strip()
    star = row.get("data-param6", "").strip()
    
    # 获取 td 内的内容
    tds = row.find_all("td")
    if len(tds) >= 6:
        name_text = tds[1].get_text(strip=True)
        effect = tds[5].get_text(strip=True)
    else:
        name_text = ""
        effect = ""

    data_list.append({
        "名称": name_text,
        "模式": mode,
        "TAG": tag,
        "获取方式": get_method,
        "效果": effect,
        "版本": version,
        "星级": star
    })

# CSV 文件名
csv_file = "curios.csv"

# 写入 CSV
with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
    fieldnames = ["名称", "模式", "TAG", "获取方式", "效果", "版本", "星级"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data_list)

print(f"CSV 文件已生成: {csv_file}")
