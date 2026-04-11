# main_gui.py - 自動重建 CSV 與效能優化版
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from adb_core import ADBController
from csv_manager import CSVLogger


class VRAppExtractorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.adb = ADBController()
        self.checkboxes = []

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.title("Meta Quest APK 提取與管理工具")
        self.geometry("600x600")
        self.resizable(False, False)

        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(
            self, text="VR 資安分析：APK 提取產線",
            font=("Arial", 22, "bold")
        ).pack(pady=(15, 10))

        ctk.CTkButton(
            self, text="1. 掃描設備 APP", font=("Arial", 14),
            command=self.scan_apps, width=200
        ).pack(pady=(0, 10))

        frame_select = ctk.CTkFrame(self, fg_color="transparent")
        frame_select.pack(pady=(0, 5))

        ctk.CTkButton(
            frame_select, text="全選", font=("Arial", 12), width=80,
            command=self.select_all
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            frame_select, text="全取消", font=("Arial", 12), width=80,
            command=self.deselect_all
        ).grid(row=0, column=1, padx=10)

        self.scroll_frame = ctk.CTkScrollableFrame(
            self, width=500, height=230, label_text="可提取的 APP 清單"
        )
        self.scroll_frame.pack(pady=(0, 15))

        frame_path = ctk.CTkFrame(self, fg_color="transparent")
        frame_path.pack(pady=(0, 15))

        ctk.CTkButton(
            frame_path, text="2. 選擇儲存資料夾", font=("Arial", 14),
            command=self.choose_directory, width=150
        ).grid(row=0, column=0, padx=(0, 10))

        self.lbl_path = ctk.CTkLabel(
            frame_path, text="尚未選擇", font=("Arial", 12), text_color="gray"
        )
        self.lbl_path.grid(row=0, column=1)

        ctk.CTkButton(
            self, text="3. 提取 APK ＆ 同步報表",
            font=("Arial", 16, "bold"), fg_color="#28a745",
            hover_color="#218838", command=self.download_apk,
            width=320, height=50
        ).pack(pady=(5, 15))

        self.lbl_status = ctk.CTkLabel(
            self, text="狀態: 待命中", font=("Arial", 12), text_color="gray"
        )
        self.lbl_status.pack(side="bottom", pady=10)

    def select_all(self):
        for cb in self.checkboxes:
            cb.select()

    def deselect_all(self):
        for cb in self.checkboxes:
            cb.deselect()

    def choose_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.lbl_path.configure(text=folder)
            self.scan_apps()

    def scan_apps(self):
        self.lbl_status.configure(text="狀態: 正在掃描設備...", text_color="yellow")
        self.update()

        for cb in self.checkboxes:
            cb.destroy()
        self.checkboxes.clear()

        apps = self.adb.get_third_party_apps()
        save_dir = self.lbl_path.cget("text")

        existing_files = []
        if save_dir != "尚未選擇" and os.path.exists(save_dir):
            existing_files = [
                f.replace(".apk", "")
                for f in os.listdir(save_dir) if f.endswith(".apk")
            ]

        if apps:
            new_count = 0
            for pkg in apps:
                is_downloaded = pkg in existing_files
                display_text = f"{pkg} (已存在 ✅)" if is_downloaded else pkg
                text_color = "#888888" if is_downloaded else "white"

                cb = ctk.CTkCheckBox(
                    self.scroll_frame, text=display_text,
                    onvalue=pkg, offvalue="", text_color=text_color
                )
                cb.pack(anchor="w", pady=5, padx=10)

                if not is_downloaded:
                    cb.select()
                    new_count += 1
                self.checkboxes.append(cb)

            self.lbl_status.configure(
                text=f"狀態: 掃描成功！新增 {new_count} 個新 APP",
                text_color="lightgreen"
            )
        else:
            self.lbl_status.configure(text="狀態: 設備中無第三方 APP", text_color="orange")

    def download_apk(self):
        save_dir = self.lbl_path.cget("text")
        if save_dir == "尚未選擇":
            messagebox.showinfo("提示", "請先選擇儲存資料夾。")
            self.choose_directory()
            save_dir = self.lbl_path.cget("text")
            if save_dir == "尚未選擇":
                return

        # 核心改良：即使沒選 App，也要確保 CSV 存在
        logger = CSVLogger(save_dir)

        selected_pkgs = [cb.get() for cb in self.checkboxes if cb.get() != ""]

        if not selected_pkgs:
            self.lbl_status.configure(text="狀態: CSV 已同步 (未選取 APK)", text_color="lightgreen")
            return messagebox.showinfo(
                "提示", "Excel 檔案已確認/建立完畢。\n由於未勾選任何 App，本次未提取 APK。"
            )

        success_count, skip_count, fail_count = 0, 0, 0

        for index, pkg in enumerate(selected_pkgs):
            file_name = f"{pkg}.apk"
            final_local_path = os.path.join(save_dir, file_name)

            if os.path.exists(final_local_path):
                logger.log_app(pkg, file_name, final_local_path)
                skip_count += 1
                continue

            status_text = f"狀態: [{index+1}/{len(selected_pkgs)}] 正在提取 {pkg}..."
            self.lbl_status.configure(text=status_text, text_color="yellow")
            self.update()

            apk_path = self.adb.get_apk_path(pkg)
            if not apk_path:
                fail_count += 1
                continue

            pull_result = self.adb.pull_apk(apk_path, final_local_path)
            if "pulled" in pull_result:
                logger.log_app(pkg, file_name, final_local_path)
                success_count += 1
            else:
                fail_count += 1

        msg = f"✅ 任務完成！\n成功提取：{success_count} 個\n跳過重複：{skip_count} 個"
        if fail_count > 0:
            msg += f"\n❌ 失敗：{fail_count} 個"

        messagebox.showinfo("完成", msg)
        self.scan_apps()


if __name__ == "__main__":
    app = VRAppExtractorGUI()
    app.mainloop()
