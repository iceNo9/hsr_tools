import requests
from bs4 import BeautifulSoup
import csv

url = "https://wiki.biligame.com/sr/%E4%BA%8B%E4%BB%B6%E4%B8%80%E8%A7%88"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
html = response.text

soup = BeautifulSoup(html, "html.parser")

table = soup.find("table", id="CardSelectTr")
if not table:
    raise ValueError("未找到目标表格")

all_rows = table.find_all("tr")
rows = []
for row in all_rows:
    if not hasattr(row, "attrs"):
        continue
    if "divsort" in row.get("class", []) or row.has_attr("data-param1"):
        rows.append(row)

data_list = []

for row in rows:
    tds = row.find_all("td")
    if len(tds) < 5:
        continue

    event_name = tds[1].get_text(strip=True)
    mode = tds[2].get_text(strip=True)

    option_td = tds[3]
    option_texts = []
    for ul in option_td.find_all("ul"):
        for li in ul.find_all("li"):
            option_texts.append(li.get_text(strip=True))
    for dl in option_td.find_all("dl"):
        for dd in dl.find_all("dd"):
            option_texts.append(dd.get_text(strip=True))
    option_text = "\n".join(option_texts)

    version = tds[4].get_text(strip=True)

    data_list.append({
        "事件名称": event_name,
        "模式": mode,
        "选项": option_text,
        "版本": version
    })

csv_file = "events.csv"
with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["事件名称","模式","选项","版本"])
    writer.writeheader()
    writer.writerows(data_list)

print(f"CSV 文件已生成: {csv_file}")
