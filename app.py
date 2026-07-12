import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 전체 화면 설정
st.set_page_config(page_title="하이브리드 컨테이너 위치 관제 시스템", layout="wide", page_icon="📦")

# 2. 고도화된 하이브리드 그리드 및 가이드라인 기반 CSS 스타일 정의
st.markdown("""
    <style>
    .vertical-grid-container {
        display: table;
        border-collapse: collapse;
        margin: 15px 0;
        font-family: 'Segoe UI', sans-serif;
        width: 100%;
        max-width: 100%;
        table-layout: fixed;
    }
    .grid-row { display: table-row; }
    .grid-cell {
        display: table-cell;
        border: 1px solid #555555;
        padding: 6px 4px;
        text-align: center;
        height: 65px; 
        min-height: 65px;
        max-height: 65px;
        box-sizing: border-box;
        vertical-align: middle;
        font-size: clamp(10px, 1.1vw, 14px); 
        font-weight: 500;
        background-color: #ffffff;
        color: #1e293b;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: normal; 
        word-break: break-all;
        transition: all 0.15s ease;
    }
    .grid-cell:hover {
        filter: brightness(0.85);
        box-shadow: inset 0 0 8px rgba(0,0,0,0.3);
    }
    .cell-header {
        background-color: #eef1f6;
        font-weight: bold;
        color: #1e293b;
        font-size: clamp(9px, 1vw, 13px);
    }
    .sub-header {
        background-color: #334155 !important;
        font-size: clamp(10px, 0.9vw, 13px);
        color: #ffffff !important;
        font-weight: bold;
        height: 40px;
    }
    
    /* 상태별 색상 및 패턴 스타일 */
    .status-normal { background-color: #ffffff; color: #1e293b; }
    .status-search { background-color: #fff200 !important; font-weight: bold; border: 3px solid #000000 !important; }
    .status-shipout { background-color: #fff200 !important; color: #000000 !important; font-weight: bold; }
    .status-direct { background-color: #16a34a !important; color: #ffffff !important; font-weight: bold; }
    .status-waterproof { background-color: #2563eb !important; color: #ffffff !important; font-weight: bold; }
    .status-repair { background-color: #dc2626 !important; color: #ffffff !important; font-weight: bold; }
    .status-shipback { background-color: #ea580c !important; color: #ffffff !important; font-weight: bold; }
    
    .status-battery { 
        background: linear-gradient(135deg, #cbd5e1 25%, #94a3b8 25%, #94a3b8 50%, #cbd5e1 50%, #cbd5e1 75%, #94a3b8 75%, #94a3b8 100%) !important;
        background-size: 15px 15px !important;
        color: #0f172a !important;
        font-weight: bold;
    }
    
    .main-title { font-size: 26px; font-weight: bold; color: #0f172a; margin-bottom: 2px; }
    .section-title {
        font-size: 16px;
        font-weight: bold;
        color: #1e293b;
        margin-top: 25px;
        margin-bottom: 10px;
        border-left: 5px solid #2563eb;
        padding-left: 10px;
    }
    .status-lbl {
        font-size: 9px;
        display: inline-block;
        background-color: rgba(0,0,0,0.12);
        padding: 1px 3px;
        border-radius: 3px;
        margin-top: 3px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📦 하이브리드 컨테이너 위치 관제 시스템 (사용자 정의 레이아웃)</div>', unsafe_allow_html=True)

# ----------------- [📌 사용자 정의 레이아웃 고정 틀 정의] -----------------
SD_LOCS = ['SD-3', 'SD-2', 'SD-1', 'SD1', 'SD2', 'SD3', 'SD4', 'SD5', 'SD6', 'SDE-1', 'SD7', 'SD8', 'SD9', 'SD10', 'SD11', 'SD12', 'SD13', 'SD14', 'SD15', 'SDE-2', 'SD16', 'SD17', 'SD18', 'SD19', 'NEW WATERPROOF', 'OUTPUT STATION', 'SDE-3', 'SDX3', 'SDX2', 'SDX1']

# 💡 질문자님이 변경하신 SF 리스트 완벽 적용
SF_EVEN_H = [f"SF{i}" for i in range(2, 61, 2)] + ['SF61', 'SF62', 'SF63', 'SF64', 'SF65','SF66', 'SF67', 'SFE-1', 'SFE-2', 'SF68', 'SF69', 'SF70']
SF_ODD_H = [f"SF{i}" for i in range(1, 60, 2)]
SF_SP_H = ['SF71', 'SF72', 'SF73', 'SF74']

NF_EVEN_H = [f"NF{i}" for i in range(2, 69, 2)]
NF_ODD_H = [f"NF{i}" for i in range(1, 69, 2)]
DOC_LOCS = ['DOC1', 'DOC2']

STATUS_OPTIONS = ["일반", "출하(노랑)", "직출하(초록)", "수밀존(파랑)", "배터리교체(사선)", "수리필요(빨강)", "쉽백(주황)"]
STATUS_CSS_MAP = {
    "일반": "status-normal", "출하(노랑)": "status-shipout", "직출하(초록)": "status-direct",
    "수밀존(파랑)": "status-waterproof", "배터리교체(사선)": "status-battery",
    "수리필요(빨강)": "status-repair", "쉽백(주황)": "status-shipback"
}

# ----------------- [💡 데이터베이스 및 파일 저장/로드 정의] -----------------
if "master_db" not in st.session_state:
    def init_cells(length):
        return [{"no": "", "status": "일반"} for _ in range(length)]
    
    st.session_state.master_db = {
        "sd_zone": {"r1": init_cells(len(SD_LOCS)), "r2": init_cells(len(SD_LOCS))},
        "sf_zone": {
            "even_r1": init_cells(len(SF_EVEN_H)), "even_r2": init_cells(len(SF_EVEN_H)), 
            "odd_r1": init_cells(len(SF_ODD_H)), "odd_r2": init_cells(len(SF_ODD_H)),
            "sp_r1": init_cells(len(SF_SP_H)), "sp_r2": init_cells(len(SF_SP_H))
        },
        "nf_zone": {"even_r1": init_cells(len(NF_EVEN_H)), "even_r2": init_cells(len(NF_EVEN_H)), "odd_r1": init_cells(len(NF_ODD_H)), "odd_r2": init_cells(len(NF_ODD_H))},
        "doc_zone": {"r1": init_cells(len(DOC_LOCS)), "r2": init_cells(len(DOC_LOCS))},
    }

db = st.session_state.master_db

# [💾 로컬 엑셀 쓰기 함수]
def save_to_local_excel(zone_key, file_name):
    rows_data = []
    if zone_key == "sd_zone":
        for idx, loc in enumerate(SD_LOCS):
            rows_data.append([loc, db["sd_zone"]["r1"][idx]["no"], db["sd_zone"]["r2"][idx]["no"]])
    elif zone_key == "sf_zone":
        for idx, loc in enumerate(SF_EVEN_H):
            rows_data.append([loc, db["sf_zone"]["even_r1"][idx]["no"], db["sf_zone"]["even_r2"][idx]["no"]])
        for idx, loc in enumerate(SF_ODD_H):
            rows_data.append([loc, db["sf_zone"]["odd_r1"][idx]["no"], db["sf_zone"]["odd_r2"][idx]["no"]])
        for idx, loc in enumerate(SF_SP_H):
            rows_data.append([loc, db["sf_zone"]["sp_r1"][idx]["no"], db["sf_zone"]["sp_r2"][idx]["no"]])
    elif zone_key == "nf_zone":
        for idx, loc in enumerate(NF_EVEN_H):
            rows_data.append([loc, db["nf_zone"]["even_r1"][idx]["no"], db["nf_zone"]["even_r2"][idx]["no"]])
        for idx, loc in enumerate(NF_ODD_H):
            rows_data.append([loc, db["nf_zone"]["odd_r1"][idx]["no"], db["nf_zone"]["odd_r2"][idx]["no"]])

    try:
        pd.DataFrame(rows_data).to_excel(file_name, header=False, index=False)
    except Exception as e:
        st.error(f"❌ 엑셀 저장 실패: {e}")

# [⚙️ 로컬 엑셀 직접 읽기 엔진]
if "excel_loaded" not in st.session_state:
    def load_local_excel(file_name, zone_key):
        try:
            df = pd.read_excel(file_name, header=None)
            excel_map = {}
            for _, row in df.iterrows():
                if pd.isna(row[0]): continue
                loc_name = str(row[0]).strip()
                val_r1 = str(row[1]).strip() if len(row) > 1 and pd.notna(row[1]) else ""
                val_r2 = str(row[2]).strip() if len(row) > 2 and pd.notna(row[2]) else ""
                if val_r1.endswith('.0'): val_r1 = val_r1[:-2]
                if val_r2.endswith('.0'): val_r2 = val_r2[:-2]
                excel_map[loc_name] = {"r1": val_r1, "r2": val_r2}
            
            if zone_key == "nf_zone":
                for idx, loc in enumerate(NF_EVEN_H):
                    if loc in excel_map: db["nf_zone"]["even_r1"][idx] = {"no": excel_map[loc]["r1"], "status": "일반"}
                    if loc in excel_map: db["nf_zone"]["even_r2"][idx] = {"no": excel_map[loc]["r2"], "status": "일반"}
                for idx, loc in enumerate(NF_ODD_H):
                    if loc in excel_map: db["nf_zone"]["odd_r1"][idx] = {"no": excel_map[loc]["r1"], "status": "일반"}
                    if loc in excel_map: db["nf_zone"]["odd_r2"][idx] = {"no": excel_map[loc]["r2"], "status": "일반"}
                for idx, loc in enumerate(DOC_LOCS):
                    if loc in excel_map: db["doc_zone"]["r1"][idx] = {"no": excel_map[loc]["r1"], "status": "일반"}
                    if loc in excel_map: db["doc_zone"]["r2"][idx] = {"no": excel_map[loc]["r2"], "status": "일반"}
            elif zone_key == "sf_zone":
                for idx, loc in enumerate(SF_EVEN_H):
                    if loc in excel_map: db["sf_zone"]["even_r1"][idx] = {"no": excel_map[loc]["r1"], "status": "일반"}
                    if loc in excel_map: db["sf_zone"]["even_r2"][idx] = {"no": excel_map[loc]["r2"], "status": "일반"}
                for idx, loc in enumerate(SF_ODD_H):
                    if loc in excel_map: db["sf_zone"]["odd_r1"][idx] = {"no": excel_map[loc]["r1"], "status": "일반"}
                    if loc in excel_map: db["sf_zone"]["odd_r2"][idx] = {"no": excel_map[loc]["r2"], "status": "일반"}
                for idx, loc in enumerate(SF_SP_H):
                    if loc in excel_map: db["sf_zone"]["sp_r1"][idx] = {"no": excel_map[loc]["r1"], "status": "일반"}
                    if loc in excel_map: db["sf_zone"]["sp_r2"][idx] = {"no": excel_map[loc]["r2"], "status": "일반"}
            elif zone_key == "sd_zone":
                for idx, loc in enumerate(SD_LOCS):
                    if loc in excel_map: db["sd_zone"]["r1"][idx] = {"no": excel_map[loc]["r1"], "status": "일반"}
                    if loc in excel_map: db["sd_zone"]["r2"][idx] = {"no": excel_map[loc]["r2"], "status": "일반"}
        except Exception as e:
            pass

    load_local_excel("NF.xlsx", "nf_zone")
    load_local_excel("SF.xlsx", "sf_zone")
    load_local_excel("SD.xlsx", "sd_zone")
    st.session_state.excel_loaded = True


# ----------------- [🎯 인터랙티브 제어 편집기 패널] -----------------
col_main, col_control = st.columns([3.8, 1.2])

with col_control:
    st.markdown("<div style='background-color:#f1f5f9; padding:15px; border-radius:8px; border:1px solid #cbd5e1;'>", unsafe_allow_html=True)
    st.subheader("🎯 실시간 선택 편집기")
    search_q = st.text_input("🔍 컨테이너 실시간 위치 조회", value="")
    
    st.divider()
    
    sel_zone = st.selectbox("🗺️ 제어 구역", ["SD 구역", "SF 구역", "NF 구역", "DOC 구역"])
    z_key = {"SD 구역": "sd_zone", "SF 구역": "sf_zone", "NF 구역": "nf_zone", "DOC 구역": "doc_zone"}[sel_zone]
    
    if z_key in ["sd_zone", "doc_zone"]:
        sel_row = st.selectbox("📏 라인", ["앞라인 (r1)", "뒷라인 (r2)"])
        r_key = "r1" if "앞" in sel_row else "r2"
        lbl_list = SD_LOCS if z_key == "sd_zone" else DOC_LOCS
    else:
        sel_row = st.selectbox("📏 라인", ["짝수 앞 (even_r1)", "짝수 뒤 (even_r2)", "홀수 앞 (odd_r1)", "홀수 뒤 (odd_r2)", "특수 앞 (sp_r1)", "특수 뒤 (sp_r2)"])
        r_key = {"짝수 앞 (even_r1)": "even_r1", "짝수 뒤 (even_r2)": "even_r2", "홀수 앞 (odd_r1)": "odd_r1", "홀수 뒤 (odd_r2)": "odd_r2", "특수 앞 (sp_r1)": "sp_r1", "특수 뒤 (sp_r2)": "sp_r2"}[sel_row]
        lbl_list = SF_EVEN_H if "even" in r_key else (SF_ODD_H if "odd" in r_key else SF_SP_H if z_key == "sf_zone" else NF_ODD_H if "odd" in r_key else NF_EVEN_H)
        
    sel_idx = st.number_input("📍 위치 순번 (Index)", min_value=0, max_value=len(lbl_list)-1, step=1)
    
    current_target = db[z_key][r_key][sel_idx]
    st.markdown(f"**선택된 로케이션:** <code style='color:#2563eb; font-size:14px;'>{lbl_list[sel_idx]}</code>", unsafe_allow_html=True)
    
    edit_no = st.text_input("📦 컨테이너/QC 번호 입력", value=current_target["no"])
    edit_status = st.selectbox("🎨 컨테이너 상태 지정", STATUS_OPTIONS, index=STATUS_OPTIONS.index(current_target["status"]))
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("💾 정보 적용", use_container_width=True):
            db[z_key][r_key][sel_idx] = {"no": edit_no, "status": edit_status}
            t_file = {"sd_zone": "SD.xlsx", "sf_zone": "SF.xlsx", "nf_zone": "NF.xlsx"}.get(z_key)
            if t_file: save_to_local_excel(z_key, t_file)
            st.rerun()
            
    with btn_col2:
        if current_target["no"] and st.button("🗑️ 칸 비우기", use_container_width=True):
            db[z_key][r_key][sel_idx] = {"no": "", "status": "일반"}
            t_file = {"sd_zone": "SD.xlsx", "sf_zone": "SF.xlsx", "nf_zone": "NF.xlsx"}.get(z_key)
            if t_file: save_to_local_excel(z_key, t_file)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- [🎨 격자판 셀 디자인 색상 분류기 함수] -----------------
def determine_class(cell, search_word):
    if not cell["no"]: return "status-normal"
    if search_word and search_word.lower() in str(cell["no"]).lower(): return "status-search"
    return STATUS_CSS_MAP.get(cell["status"], "status-normal")


# ==================== [ 🖥️ 메인 화면 그리드 출력 시스템 ] ====================
with col_main:
    tab_south, tab_north, tab_search = st.tabs(["🔹 남쪽 구역 (South Zone)", "🔸 북쪽 구역 (North Zone)", "검색"])
    
    # ----------------- [ 🔹 남쪽 구역 TAB ] -----------------
with tab_south:
        # 💡 [수정] st.tabs는 아래와 같이 리스트로 생성 후 각각 변수로 받아서 with로 열어야 합니다.
        tab_sd, tab_sf = st.tabs(["SD 구역", "SF 구역"])
        
        # ----------------- [ SD 탭 구역 ] -----------------
        with tab_sd:
            st.markdown('<div class="section-title">🚛 SD 보관 로케이션 라인</div>', unsafe_allow_html=True)
            sd_html = """<table class="vertical-grid-container"><thead><tr class="grid-row">
                        <th class="grid-cell sub-header" style="width:20%;">로케이션 명</th>
                        <th class="grid-cell sub-header" style="width:40%;">앞 (r1)</th>
                        <th class="grid-cell sub-header" style="width:40%;">뒤 (r2)</th></tr></thead><tbody>"""
            
            for i in range(len(SD_LOCS)):
                loc = SD_LOCS[i]
                c1, c2 = db["sd_zone"]["r1"][i], db["sd_zone"]["r2"][i]
                cls1, cls2 = determine_class(c1, search_q), determine_class(c2, search_q)
                st_lbl1 = f'<br><span class="status-lbl">{c1["status"]}</span>' if c1["no"] and c1["status"] != "일반" else ""
                st_lbl2 = f'<br><span class="status-lbl">{c2["status"]}</span>' if c2["no"] and c2["status"] != "일반" else ""
                
                sd_html += '<tr class="grid-row">'
                sd_html += f'<td class="grid-cell cell-header">{loc}</td>'
                if loc in ["NEW WATERPROOF", "OUTPUT STATION"]:
                    sd_html += f'<td colspan="2" class="grid-cell {cls1}">{c1["no"]}{st_lbl1}</td>'
                else:
                    sd_html += f'<td class="grid-cell {cls1}">{c1["no"]}{st_lbl1}</td>'
                    sd_html += f'<td class="grid-cell {cls2}">{c2["no"]}{st_lbl2}</td>'
                sd_html += '</tr>'
            sd_html += "</tbody></table>"
            st.markdown(sd_html, unsafe_allow_html=True)

        # ----------------- [ SF 탭 구역 ] -----------------
        with tab_sf:
            st.markdown('<div class="section-title">🏭 SF 공정 로케이션 라인 (SF01 ~ SF70)</div>', unsafe_allow_html=True)
            sf_html = """<table class="vertical-grid-container"><thead><tr class="grid-row">
                        <th class="grid-cell sub-header" style="width:12%;">SF 짝수 라인</th><th class="grid-cell sub-header" style="width:38%;">QC 넘버 (앞/뒤)</th>
                        <th class="grid-cell sub-header" style="width:12%;">SF 홀수 라인</th><th class="grid-cell sub-header" style="width:38%;">QC 넘버 (앞/뒤)</th></tr></thead><tbody>"""
            
            for i in range(max(len(SF_EVEN_H), len(SF_ODD_H))):
                h_ev = SF_EVEN_H[i] if i < len(SF_EVEN_H) else None
                h_od = SF_ODD_H[i] if i < len(SF_ODD_H) else None
                
                if h_ev in ["SF61","SF62", "SF63", "SF64", "SF65", "SF66", "SF67", "SFE-1", "SFE-2", "SF68", "SF69", "SF70"]:
                    ev1 = db["sf_zone"]["even_r1"][i]
                    cls_ev1 = determine_class(ev1, search_q)
                    lbl_ev1 = f'<br><span class="status-lbl">{ev1["status"]}</span>' if ev1["no"] and ev1["status"] != "일반" else ""
                    
                    sf_html += '<tr class="grid-row">'
                    sf_html += f'<td class="grid-cell cell-header">{h_ev}</td>'
                    if ev1["no"]:
                        sf_html += f'<td colspan="3" class="grid-cell {cls_ev1}" style="padding:0; height:65px;"><div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; width:100%; font-weight:bold;">{ev1["no"]}{lbl_ev1}</div></td>'
                    sf_html += '</tr>'
                    
                else:
                    sf_html += '<tr class="grid-row">'
                    
                    # 짝수 컬럼 (SF61 포함 기존 방식 분할 처리)
                    if h_ev:
                        ev1, ev2 = db["sf_zone"]["even_r1"][i], db["sf_zone"]["even_r2"][i]
                        cls_ev1, cls_ev2 = determine_class(ev1, search_q), determine_class(ev2, search_q)
                        lbl_ev1 = f'<br><span class="status-lbl">{ev1["status"]}</span>' if ev1["no"] and ev1["status"] != "일반" else ""
                        lbl_ev2 = f'<br><span class="status-lbl">{ev2["status"]}</span>' if ev2["no"] and ev2["status"] != "일반" else ""
                        
                        sf_html += f'<td class="grid-cell cell-header">{h_ev}</td>'
                        block_ev = ""
                        if ev1["no"]: block_ev += f'<div class="{cls_ev1}" style="padding:4px; height:32px; display:flex; align-items:center; justify-content:center;">{ev1["no"]}{lbl_ev1}</div>'
                        sf_html += f'<td class="grid-cell" style="padding:0; height:65px; text-align:stretch;">{block_ev}</td>'
                    else:
                        sf_html += '<td class="grid-cell cell-header">-</td><td class="grid-cell" style="color:#cbd5e1;">-</td>'
                    
                    # 홀수 컬럼
                    if h_od:
                        od1, od2 = db["sf_zone"]["odd_r1"][i], db["sf_zone"]["odd_r2"][i]
                        cls_od1, cls_od2 = determine_class(od1, search_q), determine_class(od2, search_q)
                        lbl_od1 = f'<br><span class="status-lbl">{od1["status"]}</span>' if od1["no"] and od1["status"] != "일반" else ""
                        lbl_od2 = f'<br><span class="status-lbl">{od2["status"]}</span>' if od2["no"] and od2["status"] != "일반" else ""
                        
                        sf_html += f'<td class="grid-cell cell-header" style="background-color:#f8fafc;">{h_od}</td>'
                        block_od = ""
                        block_od += f'<div class="{cls_od1}" style="padding:4px; height:32px; display:flex; align-items:center; justify-content:center;">{od1["no"]}{lbl_od1}</div>'
                        sf_html += f'<td class="grid-cell" style="padding:0; height:65px; text-align:stretch;">{block_od}</td>'
                    else:
                        sf_html += '<td class="grid-cell cell-header" style="background-color:#f8fafc;">-</td><td class="grid-cell" style="color:#cbd5e1;">-</td>'
                        
                    sf_html += '</tr>'
            sf_html += "</tbody></table>"
            st.markdown(sf_html, unsafe_allow_html=True)
    
            sf_special_html = """<table class="vertical-grid-container"><thead><tr class="grid-row">
                                <th class="grid-cell sub-header" style="width:20%;">로케이션 명</th>
                                <th class="grid-cell sub-header" style="width:40%;">앞 (r1)</th>
                                <th class="grid-cell sub-header" style="width:40%;">뒤 (r2)</th></tr></thead><tbody>"""
            
            for i, h_sp in enumerate(SF_SP_H):
                sp1, sp2 = db["sf_zone"]["sp_r1"][i], db["sf_zone"]["sp_r2"][i]
                cls_sp1, cls_sp2 = determine_class(sp1, search_q), determine_class(sp2, search_q)
                lbl_sp1 = f'<br><span class="status-lbl">{sp1["status"]}</span>' if sp1["no"] and sp1["status"] != "일반" else ""
                lbl_sp2 = f'<br><span class="status-lbl">{sp2["status"]}</span>' if sp2["no"] and sp2["status"] != "일반" else ""
                
                sf_special_html += f'<tr class="grid-row">'
                sf_special_html += f'<td class="grid-cell cell-header">{h_sp}</td>'
                sf_special_html += f'<td class="grid-cell {cls_sp1}">{sp1["no"]}{lbl_sp1}</td>'
                sf_special_html += f'<td class="grid-cell {cls_sp2}">{sp2["no"]}{lbl_sp2}</td>'
                sf_special_html += '</tr>'
            sf_special_html += "</tbody></table>"
            st.markdown(sf_special_html, unsafe_allow_html=True)


    # ----------------- [ 🔸 북쪽 구역 TAB ] -----------------
with tab_north:
        # 1. NF 북쪽 로케이션 라인
        st.markdown('<div class="section-title">🔸 NF 북쪽 로케이션 라인</div>', unsafe_allow_html=True)
        nf_html = """<table class="vertical-grid-container"><thead><tr class="grid-row">
                     <th class="grid-cell sub-header" style="width:12%;">NF 짝수</th><th class="grid-cell sub-header" style="width:38%;">QC 넘버 (앞/뒤)</th>
                     <th class="grid-cell sub-header" style="width:12%;">NF 홀수</th><th class="grid-cell sub-header" style="width:38%;">QC 넘버 (앞/뒤)</th></tr></thead><tbody>"""
        
        for i in range(len(NF_EVEN_H)):
            nf_html += '<tr class="grid-row">'
            h_ev = NF_EVEN_H[i]
            ev1, ev2 = db["nf_zone"]["even_r1"][i], db["nf_zone"]["even_r2"][i]
            cls_ev1, cls_ev2 = determine_class(ev1, search_q), determine_class(ev2, search_q)
            nf_html += f'<td class="grid-cell cell-header">{h_ev}</td>'
            b_ev = ""
            if ev1["no"]: b_ev += f'<div class="{cls_ev1}" style="padding:2px;">{ev1["no"]} <span class="status-lbl"></span></div>'
            nf_html += f'<td class="grid-cell" style="padding:0; text-align:stretch;">{b_ev}</td>'
            
            h_od = NF_ODD_H[i]
            od1, od2 = db["nf_zone"]["odd_r1"][i], db["nf_zone"]["odd_r2"][i]
            cls_od1, cls_od2 = determine_class(od1, search_q), determine_class(od2, search_q)
            nf_html += f'<td class="grid-cell cell-header" style="background-color:#f8fafc;">{h_od}</td>'
            b_od = ""
            if od1["no"]: b_od += f'<div class="{cls_od1}" style="padding:2px;">{od1["no"]} <span class="status-lbl"></span></div>'
            nf_html += f'<td class="grid-cell" style="padding:0; text-align:stretch;">{b_od}</td>'
            nf_html += '</tr>'
        nf_html += "</tbody></table>"
        st.markdown(nf_html, unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">⚓ DOC 보관 로케이션 라인</div>', unsafe_allow_html=True)
        doc_html = """<table class="vertical-grid-container"><thead><tr class="grid-row">
                     <th class="grid-cell sub-header" style="width:20%;">로케이션 명</th>
                     <th class="grid-cell sub-header" style="width:40%;">앞 (r1)</th>
                     <th class="grid-cell sub-header" style="width:40%;">뒤 (r2)</th></tr></thead><tbody>"""
        
        for i in range(len(DOC_LOCS)):
            loc = DOC_LOCS[i]
            d1, d2 = db["doc_zone"]["r1"][i], db["doc_zone"]["r2"][i]
            cls_d1, cls_d2 = determine_class(d1, search_q), determine_class(d2, search_q)
            lbl_d1 = f'<br><span class="status-lbl">{d1["status"]}</span>' if d1["no"] and d1["status"] != "일반" else ""
            lbl_d2 = f'<br><span class="status-lbl">{d2["status"]}</span>' if d2["no"] and d2["status"] != "일반" else ""
            
            doc_html += '<tr class="grid-row">'
            doc_html += f'<td class="grid-cell cell-header">{loc}</td>'
            doc_html += f'<td class="grid-cell {cls_d1}">{d1["no"]}{lbl_d1}</td>'
            doc_html += f'<td class="grid-cell {cls_d2}">{d2["no"]}{lbl_d2}</td>'
            doc_html += '</tr>'
        doc_html += "</tbody></table>"
        st.markdown(doc_html, unsafe_allow_html=True)
with tab_search:
        st.markdown('<div class="section-title">🔍 컨테이너/QC 넘버 통합 위치 검색</div>', unsafe_allow_html=True)
        
        # 1. 검색어 입력창 (상단 우측 입력창과 별개로 작동하거나 연동 가능)
        search_target = st.text_input("📦 찾으시는 컨테이너 또는 QC 넘버를 입력하세요:", key="tab_search_input", value="")
        
        if search_target.strip():
            # 검색 결과를 담을 리스트
            results = []
            q = search_target.strip().lower()
            
            # --- [SD 구역 검색] ---
            for i, loc in enumerate(SD_LOCS):
                r1_no = str(db["sd_zone"]["r1"][i]["no"])
                r2_no = str(db["sd_zone"]["r2"][i]["no"])
                if q in r1_no.lower():
                    results.append({"구역": "SD 구역", "로케이션": loc, "라인": "앞라인 (r1)", "번호": db["sd_zone"]["r1"][i]["no"], "상태": db["sd_zone"]["r1"][i]["status"]})
                if loc not in ["NEW WATERPROOF", "OUTPUT STATION"]:  # 통하지 않는 단일 칸 제외
                    if q in r2_no.lower():
                        results.append({"구역": "SD 구역", "로케이션": loc, "라인": "뒷라인 (r2)", "번호": db["sd_zone"]["r2"][i]["no"], "상태": db["sd_zone"]["r2"][i]["status"]})
            
            # --- [SF 구역 검색] ---
            # 짝수 라인
            for i, loc in enumerate(SF_EVEN_H):
                if q in str(db["sf_zone"]["even_r1"][i]["no"]).lower():
                    results.append({"구역": "SF 구역", "로케이션": loc, "라인": "짝수 앞 (even_r1)", "번호": db["sf_zone"]["even_r1"][i]["no"], "상태": db["sf_zone"]["even_r1"][i]["status"]})
                # 단일 통합 칸이 아닌 일반 분할 칸인 경우만 뒷라인(r2)도 검색
                if loc not in ["SF62", "SF63", "SF64", "SF65", "SF66", "SF67", "SFE-1", "SFE-2", "SF68", "SF69", "SF70"]:
                    if q in str(db["sf_zone"]["even_r2"][i]["no"]).lower():
                        results.append({"구역": "SF 구역", "로케이션": loc, "라인": "짝수 뒤 (even_r2)", "번호": db["sf_zone"]["even_r2"][i]["no"], "상태": db["sf_zone"]["even_r2"][i]["status"]})
            # 홀수 라인
            for i, loc in enumerate(SF_ODD_H):
                if q in str(db["sf_zone"]["odd_r1"][i]["no"]).lower():
                    results.append({"구역": "SF 구역", "로케이션": loc, "라인": "홀수 앞 (odd_r1)", "번호": db["sf_zone"]["odd_r1"][i]["no"], "상태": db["sf_zone"]["odd_r1"][i]["status"]})
                if q in str(db["sf_zone"]["odd_r2"][i]["no"]).lower():
                    results.append({"구역": "SF 구역", "로케이션": loc, "라인": "홀수 뒤 (odd_r2)", "번호": db["sf_zone"]["odd_r2"][i]["no"], "상태": db["sf_zone"]["odd_r2"][i]["status"]})
            # 특수 라인
            for i, loc in enumerate(SF_SP_H):
                if q in str(db["sf_zone"]["sp_r1"][i]["no"]).lower():
                    results.append({"구역": "SF 구역 (특수)", "로케이션": loc, "라인": "앞 (sp_r1)", "번호": db["sf_zone"]["sp_r1"][i]["no"], "상태": db["sf_zone"]["sp_r1"][i]["status"]})
                if q in str(db["sf_zone"]["sp_r2"][i]["no"]).lower():
                    results.append({"구역": "SF 구역 (특수)", "로케이션": loc, "라인": "뒤 (sp_r2)", "번호": db["sf_zone"]["sp_r2"][i]["no"], "상태": db["sf_zone"]["sp_r2"][i]["status"]})

            # --- [NF 구역 검색] ---
            for i, loc in enumerate(NF_EVEN_H):
                if q in str(db["nf_zone"]["even_r1"][i]["no"]).lower():
                    results.append({"구역": "NF 구역", "로케이션": loc, "라인": "짝수 앞 (even_r1)", "번호": db["nf_zone"]["even_r1"][i]["no"], "상태": db["nf_zone"]["even_r1"][i]["status"]})
                if q in str(db["nf_zone"]["even_r2"][i]["no"]).lower():
                    results.append({"구역": "NF 구역", "로케이션": loc, "라인": "짝수 뒤 (even_r2)", "번호": db["nf_zone"]["even_r2"][i]["no"], "상태": db["nf_zone"]["even_r2"][i]["status"]})
            for i, loc in enumerate(NF_ODD_H):
                if q in str(db["nf_zone"]["odd_r1"][i]["no"]).lower():
                    results.append({"구역": "NF 구역", "로케이션": loc, "라인": "홀수 앞 (odd_r1)", "번호": db["nf_zone"]["odd_r1"][i]["no"], "상태": db["nf_zone"]["odd_r1"][i]["status"]})
                if q in str(db["nf_zone"]["odd_r2"][i]["no"]).lower():
                    results.append({"구역": "NF 구역", "로케이션": loc, "라인": "홀수 뒤 (odd_r2)", "번호": db["nf_zone"]["odd_r2"][i]["no"], "상태": db["nf_zone"]["odd_r2"][i]["status"]})

            # --- [DOC 구역 검색] ---
            for i, loc in enumerate(DOC_LOCS):
                if q in str(db["doc_zone"]["r1"][i]["no"]).lower():
                    results.append({"구역": "DOC 구역", "로케이션": loc, "라인": "앞 (r1)", "번호": db["doc_zone"]["r1"][i]["no"], "상태": db["doc_zone"]["r1"][i]["status"]})
                if q in str(db["doc_zone"]["r2"][i]["no"]).lower():
                    results.append({"구역": "DOC 구역", "로케이션": loc, "라인": "뒤 (r2)", "번호": db["doc_zone"]["r2"][i]["no"], "상태": db["doc_zone"]["r2"][i]["status"]})

            # 📊 결과 출력 화면 구성
            if results:
                st.success(f"🎯 총 {len(results)}개의 일치하는 위치를 찾았습니다!")
                
                # HTML 테이블 생성
                search_html = """<table class="vertical-grid-container"><thead><tr class="grid-row">
                                 <th class="grid-cell sub-header" style="width:20%;">로케이션 명</th>
                                 <th class="grid-cell sub-header" style="width:25%;">세부 라인</th>
                                 <th class="grid-cell sub-header" style="width:20%;">QC / 컨테이너 번호</th>
                                 <th class="grid-cell sub-header" style="width:15%;">현재 상태</th></tr></thead><tbody>"""
                
                for res in results:
                    # 기존에 정의된 STATUS_CSS_MAP을 활용해 검색창 내부에서도 색상 연동
                    cls_status = STATUS_CSS_MAP.get(res["상태"], "status-normal")
                    
                    search_html += '<tr class="grid-row">'
                    search_html += f'<td class="grid-cell" style="font-weight:bold;">{res["로케이션"]}</td>'
                    search_html += f'<td class="grid-cell" style="color:#475569;">{res["라인"]}</td>'
                    search_html += f'<td class="grid-cell status-search">{res["번호"]}</td>' # 찾은 번호는 노란색 강조 테두리 적용
                    search_html += f'<td class="grid-cell {cls_status}">{res["상태"]}</td>'
                    search_html += '</tr>'
                    
                search_html += "</tbody></table>"
                st.markdown(search_html, unsafe_allow_html=True)
            else:
                st.warning("⚠️ 입력하신 번호와 일치하는 컨테이너가 현재 어느 구역에도 보관되어 있지 않습니다.")
        else:
            st.info("💡 실시간 위치를 조회하려면 조회창에 검색어를 입력해 주세요. (글자 일부만 입력해도 매칭됩니다.)")


# ----------------- [🎨 하단 가이드 범례 창] -----------------
st.markdown("""
---
**💡 가이드 컬러 맵 시스템 안내**
* <span style='background-color:#fff200; border:1px solid #000; padding:3px 8px; border-radius:4px; font-weight:bold; color:#000;'>출하 (노란색)</span> : 특정 장소 이동 대기 건 | <span style='background-color:#16a34a; padding:3px 8px; border-radius:4px; font-weight:bold; color:#fff;'>직출하 (초록색)</span> : 고객사 직송 이동 건
* <span style='background-color:#2563eb; padding:3px 8px; border-radius:4px; font-weight:bold; color:#fff;'>수밀존 (파란색)</span> : 수밀 테스트 필요 건 | <span style='background-color:#dc2626; padding:3px 8px; border-radius:4px; font-weight:bold; color:#fff;'>수리필요 (빨간색)</span> : 파손 및 정비 대상
* <span style='background-color:#ea580c; padding:3px 8px; border-radius:4px; font-weight:bold; color:#fff;'>쉽백 복귀 (주황색)</span> : 공장 복귀 자재 | <span style='background: linear-gradient(135deg, #cbd5e1 25%, #94a3b8 25%, #94a3b8 50%, #cbd5e1 50%, #cbd5e1 75%, #94a3b8 75%, #94a3b8 100%); background-size:8px 8px; padding:3px 8px; border-radius:4px; font-weight:bold; color:#0f172a;'>배터리 교체 대상 (사선 채움)</span>
""", unsafe_allow_html=True)