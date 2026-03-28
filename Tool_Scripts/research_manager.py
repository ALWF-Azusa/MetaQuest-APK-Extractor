import csv
import os
import pyperclip
import re
from datetime import datetime

def update_research_master(save_dir):
    csv_path = os.path.join(save_dir, "Master_Progress.csv")
    file_exists = os.path.isfile(csv_path)
    
    # 1. 讀取剪貼簿
    print("⏳ 正在從剪貼簿讀取資料...")
    raw_text = pyperclip.paste()
    
    if not raw_text or len(raw_text.strip()) < 10:
        print("❌ 錯誤：剪貼簿裡沒東西，或是字數太少！請先回網頁 Ctrl+A, Ctrl+C。")
        return

    print(f"📖 已讀取到 {len(raw_text)} 個字元，開始解析...")

    # 2. 解析邏輯
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    print(f"🔍 總共拆解出 {len(lines)} 行文字，正在過濾 App 格式...")
    
    new_apps = []
    i = 0
    while i < len(lines):
        # 判斷標準：這一行有文字，且下一行包含小圓點 •
        if i + 1 < len(lines) and "•" in lines[i+1]:
            name = lines[i]
            info_line = lines[i+1]
            
            # 解析評分與評價
            match_rating = re.search(r"(\d\.\d)\s*\(([\d\.Kk]+)\)", info_line)
            rating = match_rating.group(1) if match_rating else "0.0"
            reviews = match_rating.group(2) if match_rating else "0"
            
            # 解析分類
            info_parts = info_line.split('•')
            category = info_parts[-1].strip() if info_parts else "Unknown"
            
            new_apps.append({
                "App_Name": name,
                "Rating": rating,
                "Reviews": reviews,
                "Category": category,
                "Install_Status": "Pending",
                "APK_Extracted": "No",
                "MobSF_Scanned": "No",
                "Device_Cleared": "No",
                "Record_Date": datetime.now().strftime("%Y-%m-%d")
            })
            i += 3 # 跳過名稱、資訊行、按鈕行
        else:
            i += 1

    print(f"📦 解析完成，符合格式的 App 共有 {len(new_apps)} 個。")

    if not new_apps:
        print("⚠️ 警告：沒抓到任何 App！可能是複製的格式不對（需包含評分那一行）。")
        return

    # 3. 讀取舊資料並合併
    existing_data = {}
    if file_exists:
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_data[row["App_Name"]] = row

    new_add = 0
    for app in new_apps:
        if app["App_Name"] not in existing_data:
            existing_data[app["App_Name"]] = app
            new_add += 1
        else:
            # 更新數據但保留進度
            existing_data[app["App_Name"]]["Rating"] = app["Rating"]
            existing_data[app["App_Name"]]["Reviews"] = app["Reviews"]

    # 4. A-Z 排序並寫入
    sorted_apps = sorted(existing_data.values(), key=lambda x: x["App_Name"].lower())
    headers = ["App_Name", "Rating", "Reviews", "Category", "Install_Status", "APK_Extracted", "MobSF_Scanned", "Device_Cleared", "Record_Date"]
    
    with open(csv_path, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(sorted_apps)
    
    print(f"✨ 成功！新增: {new_add} 個，總計: {len(sorted_apps)} 個項目。")
    print(f"📂 檔案位置: {csv_path}")

if __name__ == "__main__":
    update_research_master(os.getcwd())
