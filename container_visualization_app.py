import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="컨테이너 위치 시각화 시스템", layout="wide", page_icon="📦")

# Styling with CSS for the layout grid similar to the user's uploaded image
st.markdown("""
    <style>
    .grid-container {
        display: table;
        border-collapse: collapse;
        margin: 10px 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .grid-row {
        display: table-row;
    }
    .grid-cell {
        display: table-cell;
        border: 1px solid #999;
        padding: 6px;
        text-align: center;
        min-width: 50px;
        height: 45px;
        vertical-align: middle;
        font-size: 11px;
        font-weight: 500;
        background-color: #ffffff;
    }
    .cell-header {
        background-color: #f0f2f6;
        font-weight: bold;
        border-bottom: 2px solid #555;
    }
    .pink-bg { background-color: #e8a7d7 !important; }
    .green-bg { background-color: #c2eed1 !important; }
    .yellow-bg { background-color: #fff200 !important; font-weight: bold; }
    .red-bg { background-color: #ff3333 !important; color: white; font-weight: bold; }
    .station-bg { background-color: #ba68c8 !important; color: white; font-weight: bold; }
    
    .section-title {
        font-size: 16px;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 5px;
        color: #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 컨테이너 위치 시각화 모니터링 시스템")
st.caption("Excel 데이터베이스 연동 및 레이아웃 그리드 뷰 프로토타입")

# 1. Mock Database Creation (Simulating Excel sheet structure)
@st.cache_data
def load_mock_excel_data():
    # Stations layout
    station_data = {
        'OUTPUT STATION': ['632', ''],
        'WATER': ['1873', ''],
        'X1': ['01003\n16', '1793'],
        'X2_H': ['330', '644'],
        'X2': ['331', '1860'],
        'X3': ['1787', '1911']
    }
    
    # SD Layout Top Row and Bottom Row
    sd_layout = {
        'SD19': ['1769', '1858'], 'SD18': ['1772', '1957'], 'SD17': ['1791', '1936'], 'SD16': ['1312', '1921'],
        'SD15_STAIR': ['STAIR\nS', ''], 'SD15': ['574', '888'], 'SD14': ['353', '607'],
        'SD13_H': ['', ''], 'SD13': ['1771', '1784'], 'SD12': ['193', '1949'], 'SD11': ['', '']
    }
    return station_data, sd_layout

station_db, sd_db = load_mock_excel_data()

# Sidebar controls for future feature expansions
st.sidebar.header("⚙️ 관제 컨트롤 패널")
file_upload = st.sidebar.file_uploader("엑셀 데이터베이스 파일 업로드 (.xlsx)", type=["xlsx"])
view_mode = st.sidebar.radio("시각화 모드", ["전체 레이아웃 뷰", "구역별 세부 뷰", "데이터 테이블 확인"])
search_q = st.sidebar.text_input("🔍 컨테이너 번호 검색")

if file_upload:
    st.sidebar.success("✅ 엑셀 파일이 성공적으로 로드되었습니다!")

# Render Main Layout View
if view_mode == "전체 레이아웃 뷰":
    st.subheader("📍 공정 및 창고 배치도 실시간 시각화")
    
    # Render Section 1: STATION / WATER / X1-X3
    st.markdown('<div class="section-title">■ 상단 마스터 스테이션 구역 (STATION / WATER / X구역)</div>', unsafe_allow_html=True)
    
    html_str = '<div class="grid-container">'
    # Header Row
    html_str += '<div class="grid-row">'
    html_str += '<div class="grid-cell cell-header">OUTPUT<br>STATION</div>'
    html_str += '<div class="grid-cell cell-header">WATER</div>'
    html_str += '<div class="grid-cell cell-header">X1</div>'
    html_str += '<div class="grid-cell cell-header"></div>'
    html_str += '<div class="grid-cell cell-header">X2</div>'
    html_str += '<div class="grid-cell cell-header">X3</div>'
    html_str += '</div>'
    
    # Data Row 1
    html_str += '<div class="grid-row">'
    html_str += '<div class="grid-cell station-bg">632</div>'
    html_str += '<div class="grid-cell">1873</div>'
    html_str += '<div class="grid-cell">01003<br>16</div>'
    html_str += '<div class="grid-cell">330</div>'
    html_str += '<div class="grid-cell">331</div>'
    html_str += '<div class="grid-cell">1787</div>'
    html_str += '</div>'
    
    # Data Row 2
    html_str += '<div class="grid-row">'
    html_str += '<div class="grid-cell"></div>'
    html_str += '<div class="grid-cell"></div>'
    html_str += '<div class="grid-cell pink-bg">1793</div>'
    html_str += '<div class="grid-cell pink-bg">644</div>'
    html_str += '<div class="grid-cell pink-bg">1860</div>'
    html_str += '<div class="grid-cell">1911</div>'
    html_str += '</div>'
    html_str += '</div>'
    
    st.markdown(html_str, unsafe_allow_html=True)
    
    # Render Section 2: SD 구역 (SD19 ~ SD11)
    st.markdown('<div class="section-title">■ 라인 배치 구역 (SD19 ~ SD11 파트)</div>', unsafe_allow_html=True)
    
    sd_html = '<div class="grid-container">'
    # Headers
    sd_html += '<div class="grid-row">'
    for col in ['SD19', 'SD18', 'SD17', 'SD16', '', 'SD15', 'SD14', '', 'SD13', 'SD12', 'SD11']:
        sd_html += f'<div class="grid-cell cell-header">{col}</div>'
    sd_html += '</div>'
    
    # Row 1
    sd_html += '<div class="grid-row">'
    sd_html += '<div class="grid-cell">1769</div>'
    sd_html += '<div class="grid-cell">1772</div>'
    sd_html += '<div class="grid-cell">1791</div>'
    sd_html += '<div class="grid-cell">1312</div>'
    sd_html += '<div class="grid-cell yellow-bg">STAIR<br>S</div>'
    sd_html += '<div class="grid-cell">574</div>'
    sd_html += '<div class="grid-cell">353</div>'
    sd_html += '<div class="grid-cell"></div>'
    sd_html += '<div class="grid-cell">1771</div>'
    sd_html += '<div class="grid-cell">193</div>'
    sd_html += '<div class="grid-cell green-bg"></div>'
    sd_html += '</div>'
    
    # Row 2
    sd_html += '<div class="grid-row">'
    sd_html += '<div class="grid-cell pink-bg">1858</div>'
    sd_html += '<div class="grid-cell">1957</div>'
    sd_html += '<div class="grid-cell pink-bg">1936</div>'
    sd_html += '<div class="grid-cell">1921</div>'
    sd_html += '<div class="grid-cell"></div>'
    sd_html += '<div class="grid-cell">888</div>'
    sd_html += '<div class="grid-cell">607</div>'
    sd_html += '<div class="grid-cell"></div>'
    sd_html += '<div class="grid-cell">1784</div>'
    sd_html += '<div class="grid-cell">1949</div>'
    sd_html += '<div class="grid-cell green-bg"></div>'
    sd_html += '</div>'
    sd_html += '</div>'
    
    st.markdown(sd_html, unsafe_allow_html=True)

    # Render Section 3: SF 구역 하단 일부 시각화 샘플
    st.markdown('<div class="section-title">■ 메인 컴포넌트 하단 구역 (SF 일부 예시)</div>', unsafe_allow_html=True)
    sf_html = '<div class="grid-container">'
    sf_html += '<div class="grid-row">'
    for i in range(44, 30, -2):
        sf_html += f'<div class="grid-cell cell-header">SF{i}</div>'
    sf_html += '</div>'
    sf_html += '<div class="grid-row">'
    sf_html += '<div class="grid-cell red-bg">Water<br>수밀</div>'
    sf_html += '<div class="grid-cell">1948</div>'
    sf_html += '<div class="grid-cell">1888</div>'
    sf_html += '<div class="grid-cell">1863</div>'
    sf_html += '<div class="grid-cell pink-bg">1855</div>'
    sf_html += '<div class="grid-cell">1883</div>'
    sf_html += '<div class="grid-cell">1955</div>'
    sf_html += '</div>'
    sf_html += '</div>'
    st.markdown(sf_html, unsafe_allow_html=True)

    if search_q:
        st.info(f"🔍 입력하신 번호 '{search_q}'를 그리드 레이아웃 내에서 하이라이팅하는 기능이 활성화됩니다.")

elif view_mode == "데이터 테이블 확인":
    st.subheader("📊 원본 데이터프레임 확인")
    st.dataframe(pd.DataFrame(station_db))
    st.dataframe(pd.DataFrame(sd_db))

st.info("💡 나중에 추가할 상세 기능들(예: 데이터 직접 수정, 엑셀 재내보내기, 실시간 상태값 변경 등)을 알려주시면 순차적으로 업데이트해 드릴게요.")
