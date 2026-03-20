import streamlit as st
import os
import pandas as pd
import warnings

# 忽略 openpyxl 讀取資料驗證的警告
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# 網頁設定
st.set_page_config(page_title="Excel 病患姓名搜尋系統", layout="wide")
st.title("🔍 Excel 病患姓名搜尋系統")
st.write("這個網頁應用程式可以幫助您跨資料夾、跨 Excel 分頁搜尋病患姓名。")

# 建立輸入區塊
search_term = st.text_input("📝 請輸入病患姓名：", help="輸入姓名後按下 Enter 或點擊搜尋按鈕")
search_btn = st.button("🚀 開始搜尋")

if search_btn or search_term:
    search_term = search_term.strip()
    if not search_term:
        st.warning("⚠️ 請輸入要搜尋的姓名！")
    else:
        # 設定搜尋目錄為程式所在目錄
        base_dir = os.path.dirname(os.path.abspath(__file__))
        results = []
        file_count = 0
        
        with st.spinner(f"⏳ 正在搜尋「{search_term}」... 請稍候 (掃描多個 Excel 檔案可能需要幾十秒鐘)"):
            try:
                for root, dirs, files in os.walk(base_dir):
                    for file in files:
                        if file.endswith('.xlsx') and not file.startswith('~'):
                            file_count += 1
                            filepath = os.path.join(root, file)
                            folder_name = os.path.basename(root)
                            if folder_name == os.path.basename(base_dir):
                                folder_name = "主目錄"

                            try:
                                xls = pd.ExcelFile(filepath)
                                for sheet_name in xls.sheet_names:
                                    # 讀取 Excel 的每一頁，全當字串處理避免格式錯誤
                                    df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
                                    mask = df.apply(lambda x: x.astype(str).str.contains(search_term, na=False, case=False))
                                    
                                    if mask.any().any():
                                        matched_rows = df[mask.any(axis=1)]
                                        for idx, row in matched_rows.iterrows():
                                            row_items = []
                                            for val in row.values:
                                                if pd.notna(val) and str(val).strip() != 'nan':
                                                    row_items.append(str(val).strip())
                                            
                                            row_text = " | ".join(row_items)
                                            results.append({
                                                "📂 年份/資料夾": folder_name,
                                                "📄 檔名": file,
                                                "📑 分頁": sheet_name,
                                                "📋 詳細資料 (日期/病歷號/主治醫師等)": row_text
                                            })
                            except Exception:
                                pass
            except Exception as e:
                st.error(f"❌ 搜尋發生錯誤: {str(e)}")
        
        # 顯示搜尋結果
        if results:
            st.success(f"✅ 搜尋完成！共掃描了 {file_count} 個 Excel 檔案，找到 **{len(results)}** 筆結果。")
            df_results = pd.DataFrame(results)
            # 使用 st.dataframe 讓使用者可以輕易滾動、排序與觀看資料
            st.dataframe(df_results, use_container_width=True)
        else:
            st.info(f"ℹ️ 搜尋完成！掃描了 {file_count} 個 Excel 檔案，但找不到符合「{search_term}」的資料。")

st.markdown("---")
st.markdown("💡 **提示：** ")
st.markdown("- **本機測試：** 您現在看到的是本機運行版本。")
st.markdown("- **發佈為公開網址：** 若想讓大家「點擊網址就能用」，您可以將這個程式 (.py) 以及資料夾內的 Excel 檔案上傳到 GitHub，並連接到 **Streamlit Community Cloud**，它會為您免費生成一個可以分享給所有人的專屬網址！")
