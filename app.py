import streamlit as st
import pandas as pd
import json
import os
import requests


# 1. 페이지 전체 화면 설정
st.set_page_config(page_title="컨테이너 위치 관제 시스템", layout="wide", page_icon="📦")

# 2. 하이브리드 그리드 스타일 정의 (반응형 글자 크기 적용)
st.markdown("""
    <style>
    .vertical-grid-container {
        display: table;
        border-collapse: collapse;
        margin: 15px 0;
        font-family: 'Segoe UI', sans-serif;
        width: 100%;
        max-width: 100%; /* 화면 크기에 맞게 100% 채우기 */
        table-layout: fixed;
    }
    .grid-row { display: table-row; }
    .grid-cell {
        display: table-cell;
        border: 1px solid #777777;
        padding: 4px 6px;
        text-align: center;
        height: 55px; 
        min-height: 55px;
        max-height: 55px;
        box-sizing: border-box;
        vertical-align: middle;
        /* 핵심: 화면 크기에 따라 최소 10px ~ 최대 14px 사이로 글자 크기 자동 조절 */
        font-size: clamp(10px, 1.1vw, 14px); 
        font-weight: 500;
        background-color: #ffffff;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: normal; 
        word-break: break-all; /* 영문/숫자가 길어도 자르고 줄바꿈 */
    }
    .cell-header {
        background-color: #eef1f6;
        font-weight: bold;
        color: #1e293b;
        font-size: clamp(9px, 1vw, 13px);
    }
    .sub-header {
        background-color: #f8fafc;
        font-size: clamp(9px, 0.9vw, 12px);
        color: #64748b;
        font-weight: bold;
        border-bottom: 2px solid #cbd5e1;
        height: 35px;
    }
    .yellow-bg { background-color: #fff200 !important; font-weight: bold; }
    .main-title { font-size: 24px; font-weight: bold; color: #1e293b; margin-bottom: 5px; }
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
st.caption("틀 고정(소스코드) / 데이터 동적 분리(JSON) 하이브리드 버전")

# ----------------- [사이드바 컨트롤] -----------------
st.sidebar.header("⚙️ 관제 컨트롤 패널")
file_upload = st.sidebar.file_uploader("엑셀 데이터베이스 파일 업로드 (.xlsx)", type=["xlsx"])
search_q = st.sidebar.text_input("🔍 컨테이너 번호 동적 검색")

if file_upload:
    st.sidebar.success("✅ 파일 로드 완료")


# ----------------- [📌 절대로 안 바뀌는 구역/틀 고정 데이터] -----------------
SD_LOCS = ['SD-3', 'SD-2', 'SD-1', 'SD1', 'SD2', 'SD3', 'SD4', 'SD5', 'SD6', 'SDE-1', 'SD7', 'SD8', 'SD9', 'SD10', 'SD11', 'SD12', 'SD13', 'SD14', 'SD15', 'SDE-2', 'SD16', 'SD17', 'SD18', 'SD19', 'NEW WATERPROOF', 'OUTPUT STATION', 'SDE-3', 'SDX3', 'SDX2', 'SDX1']

SF_EVEN_H = [f"SF{i}" for i in range(2, 71, 2)] + ['SF71', 'SF72', 'SF73', 'SF74']
SF_ODD_H = [f"SF{i}" for i in range(1, 70, 2)] + ['-', '-', '-', '-']

NF_EVEN_H = [f"NF{i}" for i in range(2, 69, 2)]
NF_ODD_H = [f"NF{i}" for i in range(1, 69, 2)]

DOC_LOCS = ['DOC1', 'DOC2']


# ----------------- [백엔드 데이터 로드 로직] -----------------
def fetch_data_from_backend():
    url = "https://twiddle-refract-editor.ngrok-free.dev/api/containers"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        st.error("🚨 백엔드 서버(loaddata.py)가 꺼져 있습니다! uvicorn 명령어로 서버를 켜주세요.")
        
    return {
        "sd_zone": {"r1": [""]*len(SD_LOCS), "r2": [""]*len(SD_LOCS)},
        "sf_zone": {"even_r1": [""]*len(SF_EVEN_H), "even_r2": [""]*len(SF_EVEN_H), "odd_r1": [""]*len(SF_ODD_H), "odd_r2": [""]*len(SF_ODD_H)},
        "nf_zone": {"even_r1": [""]*len(NF_EVEN_H), "even_r2": [""]*len(NF_EVEN_H), "odd_r1": [""]*len(NF_ODD_H), "odd_r2": [""]*len(NF_ODD_H)},
        "doc_zone": {"r1": [""]*len(DOC_LOCS), "r2": [""]*len(DOC_LOCS)}
    }

db = fetch_data_from_backend()


# ----------------- [렌더링 함수 1: SD 및 DOC 전용 (2칸 구조)] -----------------
def render_sd_grid(headers, row1, row2):
    html = """
    <table class="vertical-grid-container">
        <thead>
            <tr class="grid-row">
                <th class="grid-cell sub-header" style="width:20%;">로케이션 명</th>
                <th class="grid-cell sub-header" style="width:40%;">앞</th>
                <th class="grid-cell sub-header" style="width:40%;">뒤</th>
            </tr>
        </thead>
        <tbody>
    """
    cell_style = "border: 1px solid #777; text-align: center; height: 55px; box-sizing: border-box; vertical-align: middle; font-size: clamp(10px, 1.1vw, 14px); font-weight: 500; background-color: #ffffff; overflow: hidden; text-overflow: ellipsis; white-space: normal; word-break: break-all;"
    header_style = "background-color: #eef1f6; font-weight: bold; color: #1e293b; border: 1px solid #777; text-align: center; height: 55px; vertical-align: middle; font-size: clamp(9px, 1vw, 13px);"

    for i in range(len(headers)):
        h_val = headers[i]
        v1 = row1[i] if i < len(row1) else ""
        v2 = row2[i] if i < len(row2) else ""
        
        html += '<tr class="grid-row">'
        
        if h_val in ["NEW WATERPROOF", "OUTPUT STATION"]:
            h_font_style = "font-size: clamp(8px, 0.8vw, 11px); line-height: 1.2; padding: 2px;"
        else:
            h_font_style = ""
            
        html += f'<td style="{header_style} {h_font_style}">{h_val}</td>'
        
        if h_val in ["NEW WATERPROOF", "OUTPUT STATION"]:
            bg = "background-color: #fff200 !important; font-weight: bold;" if search_q and search_q == str(v1) else ""
            html += f'<td colspan="2" style="{cell_style} {bg}">{v1}</td>'
        else:
            bg1 = "background-color: #fff200 !important; font-weight: bold;" if search_q and search_q == str(v1) else ""
            bg2 = "background-color: #fff200 !important; font-weight: bold;" if search_q and search_q == str(v2) else ""
            html += f'<td style="{cell_style} {bg1}">{v1}</td>'
            html += f'<td style="{cell_style} {bg2}">{v2}</td>'
            
        html += '</tr>'
        
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)


# ----------------- [렌더링 함수 2: SF/NF 전용 (4칸 구조)] -----------------
def render_4part_grid(zone_prefix, pairs_count, even_headers, odd_headers, even_r1, even_r2, odd_r1, odd_r2):
    html = """
    <table class="vertical-grid-container">
        <thead>
            <tr class="grid-row">
                <th class="grid-cell sub-header" style="width:16%; background-color:#e2e8f0; color: #1e293b;">{0} 짝수</th>
                <th class="grid-cell sub-header" style="width:34%; background-color:#e2e8f0; color: #1e293b;">QC 넘버</th>
                <th class="grid-cell sub-header" style="width:16%; background-color:#f1f5f9; color: #1e293b;">{0} 홀수</th>
                <th class="grid-cell sub-header" style="width:34%; background-color:#f1f5f9; color: #1e293b;">QC 넘버</th>
            </tr>
        </thead>
        <tbody>
    """.format(zone_prefix)
    
    cell_style = "border: 1px solid #777; text-align: center; height: 55px; box-sizing: border-box; vertical-align: middle; font-size: clamp(10px, 1.1vw, 14px); font-weight: 500; background-color: #ffffff; overflow: hidden; text-overflow: ellipsis; white-space: normal; word-break: break-all;"
    header_style = "background-color: #eef1f6; font-weight: bold; color: #1e293b; border: 1px solid #777; text-align: center; height: 55px; vertical-align: middle; font-size: clamp(9px, 1vw, 13px);"
    odd_header_style = "background-color: #f8fafc; font-weight: bold; color: #1e293b; border: 1px solid #777; text-align: center; height: 55px; vertical-align: middle; font-size: clamp(9px, 1vw, 13px);"

    for i in range(pairs_count):
        html += '<tr class="grid-row">'
        
        # 1. 짝수 라인
        if i < len(even_headers):
            html += f'<td style="{header_style}">{even_headers[i]}</td>'
            v1 = even_r1[i] if i < len(even_r1) else ""
            v2 = even_r2[i] if i < len(even_r2) else ""
            ev_val = f"{v1}<br>{v2}" if v2 else f"{v1}"
            bg_ev = "background-color: #fff200 !important; font-weight: bold;" if search_q and (search_q == str(v1) or search_q == str(v2)) else ""
            html += f'<td style="{cell_style} {bg_ev}">{ev_val}</td>'
        else:
            html += f'<td style="{header_style} background-color:#f8fafc;"></td><td style="{cell_style}"></td>'
            
        # 2. 홀수 라인
        if i < len(odd_headers):
            odd_h_val = odd_headers[i]
            if odd_h_val in ["-", "NEW WATERPROOF"]:
                html += f'<td colspan="2" style="{cell_style} color: #cbd5e1;"></td>'
            else:
                html += f'<td style="{odd_header_style}">{odd_h_val}</td>'
                v1_od = odd_r1[i] if i < len(odd_r1) else ""
                v2_od = odd_r2[i] if i < len(odd_r2) else ""
                od_val = f"{v1_od}<br>{v2_od}" if v2_od else f"{v1_od}"
                bg_od = "background-color: #fff200 !important; font-weight: bold;" if search_q and (search_q == str(v1_od) or search_q == str(v2_od)) else ""
                html += f'<td style="{cell_style} {bg_od}">{od_val}</td>'
        else:
            html += f'<td style="{odd_header_style}"></td><td style="{cell_style}"></td>'
            
        html += '</tr>'
        
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)


# ----------------- [메인 화면 탭 구성] -----------------
main_tab1, main_tab2 = st.tabs(["🔹 남쪽 (South Zone)", "🔸 북쪽 (North Zone)"])

with main_tab1:
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📊 전체 레이아웃", "🚛 SD 구역", "🏭 SF 구역"])
    
    with sub_tab1:
        st.markdown('<div class="section-title">🚛 SD 보관 로케이션 라인</div>', unsafe_allow_html=True)
        render_sd_grid(SD_LOCS, db["sd_zone"]["r1"], db["sd_zone"]["r2"])
        
        st.markdown('<div class="section-title">🏭 SF 공정 로케이션 라인</div>', unsafe_allow_html=True)
        render_4part_grid('SF', max(len(SF_EVEN_H), len(SF_ODD_H)), SF_EVEN_H, SF_ODD_H,
                          db["sf_zone"]["even_r1"], db["sf_zone"]["even_r2"], db["sf_zone"]["odd_r1"], db["sf_zone"]["odd_r2"])

    with sub_tab2:
        st.markdown('<div class="section-title">🚛 SD 보관 구역 단독 모니터링</div>', unsafe_allow_html=True)
        render_sd_grid(SD_LOCS, db["sd_zone"]["r1"], db["sd_zone"]["r2"])

    with sub_tab3:
        st.markdown('<div class="section-title">🏭 SF 공정 구역 단독 모니터링</div>', unsafe_allow_html=True)
        render_4part_grid('SF', max(len(SF_EVEN_H), len(SF_ODD_H)), SF_EVEN_H, SF_ODD_H,
                          db["sf_zone"]["even_r1"], db["sf_zone"]["even_r2"], db["sf_zone"]["odd_r1"], db["sf_zone"]["odd_r2"])

with main_tab2:
    st.markdown('<div class="section-title">🔸 NF 북쪽 로케이션 라인</div>', unsafe_allow_html=True)
    render_4part_grid('NF', max(len(NF_EVEN_H), len(NF_ODD_H)), NF_EVEN_H, NF_ODD_H,
                      db["nf_zone"]["even_r1"], db["nf_zone"]["even_r2"], db["nf_zone"]["odd_r1"], db["nf_zone"]["odd_r2"])
    
    st.markdown('<div class="section-title">📦 DOC 신규 구역 라인 (보관 구조)</div>', unsafe_allow_html=True)
    render_sd_grid(DOC_LOCS, db["doc_zone"]["r1"], db["doc_zone"]["r2"])

if search_q:
    st.sidebar.success(f"🎯 '{search_q}' 번호 위치를 노란색으로 반전 표시 중입니다.")
