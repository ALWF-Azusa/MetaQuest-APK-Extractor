# MetaQuest-APK-Extractor
這是一個用於 Meta Quest VR 資安研究的自動化 APK 提取 GUI 工具。
<img width="596" height="578" alt="image" src="https://github.com/user-attachments/assets/6df0f782-998f-43bb-a161-a5efefc27330" />

此工具應用於Meta Quest VR，若需要使用請先將ADB以及Quest的開發人員模式開啟。

需要安裝Python 以及 使用pip install customtkinter
# 🥽 Meta Quest APK Extractor & Research Manager

## 🚀 About The Project
This project is an automated pipeline designed for cybersecurity researchers to extract, manage, and inventory Android application packages (APKs) from Meta Quest devices. It solves the complexity of handling thousands of VR app samples by streamlining the workflow from device extraction to static analysis readiness.

## ✨ Key Features
* **Automated Extraction**: Single-click extraction of third-party VR apps via ADB with a custom GUI.
* **Smart Inventory Management**: 
    * Automatically generates and updates `VR_App_Inventory.csv` in the project root.
    * Tracks package names, file sizes, and extraction dates.
* **Research-Grade Classification**: 
    * Distinguishes between **System Built-in** (native Quest components) and **Meta Store Apps** (including first-party and third-party apps).
    * Prevents duplicate extractions and maintains a clean research ledger.
* **Optimized for Analysis**: Designed to output standardized APK files compatible with static analysis tools like **MobSF**.

## 📁 Recommended Project Structure
```text
E:\Quest apk\
 ├── VR_App_Inventory.csv      # Auto-generated master inventory
 ├── 01_Extracted_APKs\       # Storage for base.apk samples
 ├── 02_MobSF_Reports\        # Future security analysis reports
