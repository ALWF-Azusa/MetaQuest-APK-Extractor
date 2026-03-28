import csv
import os
import subprocess
import re
from datetime import datetime

class CSVLogger:
    def __init__(self, save_dir):
        # 要求一：自動上移至上一層 (E:\Quest apk)
        if os.path.basename(save_dir) == "01_Extracted_APKs":
            report_dir = os.path.dirname(save_dir)
        else:
            report_dir = save_dir 
            
        self.csv_path = os.path.join(report_dir, "VR_App_Inventory.csv")
        self.fieldnames = ["No.", "App_Name (官方名稱)", "套件名稱 (Package)", "APK 檔名", "檔案大小", "提取日期", "分類", "MobSF 弱點備註"]
        
        # 要求三：真正的 Meta 官方/系統元件清單 (這部分會自動標記)
        # 不在這裡面的，即使是 com.oculus 開頭也會被歸類為第三方
        self.meta_official_list = {
            "com.oculus.vrprivacycheckup": "Privacy and social settings",
            "com.oculus.accountscenter": "Accounts Center",
            "com.oculus.helpcenter": "Help Center",
            "com.facebook.arvr.quillplayer": "VR Animation Player",
            "com.meta.handseducationmodule": "First Steps With Hand Tracking",
            "com.meta.shell.env.vista.central": "Quest Environment: Vista Central",
            "com.meta.shell.env.footprint.haven2025": "Quest Environment: Haven 2025",
            "com.oculus.browser": "Meta Quest Browser",
            "com.oculus.tv": "Meta Quest TV"
        }
        
        self.initialize_csv()

    def initialize_csv(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def get_app_label_via_adb(self, package_name):
        """要求二：更精準地從系統抓取 App 顯示名稱"""
        try:
            # 使用 dumpsys 並過濾特定的 Label 欄位
            cmd = f'adb shell "dumpsys package {package_name} | grep -E \'label=\'"'
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8')
            
            # 尋找第一個出現的 label= 內容
            match = re.search(r'label=([^\s]+)', output)
            if match:
                label = match.group(1).replace('"', '').replace("'", "")
                return label
        except:
            pass
        return ""

    def log_app(self, package_name, apk_name, local_path):
        file_size = "Unknown"
        if os.path.exists(local_path):
            size_bytes = os.path.getsize(local_path)
            file_size = f"{size_bytes / (1024*1024):.2f} MB"

        rows = []
        if os.path.exists(self.csv_path):
            with open(self.csv_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

        existing_packages = [row["套件名稱 (Package)"] for row in rows]

        if package_name not in existing_packages:
            next_no = len(rows) + 1
            
            # 優先從官方清單比對 (要求三)
            if package_name in self.meta_official_list:
                category = "Meta官方/內建"
                final_name = f"[Meta官方] {self.meta_official_list[package_name]}"
            else:
                # 不在官方清單內，統一視為第三方 (要求二)
                category = "第三方應用"
                # 嘗試從設備抓取真實名稱
                fetched_name = self.get_app_label_via_adb(package_name)
                final_name = fetched_name if fetched_name else ""

            new_row = {
                "No.": next_no,
                "App_Name (官方名稱)": final_name,
                "套件名稱 (Package)": package_name,
                "APK 檔名": apk_name,
                "檔案大小": file_size,
                "提取日期": datetime.now().strftime("%Y-%m-%d"),
                "分類": category,
                "MobSF 弱點備註": ""
            }
            
            with open(self.csv_path, mode='a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(new_row)
            print(f"✅ 已紀錄: {final_name} [{category}]")
            
        else:
            # 更新已存在的資料 (不碰 App_Name)
            for row in rows:
                if row["套件名稱 (Package)"] == package_name:
                    row["檔案大小"] = file_size
                    row["提取日期"] = datetime.now().strftime("%Y-%m-%d")
            
            with open(self.csv_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"🔄 已更新: {package_name}")
