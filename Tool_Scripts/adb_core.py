# adb_core.py
import subprocess

class ADBController:
    @staticmethod
    def run_command(command):
        try:
            result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
            return result.strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e.output}"

    def get_third_party_apps(self):
        """掃描頭盔內的第三方 APP (附帶嚴格的 ADB 廢話過濾)"""
        output = self.run_command("adb shell pm list packages -3")

        # 如果發生真的執行錯誤
        if output.startswith("Error:"):
            return None

        apps = []
        for line in output.split('\n'):
            line = line.strip()
            # 核心修復：只抓取真正以 'package:' 開頭的行，無視 daemon 啟動訊息
            if line.startswith("package:"):
                apps.append(line.replace("package:", ""))

        return apps if apps else None

    def get_apk_path(self, package_name):
        """取得 APK 所在路徑，自動過濾並只抓取核心的 base.apk"""
        output = self.run_command(f"adb shell pm path {package_name}")
        if "package:" not in output:
            return None

        # 取得所有跟這個 App 有關的 APK 路徑清單
        paths = [line.strip().replace("package:", "") for line in output.strip().split('\n') if line.strip()]

        # 情況 A：如果是 Split APKs (混合體)，我們只挑出包含 'base.apk' 的那一條路徑
        for p in paths:
            if p.endswith("base.apk"):
                print(f"🎯 [精準鎖定] 偵測到混合型 APK ({package_name})，已鎖定主體 base.apk")
                return p

        # 情況 B：如果是早期傳統的單一 APK (沒有拆分)，就直接回傳第一個路徑
        return paths[0]
    def pull_apk(self, remote_path, local_path):
        """將 APK 下載到電腦"""
        return self.run_command(f"adb pull {remote_path} \"{local_path}\"")
