import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==========================================
# 💡 這裡可以自訂你的「翻譯辭典」
# 格式："包名": "你想要顯示的名稱"
# ==========================================
KNOWN_APPS = {
    "com.vrchat.oculus.quest": "VRChat",
    "com.facebook.orca": "Messenger (VR)",
    "com.whatsapp": "WhatsApp",
    "VirtualDesktop.Android": "Virtual Desktop",
    "com.oculus.tv": "Meta Quest TV"
}

checkboxes = []  # 存放動態生成的打勾方塊

def run_adb_command(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"

def scan_apps():
    lbl_status.configure(text="狀態: 正在掃描設備...", text_color="yellow")
    app.update()

    # 清空舊的清單
    for cb in checkboxes:
        cb.destroy()
    checkboxes.clear()

    output = run_adb_command("adb shell pm list packages -3")
    
    if "Error" in output or not output:
        messagebox.showerror("錯誤", "掃描失敗！請確認 Quest 2 已連線。")
        lbl_status.configure(text="狀態: 掃描失敗", text_color="red")
        return

    apps = [pkg.replace("package:", "").strip() for pkg in output.split('\n') if pkg.strip()]
    
    if not apps:
        lbl_status.configure(text="狀態: 找不到第三方 APP", text_color="red")
        return

    # 動態生成打勾方塊
    for pkg in apps:
        # 如果在辭典裡有建檔，就顯示「中文名 (包名)」，否則只顯示包名
        display_name = f"{KNOWN_APPS[pkg]}  ({pkg})" if pkg in KNOWN_APPS else pkg
        
        cb = ctk.CTkCheckBox(scrollable_frame, text=display_name, onvalue=pkg, offvalue="")
        cb.pack(anchor="w", pady=5, padx=10)
        checkboxes.append(cb)

    lbl_status.configure(text=f"狀態: 掃描成功！共找到 {len(apps)} 個 APP", text_color="lightgreen")

def choose_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        lbl_path.configure(text=folder_selected)

def download_apk():
    # 找出所有被打勾的包名
    selected_pkgs = [cb.get() for cb in checkboxes if cb.get() != ""]
    save_dir = lbl_path.cget("text")

    if not selected_pkgs:
        messagebox.showwarning("警告", "請至少勾選一個 APP！")
        return
    if save_dir == "尚未選擇":
        messagebox.showwarning("警告", "請先選擇儲存位置！")
        return

    success_count = 0
    # 開始批量迴圈下載
    for index, pkg in enumerate(selected_pkgs):
        lbl_status.configure(text=f"狀態: [{index+1}/{len(selected_pkgs)}] 正在處理 {pkg}...", text_color="yellow")
        app.update()
        
        path_output = run_adb_command(f"adb shell pm path {pkg}")
        if "Error" in path_output or not path_output:
            continue # 找不到路徑就跳過這個，抓下一個

        apk_path = path_output.replace("package:", "").strip()
        local_path = os.path.join(save_dir, f"{pkg}.apk")
        
        pull_output = run_adb_command(f"adb pull {apk_path} \"{local_path}\"")
        if "pulled" in pull_output:
            success_count += 1

    # 總結報告
    if success_count == len(selected_pkgs):
        messagebox.showinfo("成功", f"全部 {success_count} 個 APP 提取成功！\n已儲存至：{save_dir}")
        lbl_status.configure(text="狀態: 批量提取完成！", text_color="lightgreen")
    else:
        messagebox.showwarning("部分完成", f"預計抓取 {len(selected_pkgs)} 個，成功 {success_count} 個。\n請檢查連線或儲存空間。")
        lbl_status.configure(text="狀態: 部分提取失敗", text_color="orange")

# ================= 介面設計 =================
app = ctk.CTk()
app.title("Meta Quest 批量 APK 提取器")
app.geometry("600x550")
app.resizable(False, False)

lbl_title = ctk.CTkLabel(app, text="VR 資安分析：APK 批量提取器", font=("Arial", 22, "bold"))
lbl_title.pack(pady=(15, 10))

btn_scan = ctk.CTkButton(app, text="1. 掃描設備 APP", font=("Arial", 14), command=scan_apps, width=200)
btn_scan.pack(pady=(0, 10))

# 建立可滾動的區域來放打勾清單
scrollable_frame = ctk.CTkScrollableFrame(app, width=500, height=200, label_text="可提取的 APP 清單 (可複選)")
scrollable_frame.pack(pady=(0, 15))

frame_path = ctk.CTkFrame(app, fg_color="transparent")
frame_path.pack(pady=(0, 15))
btn_path = ctk.CTkButton(frame_path, text="2. 選擇儲存位置", font=("Arial", 14), command=choose_directory, width=150)
btn_path.grid(row=0, column=0, padx=(0, 10))
lbl_path = ctk.CTkLabel(frame_path, text="尚未選擇", font=("Arial", 12), text_color="gray")
lbl_path.grid(row=0, column=1)

btn_download = ctk.CTkButton(app, text="3. 批量提取選中的 APK", font=("Arial", 16, "bold"), fg_color="#28a745", hover_color="#218838", command=download_apk, width=250, height=45)
btn_download.pack(pady=(5, 15))

lbl_status = ctk.CTkLabel(app, text="狀態: 待命中", font=("Arial", 12), text_color="gray")
lbl_status.pack(side="bottom", pady=10)

app.mainloop()
