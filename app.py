import streamlit as st
import pandas as pd

# 1. 페이지 전체 화면 설정
st.set_page_config(page_title="컨테이너 위치 관제 시스템", layout="wide", page_icon="📦")

# 2. 하이브리드 그리드(2칸/4칸)를 위한 CSS 스타일 정의
st.markdown("""
    <style>
    .vertical-grid-container {
        display: table;
        border-collapse: collapse;
        margin: 15px 0;
        font-family: 'Segoe UI', sans-serif;
        width: 100%;
        max-width: 650px; /* 4칸으로 확장됨에 따라 전체 최대 너비 소폭 확장 */
    }
    .grid-row {
        display: table-row;
    }
    .grid-cell {
        display: table-cell;
        border: 1px solid #777777;
        padding: 10px;
        text-align: center;
        height: 45px;
        vertical-align: middle;
        font-size: 13px;
        font-weight: 500;
        background-color: #ffffff;
    }
    .cell-header {
        background-color: #eef1f6;
        font-weight: bold;
        color: #1e293b;
    }
    .sub-header {
        background-color: #f8fafc;
        font-size: 11px;
        color: #64748b;
        font-weight: bold;
        border-bottom: 2px solid #cbd5e1;
    }
    /* 색상 테마 정의 */
    .pink-bg { background-color: #e8a7d7 !important; }
    .green-bg { background-color: #c2eed1 !important; }
    .yellow-bg { background-color: #fff200 !important; font-weight: bold; }
    .red-bg { background-color: #ff3333 !important; color: white; font-weight: bold; }
    
    .main-title {
        font-size: 24px;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 5px;
    }
    .section-title {
        font-size: 16px;
        font-weight: bold;
        color: #334155;
        margin-top: 20px;
        margin-bottom: 10px;
        border-left: 4px solid #3b82f6;
        padding-left: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📦 컨테이너 위치 관제 시스템 (하이브리드 뷰)</div>', unsafe_allow_html=True)
st.caption("SD(기존 틀) 유지 및 SF/NF 구역 4칸 분할(짝수/홀수 나란히 배치) 적용 버전")

# ----------------- [사이드바 컨트롤] -----------------
st.sidebar.header("⚙️ 관제 컨트롤 패널")
file_upload = st.sidebar.file_uploader("엑셀 데이터베이스 파일 업로드 (.xlsx)", type=["xlsx"])
search_q = st.sidebar.text_input("🔍 컨테이너 번호 동적 검색")

if file_upload:
    st.sidebar.success("✅ 파일 로드 완료")

# ----------------- [렌더링 함수 1: SD 전용 (기존 2칸 구조)] -----------------
def render_sd_grid(headers, row1, row2, pink_elements=None):
    pink_set = set(pink_elements or [])
    html = '<div class="vertical-grid-container">'
    
    html += '<div class="grid-row">'
    html += '<div class="grid-cell sub-header" style="width:20%;">로케이션 명</div>'
    html += '<div class="grid-cell sub-header" style="width:40%;">적재 위치 1</div>'
    html += '<div class="grid-cell sub-header" style="width:40%;">적재 위치 2</div>'
    html += '</div>'
    
    for i in range(len(headers)):
        h_val, v1, v2 = headers[i], row1[i], row2[i]
        html += '<div class="grid-row">'
        html += f'<div class="grid-cell cell-header">{h_val}</div>'
        
        for v in [v1, v2]:
            bg = "pink-bg" if v in pink_set else ""
            if search_q and search_q == str(v): bg = "yellow-bg"
            html += f'<div class="grid-cell {bg}">{v}</div>'
        html += '</div>'
        
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ----------------- [렌더링 함수 2: SF/NF 전용 (요청하신 4칸 구조)] -----------------
def render_4part_grid(zone_prefix, pairs_count, even_data, odd_data, pink_elements=None):
    """
    zone_prefix: 'SF' 또는 'NF'
    pairs_count: 행의 총 개수
    even_data: (짝수번호 리스트, 적재1 리스트, 적재2 리스트)
    odd_data: (홀수번호 리스트, 적재1 리스트, 적재2 리스트)
    """
    pink_set = set(pink_elements or [])
    
    even_headers, even_r1, even_r2 = even_data
    odd_headers, odd_r1, odd_r2 = odd_data
    
    html = '<div class="vertical-grid-container">'
    
    # 최상단 열 헤더 레이아웃 (총 4칸 구성)
    html += '<div class="grid-row">'
    html += f'<div class="grid-cell sub-header" style="width:25%; background-color:#e2e8f0;">{zone_prefix} 짝수 라인</div>'
    html += '<div class="grid-cell sub-header" style="width:25%; background-color:#e2e8f0;">QC 넘버</div>'
    html += f'<div class="grid-cell sub-header" style="width:25%; background-color:#f1f5f9;">{zone_prefix} 홀수 라인</div>'
    html += '<div class="grid-cell sub-header" style="width:25%; background-color:#f1f5f9;">QC 넘버</div>'
    html += '</div>'
    
    # 세로 행(Row) 생성 루프
    for i in range(pairs_count):
        html += '<div class="grid-row">'
        
        # --------------------------------------------
        # [1-2칸]: 짝수 영역 처리 (인덱스 범위 안전 검사 추가)
        # --------------------------------------------
        if i < len(even_headers):
            html += f'<div class="grid-cell cell-header">{even_headers[i]}</div>'
            
            # 리스트 범위를 벗어나지 않도록 방어 코드(IndexError 방지)
            v1 = even_r1[i] if i < len(even_r1) else ""
            v2 = even_r2[i] if i < len(even_r2) else ""
            
            ev_val = f"{v1}<br>{v2}" if v2 else f"{v1}"
            bg_ev = "pink-bg" if (v1 in pink_set or v2 in pink_set) else ""
            if "Water" in str(v1): bg_ev = "red-bg"
            if search_q and (search_q == str(v1) or search_q == str(v2)): bg_ev = "yellow-bg"
            html += f'<div class="grid-cell {bg_ev}">{ev_val}</div>'
        else:
            html += '<div class="grid-cell" style="background-color:#f8fafc;"></div><div class="grid-cell"></div>'
            
        # --------------------------------------------
        # [3-4칸]: 홀수 영역 처리 (인덱스 범위 안전 검사 추가)
        # --------------------------------------------
        if i < len(odd_headers):
            html += f'<div class="grid-cell cell-header" style="background-color:#f8fafc;">{odd_headers[i]}</div>'
            
            # 리스트 범위를 벗어나지 않도록 방어 코드(IndexError 방지)
            v1_od = odd_r1[i] if i < len(odd_r1) else ""
            v2_od = odd_r2[i] if i < len(odd_r2) else ""
            
            od_val = f"{v1_od}<br>{v2_od}" if v2_od else f"{v1_od}"
            bg_od = "pink-bg" if (v1_od in pink_set or v2_od in pink_set) else ""
            if search_q and (search_q == str(v1_od) or search_q == str(v2_od)): bg_od = "yellow-bg"
            html += f'<div class="grid-cell {bg_od}">{od_val}</div>'
        else:
            html += '<div class="grid-cell" style="background-color:#f8fafc;"></div><div class="grid-cell"></div>'
            
        html += '</div>'
        
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ----------------- [샘플 및 가공 데이터 정의] -----------------
# 1. SD 데이터 (기존 유지)
sd_locs = ['SD-3', 'SD-2', 'SD-1', 'SD1', 'SD2', 'SD3', 'SD4', 'SD5', 'SD6', 'SDE-1', 'SD7', 'SD8', 'SD9', 'SD10', 'SD11', 'SD12', 'SD13', 'SD14', 'SD15', 'SDE-2', 'SD16', 'SD17', 'SD18', 'SD19', 'NEW WATERPROOF', 'SDE-3', 'SDX3', 'SDX2', 'SDX1']
sd_r1 = ['', '', '', '2310', '', '1491', '2245', '1832', '2334', '2315', '2238', '', '2336', '11006_1A', '2318', '2313', '2335', '2301', '2263', '2242', '2232', '2345', '2307', '2347', '2218', '2230', '2316', '2350', '2302']
sd_r2 = ['', '', '', '', '2118', '1776', '2191', '14201_1H', '2211', '2312', '', '2223', '905', '2185', '2198', '2268', '1771', '2123', '2304', '', '2233', '2189', '1772', '2298', '', '2299', '2314', '81201_1W', '']

# 2. SF 구역 데이터 쪼개기 (짝수 / 홀수 분리 가공)
sf_even_h = [f"SF{i}" for i in range(2, 71, 2)] + ['SF71']+ ['SF72']+ ['SF73']+ ['SF74']
# 샘플 데이터 (74번부터 시작하므로 앞부분은 빈칸 처리되도록 구성하거나 순서에 맞춤)
sf_even_r1 = ["Water", "1888", "1855", "1955", "1918", "1882", "1920", "1841", "888", "1004_1", "1538", "1954"] + [""] * 30
sf_even_r2 = ["", "1859", "1003_1", "344", "1478", "1937"] + [""] * 35

# range(73, 0, -2)는 73, 71, 69 ... 1 까지 생성합니다.
sf_odd_h = [f"SF{i}" for i in range(1,70, 2)] + ['-']+ ['-']+ ['-']+ ['-']
sf_odd_r1 = ["1948", "1863", "1883", "1825", "1932", "1935", "1952", "1593", "1947", "1917", "1862"] + [""] * 30
sf_odd_r2 = ["", "1002_1", "1675", "", "1785"] + [""] * 35

# 3. NF 구역 데이터 쪼개기 (짝수 / 홀수 분리 가공)
nf_even_h = [f"NF{i}" for i in range(2, 69, 2)]
nf_even_r1 = ["5120", "5122", "5124", "5126", "5127", "5129", "5131", "5133", "5135", "5137", "5139", "5141", ""]
nf_even_r2 = ["", "4122", "4124", "", "4127", "4129", "4131", "4133", "", "", "", "", ""]

nf_odd_h = [f"NF{i}" for i in range(1, 70, 2)]
nf_odd_r1 = ["5121", "5123", "5125", "5128", "5130", "5132", "5134", "5136", "5138", "5140", "", "", ""]
nf_odd_r2 = ["4120", "4123", "4125", "4128", "4130", "4132", "4133", "", "", "", "", "", ""]


# ----------------- [메인 화면 탭 구성] -----------------
main_tab1, main_tab2 = st.tabs(["🔹 남쪽 (South Zone)", "🔸 북쪽 (North Zone)"])

# ==========================================
# 1. 남쪽 구역 (SD, SF)
# ==========================================
with main_tab1:
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📊 전체 레이아웃", "🚛 SD 구역", "🏭 SF 구역"])
    
    with sub_tab1:
        st.markdown('<div class="section-title">🚛 SD 보관 로케이션 라인 (기존 2칸 구조)</div>', unsafe_allow_html=True)
        render_sd_grid(sd_locs, sd_r1, sd_r2, pink_elements=['1491', '2307'])
        
        st.markdown('<div class="section-title">🏭 SF 공정 로케이션 라인 (4칸 분할 세로형 구조)</div>', unsafe_allow_html=True)
        render_4part_grid('SF', max(len(sf_even_h), len(sf_odd_h)), 
                          (sf_even_h, sf_even_r1, sf_even_r2), 
                          (sf_odd_h, sf_odd_r1, sf_odd_r2), 
                          pink_elements=['1855', '1920'])

    with sub_tab2:
        st.markdown('<div class="section-title">🚛 SD 보관 구역 단독 모니터링</div>', unsafe_allow_html=True)
        render_sd_grid(sd_locs, sd_r1, sd_r2, pink_elements=['1491', '2307'])

    with sub_tab3:
        st.markdown('<div class="section-title">🏭 SF 공정 구역 단독 모니터링 (4칸 분할 구조)</div>', unsafe_allow_html=True)
        render_4part_grid('SF', max(len(sf_even_h), len(sf_odd_h)), 
                          (sf_even_h, sf_even_r1, sf_even_r2), 
                          (sf_odd_h, sf_odd_r1, sf_odd_r2), 
                          pink_elements=['1855', '1920'])

# ==========================================
# 2. 북쪽 구역 (NF)
# ==========================================
with main_tab2:
    st.markdown('<div class="section-title">🔸 NF 북쪽 로케이션 라인 (4칸 분할 세로형 구조)</div>', unsafe_allow_html=True)
    render_4part_grid('NF', max(len(nf_even_h), len(nf_odd_h)), 
                      (nf_even_h, nf_even_r1, nf_even_r2), 
                      (nf_odd_h, nf_odd_r1, nf_odd_r2), 
                      pink_elements=['5123', '4125'])

# ----------------- [동적 검색 처리 피드백] -----------------
if search_q:
    st.sidebar.success(f"🎯 '{search_q}' 번호 위치를 노란색으로 반전 표시 중입니다.")
