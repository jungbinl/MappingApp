from fastapi import FastAPI
import json
import os

app = FastAPI(title="컨테이너 관제 시스템 백엔드 API")

# 파일이 없거나 깨졌을 때 보낼 디폴트 빈 데이터 크기 정의 (고정틀 크기와 일치)
DEFAULT_DATA = {
    "sd_zone": {"r1": [""] * 30, "r2": [""] * 30},
    "sf_zone": {"even_r1": [""] * 39, "even_r2": [""] * 39, "odd_r1": [""] * 39, "odd_r2": [""] * 39},
    "nf_zone": {"even_r1": [""] * 34, "even_r2": [""] * 34, "odd_r1": [""] * 35, "odd_r2": [""] * 35},
    "doc_zone": {"r1": [""] * 2, "r2": [""] * 2}
}

@app.get("/api/containers")
def load_json_db():
    json_path = "data.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("🚨 'data.json' 파일의 형식이 깨졌습니다!")
            
    # 파일이 없거나 형식이 깨진 경우 디폴트 빈 구조 반환
    return DEFAULT_DATA

# 💡 터미널에서 실행 명령: uvicorn loaddata:app --reload