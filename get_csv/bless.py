import requests
from bs4 import BeautifulSoup
import csv

url = "https://wiki.biligame.com/sr/%E7%A5%9D%E7%A6%8F%E4%B8%80%E8%A7%88%EF%BC%88%E5%B7%AE%E5%88%86%EF%BC%89"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
html = response.text

soup = BeautifulSoup(html, "html.parser")

# 找到表格
table = soup.find("table", id="CardSelectTr")
if not table:
    raise ValueError("未找到目标表格")

# 筛选行
all_rows = table.find_all("tr")
rows = []
for row in all_rows:
    if not hasattr(row, "attrs"):
        continue
    # divsort 或者有 data-param1 都是数据行
    if "divsort" in row.get("class", []) or row.has_attr("data-param1"):
        rows.append(row)

data_list = []

for row in rows:
    tds = row.find_all("td")
    if len(tds) < 7:
        continue

    name = tds[1].get_text(strip=True)
    destiny = tds[2].get_text(strip=True)
    mode = tds[3].get_text(strip=True)
    tag = tds[4].get_text(strip=True)
    effect = tds[5].get_text(strip=True)
    version = tds[6].get_text(strip=True)

    data_list.append({
        "名称": name,
        "命途": destiny,
        "模式": mode,
        "TAG": tag,
        "效果": effect,
        "版本": version
    })

# 写入 CSV
csv_file = "blessing_diff.csv"
with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["名称","命途","模式","TAG","效果","版本"])
    writer.writeheader()
    writer.writerows(data_list)

print(f"CSV 文件已生成: {csv_file}")
