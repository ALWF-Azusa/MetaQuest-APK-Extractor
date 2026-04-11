@echo off
:: 1. 使用絕對路徑啟動 Conda 環境 (指向你的 Miniconda 安裝路徑)
call C:\ProgramData\miniconda3\Scripts\activate.bat quest_env

:: 2. 執行你的程式
python Tool_Scripts/main_gui.py

:: 3. 程式關閉後不要立刻關掉視窗，方便看報錯
pause