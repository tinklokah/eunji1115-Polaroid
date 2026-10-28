import streamlit as st
import os
import csv

# 設定網頁標題
st.set_page_config(page_title="即時銷量監控儀表板", page_icon="🔒", layout="centered")

# ================= 🔐 密碼設定區 =================
APP_PASSWORD = "0818" 

def check_password():
    """驗證密碼的邏輯"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # 如果還沒登入，顯示密碼輸入畫面
    st.title("🔒 銷量監控儀表板 (鎖定中)")
    st.write("此頁面受密碼保護，請輸入密碼以繼續。")
    
    password_input = st.text_input("請輸入密碼：", type="password")
    if st.button("登入"):
        if password_input == APP_PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ 密碼錯誤，請重新輸入。")
            
    return False

# 如果密碼沒通過，直接停止執行後續網頁內容
if not check_password():
    st.stop()
# ===============================================

# 🟢 密碼通過後的真實儀表板內容
st.title("📊 銷量即時監控與有效單排行榜")

# 🔄 新增：專屬的重新整理按鈕（點了只會更新資料，不會要求重新輸入密碼！）
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.success("🔓 驗證成功！歡迎回來。")
with col_top2:
    if st.button("🔄 重新整理資料", use_container_width=True):
        st.rerun()

HISTORY_FILE = "history.csv"

def get_clean_ranked_records():
    if not os.path.exists(HISTORY_FILE):
        return [], 0
    
    active_items = []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for row in csv.reader(f):
                if len(row) >= 4:
                    diff = int(row[2])
                    if diff > 0:
                        active_items.append(diff)
                    elif diff < 0:
                        target = abs(diff)
                        if target in active_items:
                            active_items.remove(target)
                        else:
                            active_items.append(diff)
    except:
        pass
    
    net_total = sum(active_items)
    ranked_positive = [x for x in active_items if x > 0]
    ranked_positive.sort(reverse=True)
    
    return ranked_positive, net_total

ranked_list, net_total = get_clean_ranked_records()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="💰 淨成交總量", value=f"{net_total} 單")
with col2:
    st.metric(label="🏆 有效加單筆數", value=f"{len(ranked_list)} 筆")

st.markdown("---")

st.subheader("🔥 有效加單排行榜（由大到小排序）")
if not ranked_list:
    st.info("目前尚無有效加單紀錄，或已被全數抵消。")
else:
    for i, val in enumerate(ranked_list, 1):
        st.markdown(f"**第 {i} 名：** `+{val}`")

st.markdown("---")

st.subheader("📜 歷史變動明細紀錄")
if os.path.exists(HISTORY_FILE):
    records = []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for row in csv.reader(f):
                if len(row) >= 4:
                    records.append({
                        "時間": row[0],
                        "事件類型": row[1],
                        "變動量": row[2],
                        "當前總量": row[3]
                    })
        if records:
            st.dataframe(records[::-1], use_container_width=True)
        else:
            st.write("目前尚無歷史明細。")
    except:
        st.write("讀取歷史檔案時發生錯誤。")
else:
    st.warning("找不到 history.csv 檔案（當背景監控程式有產生異動時才會建立）。")
