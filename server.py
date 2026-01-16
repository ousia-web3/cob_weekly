from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import boto3
import io
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import pytz

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://192.168.82.105:5173",
    ],  # React Dev Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS Bedrock Configuration
BEDROCK_REGION = os.getenv("AWS_REGION", "us-west-2")
MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
ANTHROPIC_VERSION = os.getenv("ANTHROPIC_VERSION", "bedrock-2023-05-31")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
PROMPT_TEMPLATE = os.getenv("AI_PROMPT_TEMPLATE", "")

# TOP 20 추출 설정
USE_OCR_FOR_TOP20 = False  # True: OCR 사용, False: 텍스트 영역 사용

# 디버그 모드
DEBUG_MODE = True  # True: 상세 로그 출력, False: 최소 로그만 출력


def get_last_week_range():
    """
    KST 기준 전주(월요일~일요일) 날짜 범위를 계산

    Returns:
        tuple: (year, month, week_number, range_str, title)
        - year: 전주의 연도
        - month: 전주의 월
        - week_number: 해당 월의 몇 번째 주인지
        - range_str: "2025.12.09 ~ 2025.12.15" 형식
        - title: "2025년 12월 2주차 트래픽 현황 보고"
    """
    # KST 타임존 설정
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.now(kst)

    # 오늘 기준 요일 (0=월요일, 6=일요일)
    today_weekday = now_kst.weekday()

    # 지난주 월요일 계산
    # 월요일(0)이면 7일 전, 화요일(1)이면 8일 전... 일요일(6)이면 6일 전
    days_to_last_monday = today_weekday + 7
    last_monday = now_kst - timedelta(days=days_to_last_monday)

    # 지난주 일요일 계산 (월요일 + 6일)
    last_sunday = last_monday + timedelta(days=6)

    # 날짜 포맷팅
    start_date = last_monday.strftime("%Y.%m.%d")
    end_date = last_sunday.strftime("%Y.%m.%d")
    range_str = f"{start_date} ~ {end_date}"

    # 주차 계산 (해당 월의 몇 번째 주인지)
    year = last_monday.year
    month = last_monday.month
    day = last_monday.day
    week_number = (day - 1) // 7 + 1

    # 제목 생성
    title = f"{year}년 {month}월 {week_number}주차 트래픽 현황 보고"

    print(f"📅 전주 날짜 계산 완료: {range_str} (KST 기준, 월~일)")
    print(f"   - 연도: {year}, 월: {month}, 주차: {week_number}")

    return year, month, week_number, range_str, title


def extract_top20_from_cells(df):
    """
    엑셀 텍스트 영역에서 TOP 20 데이터 추출

    데이터 구조 (가로 방향):
    - 행 128 (인덱스 127): 대리점명 (열 3부터 시작)
    - 행 129 (인덱스 128): 채널유형
    - 행 130 (인덱스 129): UV
    - 행 133 (인덱스 132): 증감률
    """
    top20_data = []

    # 행 인덱스 (0-based)
    name_row = 127  # 행 128 (대리점명)
    type_row = 128  # 행 129 (채널유형)
    uv_row = 129  # 행 130 (UV)
    growth_row = 132  # 행 133 (증감률)

    # 열 시작 인덱스 (실제 데이터는 D열부터 = 인덱스 3)
    start_col = 3

    # 최대 20개까지 읽기
    for i in range(20):
        col_idx = start_col + i

        # 열이 범위를 벗어나면 중단
        if col_idx >= len(df.columns):
            break

        # 대리점명
        name = df.iloc[name_row, col_idx]
        if pd.isna(name):
            break  # 빈 열이면 종료
        name = str(name).strip()

        # 채널유형
        channel_type = df.iloc[type_row, col_idx]
        if pd.isna(channel_type):
            channel_type = ""
        else:
            channel_type = str(channel_type).strip()

        # UV
        uv_val = df.iloc[uv_row, col_idx]
        try:
            if isinstance(uv_val, str):
                uv = int(uv_val.replace(",", ""))
            else:
                uv = int(uv_val)
        except:
            uv = 0

        # 증감률
        growth_val = df.iloc[growth_row, col_idx]
        try:
            if isinstance(growth_val, str):
                # 문자열인 경우 (예: "▲5.3%", "▼0.2%")
                growth_str = growth_val.replace("%", "").strip()
                if "▲" in growth_str:
                    growth = float(growth_str.replace("▲", "").strip())
                elif "▼" in growth_str:
                    growth = -float(growth_str.replace("▼", "").strip())
                else:
                    growth = float(growth_str)
            else:
                # 소수 형태인 경우 (예: -0.601781 = -60.1781%)
                growth = float(growth_val) * 100

            # 소수점 1자리로 반올림
            growth = round(growth, 1)
        except:
            growth = 0

        if name and uv > 0:
            top20_data.append(
                {
                    "rank": i + 1,
                    "name": name,
                    "type": channel_type,
                    "uv": uv,
                    "growth": growth,
                }
            )

    print(f"텍스트 영역에서 TOP 20: {len(top20_data)}개 항목 추출")
    return top20_data


def generate_ai_insights(df):
    try:
        # Extract Key Data for the Prompt
        # Block 1: Rows 1-52 (Main Data)
        main_data = df.iloc[0:52].to_string()

        # Block 4: Rows 84-93 (Top 10 lists - used for Top 20 context)
        top10_data = df.iloc[83:93].to_string()

        # Construct Prompt using template from .env
        print(
            f"프롬프트 템플릿 로드 상태: {'있음 (길이: ' + str(len(PROMPT_TEMPLATE)) + ')' if PROMPT_TEMPLATE else '없음 - 기본값 사용'}"
        )

        if PROMPT_TEMPLATE:
            # Use template from .env and replace placeholders
            prompt = PROMPT_TEMPLATE.format(main_data=main_data, top10_data=top10_data)
            print(f"프롬프트 템플릿 사용 (처음 200자): {PROMPT_TEMPLATE[:200]}")
        else:
            # Fallback to default prompt if not set in .env
            prompt = f"""
        You are a data analyst for a travel agency. Analyze the following weekly traffic data and provide an executive summary.
        
        Data Context:
        - The data covers weekly UV (Unique Visitors) for a travel platform.
        - "Co-Brand" refers to partner sites.
        - Compare current week vs previous week.
        
        Data Snippets:
        
        [Main Data (Overview & Categories)]
        {main_data}
        
        [Top 10 Lists (Brand Mall & Affiliate)]
        {top10_data}
        
        Task:
        Generate 4 key insights (Executive Summary) in Korean.
        Format the output as a JSON array of objects with "title" and "content" keys.
        
        Example Format:
        [
            {{ "title": "Insight Title 1", "content": "Detailed explanation..." }},
            {{ "title": "Insight Title 2", "content": "Detailed explanation..." }}
        ]
        
        Focus on:
        1. Overall traffic trend (Growth/Decline).
        2. Notable category performance (e.g., Flight vs Hotel).
        3. Device share or specific channel performance if visible.
        4. Co-brand partner performance.
        
        Output ONLY the JSON array.
        """

        print("Calling AWS Bedrock...")
        bedrock = boto3.client(
            service_name="bedrock-runtime", region_name=BEDROCK_REGION
        )

        body = json.dumps(
            {
                "anthropic_version": ANTHROPIC_VERSION,
                "max_tokens": MAX_TOKENS,
                "messages": [{"role": "user", "content": prompt}],
            }
        )

        response = bedrock.invoke_model(
            body=body,
            modelId=MODEL_ID,
            accept="application/json",
            contentType="application/json",
        )

        response_body = json.loads(response.get("body").read())
        result_text = response_body["content"][0]["text"]

        # Debug: Print actual AI response
        print("=" * 80)
        print("AI 응답 (원본):")
        print(result_text)
        print("=" * 80)

        # Extract JSON from text
        start = result_text.find("[")
        end = result_text.rfind("]") + 1
        if start != -1 and end != -1:
            json_str = result_text[start:end]
            print(f"추출된 JSON: {json_str[:200]}...")
            return json.loads(json_str)
        else:
            print(f"JSON 찾기 실패 - start: {start}, end: {end}")
            return [
                {
                    "title": "AI 응답 파싱 오류",
                    "content": f"AI 응답에서 JSON을 찾을 수 없습니다.\n\n실제 응답:\n{result_text[:500]}",
                }
            ]

    except Exception as e:
        print(f"AI Generation Error: {e}")
        # Return mock insights if AI fails (e.g. no credentials)
        return [
            {
                "title": "AI 분석 실패",
                "content": f"AI 요약을 생성하는 중 오류가 발생했습니다: {str(e)}",
            },
            {
                "title": "시스템 메시지",
                "content": "AWS 자격 증명을 확인하거나 로컬 환경 설정을 점검해주세요.",
            },
        ]


def parse_excel_data(df):
    # Helper to safely get cell value
    def get_val(r, c):
        try:
            val = df.iloc[r, c]
            if pd.notna(val):
                # Try to convert to float
                if isinstance(val, (int, float)):
                    return float(val)
                elif isinstance(val, str):
                    # Remove commas and convert
                    cleaned = val.replace(",", "").strip()
                    return float(cleaned) if cleaned else 0
                else:
                    return 0
            return 0
        except Exception as e:
            if DEBUG_MODE:
                print(f"⚠️ get_val 오류 (행:{r+1}, 열:{c}): {e}")
            return 0

    def get_str(r, c):
        try:
            val = df.iloc[r, c]
            return str(val).strip() if pd.notna(val) else ""
        except:
            return ""

    # 1. Device Share
    # Updated: Index 102, Cols E-F
    mobile_decimal = get_val(102, 4)  # Index 102, Col E = index 4
    pc_decimal = get_val(102, 5)  # Index 102, Col F = index 5

    # Convert decimal to percentage (0.767655 -> 77)
    if mobile_decimal > 0 and mobile_decimal <= 1:
        mobile_share = round(mobile_decimal * 100)
        pc_share = round(pc_decimal * 100)
    else:
        # Fallback: if data format is different
        mobile_share = 77
        pc_share = 23

    print(f"디바이스 점유율 (Index 102): Mobile {mobile_share}%, PC {pc_share}%")

    device_data = [
        {"name": "Mobile", "value": mobile_share},
        {"name": "PC", "value": pc_share},
    ]

    # 2. Top 10 Lists
    # Updated: Indices 83-92 contain the TOP 10 data (행 84-93)
    # 행 83은 헤더이므로 제외
    def parse_top10(start_row, end_row, start_col_name, start_col_uv):
        lst = []
        for i in range(start_row, end_row):
            rank = i - start_row + 1
            if rank > 10:  # 상위 10개만
                break
            name = get_str(i, start_col_name)
            uv = get_val(i, start_col_uv)
            if (
                name
                and name != "0"
                and str(name).lower() != "nan"
                and name != "대리점명"
            ):
                lst.append(
                    {
                        "rank": rank,
                        "name": name,
                        "uv": int(uv) if isinstance(uv, (int, float)) else 0,
                    }
                )
        return lst

    # Brand Mall: Indices 83-92 (행 84-93), Col D (index 3) = Name, Col E (index 4) = UV
    brand_mall_data = parse_top10(83, 93, 3, 4)
    print(f"브랜드몰 TOP 10 (Index 83-92): {len(brand_mall_data)}개 항목")

    # Affiliate: Indices 83-92 (행 84-93), Col I (index 8) = Name, Col J (index 9) = UV
    affiliate_data = parse_top10(83, 93, 8, 9)
    print(f"제휴사 TOP 10 (Index 83-92): {len(affiliate_data)}개 항목")

    # Official Center: Indices 83-92 (행 84-93), Col O (index 14) = Name, Col P (index 15) = UV
    official_center_data = parse_top10(83, 93, 14, 15)
    print(f"공식인증센터 TOP 10 (Index 83-92): {len(official_center_data)}개 항목")

    # 전주대비 증감률 (행 94, 인덱스 93)
    # F열(인덱스 5) = 브랜드몰, K열(인덱스 10) = 제휴사, Q열(인덱스 16) = 공식인증센터
    # 형식: "(전주비 3.2%↓)" 또는 "(전주비 43.2%↑)"

    def parse_growth_string(growth_str):
        """전주비 문자열 파싱: (전주비 3.2%↓) -> -3.2"""
        if pd.isna(growth_str):
            return 0

        growth_str = str(growth_str)
        try:
            # 숫자 추출
            import re

            match = re.search(r"(\d+\.?\d*)", growth_str)
            if not match:
                return 0

            value = float(match.group(1))

            # 방향 확인 (↓ = 하락 = 음수, ↑ = 상승 = 양수)
            if "↓" in growth_str:
                return -value
            elif "↑" in growth_str:
                return value
            else:
                return value
        except:
            return 0

    brand_mall_growth = parse_growth_string(get_str(93, 5))
    affiliate_growth = parse_growth_string(get_str(93, 10))
    official_center_growth = parse_growth_string(get_str(93, 16))

    # 소수점 1자리로 반올림
    brand_mall_growth = round(brand_mall_growth, 1)
    affiliate_growth = round(affiliate_growth, 1)
    official_center_growth = round(official_center_growth, 1)

    print(
        f"전주대비 증감률 - 브랜드몰: {brand_mall_growth}%, 제휴사: {affiliate_growth}%, 공식인증센터: {official_center_growth}%"
    )

    def calc_meta(data, growth):
        total = sum(item["uv"] for item in data)
        return {"totalUV": total, "growth": growth, "data": data}

    detailed_top10 = {
        "brandMall": calc_meta(brand_mall_data, brand_mall_growth),
        "affiliate": calc_meta(affiliate_data, affiliate_growth),
        "officialCenter": calc_meta(official_center_data, official_center_growth),
    }

    # 3. Co-Brand Top 20 (실제 데이터 추출)
    combined_top20 = extract_top20_from_cells(df)

    if combined_top20:
        print(f"코브랜드 TOP 20: {len(combined_top20)}개 항목 추출 완료")
        print(
            f"  1위: {combined_top20[0]['name']} ({combined_top20[0]['type']}) - {combined_top20[0]['uv']:,} UV"
        )
    else:
        print("⚠ TOP 20 데이터를 찾을 수 없습니다. Mock 데이터 사용")
        # Fallback: 기존 방식 사용
        combined_top20 = []
        for item in brand_mall_data:
            combined_top20.append({**item, "type": "브랜드몰"})
        for item in affiliate_data:
            combined_top20.append({**item, "type": "제휴채널"})

        combined_top20.sort(key=lambda x: x["uv"], reverse=True)
        combined_top20 = combined_top20[:20]

        for idx, item in enumerate(combined_top20):
            item["rank"] = idx + 1
            item["growth"] = 0

    # ========================================
    # 실제 데이터 추출 (Mock 데이터 제거)
    # ========================================

    # 1. Summary 데이터 추출
    # 행 15 (인덱스 14): 전체 UV 데이터

    # 동적 컬럼 감지: 행 14 (인덱스 13)에서 헤더 찾기
    header_row_idx = 13
    col_current = -1
    col_prev = -1
    col_rate = -1

    print(f"🔍 헤더 분석 (행 {header_row_idx+1}):")
    headers = []
    for c in range(min(10, len(df.columns))):  # 처음 10개 열만 확인 (메인 데이터 영역)
        val = str(df.iloc[header_row_idx, c]).strip()
        headers.append(f"{c}:{val}")
        # 첫 번째로 발견된 헤더만 사용
        if val == "UV" and col_current == -1:
            col_current = c
        elif val == "전주UV" and col_prev == -1:
            col_prev = c
        elif val == "증감률" and col_rate == -1:
            col_rate = c

    print(f"  발견된 헤더들: {', '.join(headers)}")

    # 헤더를 못 찾으면 기본값(실제 엑셀 기준) 사용: E(4), F(5), G(6)
    if col_current == -1:
        col_current = 4  # E열: UV
    if col_prev == -1:
        col_prev = 5  # F열: 전주UV
    if col_rate == -1:
        col_rate = 6  # G열: 증감률

    print(
        f"✅ 컬럼 인덱스 확정: Current={col_current}, Prev={col_prev}, Rate={col_rate}"
    )

    # Summary 데이터 추출
    total_uv = int(get_val(14, col_current))
    prev_total_uv = int(get_val(14, col_prev))
    growth_decimal = get_val(14, col_rate)

    # 증감률 처리 함수 (공통 사용)
    def parse_rate(val):
        if val == 0:
            return 0
        try:
            # 절댓값이 1 이하면 소수로 간주 (0.044 → 4.4%)
            if abs(val) <= 1:
                return round(val * 100, 1)
            else:
                # 이미 퍼센트 형식 (4.4 → 4.4%)
                return round(val, 1)
        except Exception as e:
            if DEBUG_MODE:
                print(f"⚠️ parse_rate 오류 (값:{val}): {e}")
            return 0

    growth_rate = parse_rate(growth_decimal)

    print(f"전체 UV: {total_uv:,}, 전주 UV: {prev_total_uv:,}, 증감률: {growth_rate}%")

    # 2. Categories 데이터 추출 - 고정 구조 사용
    # 엑셀 데이터를 맵으로 저장
    excel_data_map = {}
    last_category = ""  # Forward Fill을 위한 변수

    for row_idx in range(14, 51):  # 행 15-51
        raw_category = get_str(row_idx, 2)  # C열: 구분
        sub_category = get_str(row_idx, 3)  # D열: 상세 구분

        # Category Forward Fill Logic (공백 처리 개선)
        # 공백 제거 후 검증
        raw_category_clean = raw_category.strip() if raw_category else ""
        if raw_category_clean and raw_category_clean != "nan":
            last_category = raw_category_clean

        # 현재 카테고리 결정: 값이 있으면 그거 쓰고, 없으면 last_category 사용
        category = (
            raw_category_clean
            if raw_category_clean and raw_category_clean != "nan"
            else last_category
        )

        if category or sub_category:
            # nan 값을 빈 문자열로 처리
            sub_clean = (
                "" if (not sub_category or sub_category == "nan") else sub_category
            )
            key = f"{category}|{sub_clean}".strip()
            current_val = get_val(row_idx, col_current)
            prev_val = get_val(row_idx, col_prev)
            rate_decimal = get_val(row_idx, col_rate)

            if current_val or prev_val:  # 둘 중 하나라도 있으면 데이터 존재로 간주
                rate = parse_rate(rate_decimal)

                excel_data_map[key] = {
                    "current": int(current_val),
                    "prev": int(prev_val),
                    "rate": rate,
                }

                # 디버그: 모든 항목의 키 출력 (매핑 확인용)
                if DEBUG_MODE:
                    print(
                        f"  행 {row_idx+1}: 키='{key}' | UV:{int(current_val):,} / 전주:{int(prev_val):,} / 증감률:{rate}%"
                    )
                    # 특정 키 강조 출력
                    if "국내 패키지" in key or "기획전" in key or "플레이스" in key:
                        print(f"  ⭐ 중요: '{key}' (repr: {repr(key)})")

    # 고정된 카테고리 구조 정의
    fixed_categories = [
        {
            "group": "공통",
            "items": [
                {"name": "전체", "key": "전체|"},
                {"name": "메인", "key": "메인|"},
                {"name": "검색", "key": "검색|"},
            ],
        },
        {
            "group": "패키지",
            "items": [
                {"name": "대표상품", "key": "패키지|대표상품"},
                {"name": "상품상세", "key": "패키지|상품상세"},
                {"name": "예약하기", "key": "패키지|예약하기"},
                {"name": "예약완료", "key": "패키지|예약완료"},
            ],
        },
        {
            "group": "해외 패키지",
            "items": [
                {"name": "서브메인", "key": "해외 패키지|서브메인"},
            ],
        },
        {
            "group": "국내 패키지",
            "items": [
                {"name": "서브메인", "key": "국내 패키지\n(제주서브메인포함)|서브메인"},
            ],
        },
        {
            "group": "허니문",
            "items": [
                {"name": "서브메인", "key": "허니문|서브메인"},
            ],
        },
        {
            "group": "해외골프",
            "items": [
                {"name": "서브메인", "key": "해외골프|서브메인"},
            ],
        },
        {
            "group": "국내골프",
            "items": [
                {"name": "서브메인", "key": "국내골프|서브메인"},
            ],
        },
        {
            "group": "제우스",
            "items": [
                {"name": "서브메인", "key": "제우스|서브메인"},
            ],
        },
        {
            "group": "크루즈",
            "items": [
                {"name": "서브메인", "key": "크루즈|서브메인"},
            ],
        },
        {
            "group": "트레킹",
            "items": [
                {"name": "서브메인", "key": "트레킹|서브메인"},
            ],
        },
        {
            "group": "해외호텔",
            "items": [
                {"name": "서브메인", "key": "해외호텔|서브메인"},
            ],
        },
        {
            "group": "기획전",
            "items": [
                {"name": "전체", "key": "기획전|"},
            ],
        },
        {
            "group": "플레이스",
            "items": [
                {"name": "메인", "key": "플레이스|메인"},
                {"name": "상세", "key": "플레이스|상세"},
            ],
        },
        {
            "group": "항공(해외)",
            "items": [
                {"name": "서브메인", "key": "항공\n(해외)|서브메인"},
                {"name": "검색(해외)", "key": "항공\n(해외)|검색(해외)"},
                {"name": "약관동의", "key": "항공\n(해외)|약관동의"},
                {"name": "예약정보입력", "key": "항공\n(해외)|예약정보입력"},
                {"name": "예약완료", "key": "항공\n(해외)|예약완료"},
            ],
        },
        {
            "group": "호텔(해외)",
            "items": [
                {"name": "서브메인", "key": "호텔 \n(해외)|서브메인"},
                {"name": "상품리스팅", "key": "호텔 \n(해외)|상품리스팅"},
                {"name": "상품상세", "key": "호텔 \n(해외)|상품상세"},
                {"name": "예약하기", "key": "호텔 \n(해외)|예약하기"},
                {"name": "결제완료", "key": "호텔 \n(해외)|결제완료"},
            ],
        },
        {
            "group": "마이페이지",
            "items": [
                {"name": "메인", "key": "마이페이지|서브메인"},
                {"name": "패키지", "key": "마이페이지|패키지"},
                {"name": "해외항공", "key": "마이페이지|해외항공"},
                {"name": "국내항공", "key": "마이페이지|국내항공"},
                {"name": "호텔", "key": "마이페이지|호텔"},
            ],
        },
    ]

    # Best Growth & Worst Drop 초기화
    best_growth = {"name": "-", "rate": -999}
    worst_drop = {"name": "-", "rate": 999}

    # 고정 구조에 엑셀 데이터 매핑 및 Best/Worst 계산
    categories_data = []
    for group in fixed_categories:
        items = []
        for item_template in group["items"]:
            # 엑셀 데이터에서 값 찾기
            data = excel_data_map.get(
                item_template["key"], {"current": 0, "prev": 0, "rate": 0}
            )

            # 항목 추가
            items.append(
                {
                    "name": item_template["name"],
                    "current": data["current"],
                    "prev": data["prev"],
                    "rate": data["rate"],
                }
            )

            # Best/Worst 업데이트 - 패키지, 항공(해외), 호텔(해외) 3개 카테고리만 대상
            target_groups = ["패키지", "항공(해외)", "호텔(해외)"]
            if group["group"] in target_groups and data["current"] > 0:
                # 항상 "그룹명 항목명" 형식으로 표시 (예: "호텔(해외) 예약하기")
                display_name = f"{group['group']} {item_template['name']}"

                if data["rate"] > best_growth["rate"]:
                    best_growth = {"name": display_name, "rate": data["rate"]}
                if data["rate"] < worst_drop["rate"]:
                    worst_drop = {"name": display_name, "rate": data["rate"]}

        categories_data.append({"group": group["group"], "items": items})

    # 만약 데이터가 없어서 초기값 그대로라면 수정
    if best_growth["rate"] == -999:
        best_growth = {"name": "-", "rate": 0}
    if worst_drop["rate"] == 999:
        worst_drop = {"name": "-", "rate": 0}

    print(f"카테고리 데이터: {len(categories_data)}개 그룹 추출")
    print(f"Best Growth: {best_growth['name']} ({best_growth['rate']}%)")
    print(f"Worst Drop: {worst_drop['name']} ({worst_drop['rate']}%)")

    # 3. Trend 데이터 (주간 추이) - 행 119-124 (인덱스 118-123)
    # 열 C (인덱스 2): 주차명 (예: "10월 05주차")
    # 열 D (인덱스 3): UV
    trend_data = []
    for row_idx in range(118, 124):  # 행 119-124 (인덱스 118-123)
        week_name = get_str(row_idx, 2)  # C열: 주차명
        uv_val = get_val(row_idx, 3)  # D열: UV

        if week_name and uv_val:
            # "10월 05주차" -> "10월 5주"로 변환
            week_name_formatted = week_name.replace("주차", "주").replace(" 0", " ")
            trend_data.append({"name": week_name_formatted, "uv": int(uv_val)})

    print(f"주간 추이 데이터: {len(trend_data)}개 주차 추출")

    summary_data = {
        "totalUV": total_uv,
        "prevTotalUV": prev_total_uv,
        "growth": growth_rate,
        "mobileShare": mobile_share,
        "bestGrowth": best_growth,
        "worstDrop": worst_drop,
    }

    # KST 기준 전주 날짜 범위 계산
    year, month, week_number, range_str, title = get_last_week_range()

    return {
        "meta": {
            "year": year,
            "month": month,
            "weekNumber": week_number,
            "range": range_str,
            "title": title,
        },
        "summary": summary_data,
        "trend": trend_data,
        "device": device_data,
        "categories": categories_data,
        "coBrandTop20": combined_top20,
        "detailedTop10": detailed_top10,
    }


@app.post("/analyze")
def analyze_excel(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        df = pd.read_excel(io.BytesIO(contents), header=None)

        # 1. Parse Data
        dashboard_data = parse_excel_data(df)

        # 2. Generate AI Insights
        ai_insights = generate_ai_insights(df)

        # 3. Combine
        dashboard_data["aiInsight"] = ai_insights

        return dashboard_data

    except Exception as e:
        error_msg = traceback.format_exc()
        print(error_msg)
        with open("server_error.log", "a") as f:
            f.write(f"[{datetime.now()}] Error: {str(e)}\n{error_msg}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save-json")
async def save_json(data: dict):
    """JSON 데이터를 data/json 폴더에 저장"""
    try:
        # data/json 폴더 생성
        json_dir = "data/json"
        os.makedirs(json_dir, exist_ok=True)

        # 파일명 생성 (타임스탬프 포함)
        title = data.get("meta", {}).get("title", "dashboard")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title}_{timestamp}.json"
        filepath = os.path.join(json_dir, filename)

        # JSON 저장
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ JSON 저장 완료: {filepath}")
        return {"success": True, "filepath": filepath, "filename": filename}

    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"JSON 저장 오류: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save-html")
async def save_html(request: dict):
    """HTML 파일을 data/html 폴더에 저장"""
    try:
        # data/html 폴더 생성
        html_dir = "data/html"
        os.makedirs(html_dir, exist_ok=True)

        # 파일명 생성 (타임스탬프 포함)
        title = request.get("title", "dashboard")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title}_{timestamp}.html"
        filepath = os.path.join(html_dir, filename)

        # HTML 저장
        html_content = request.get("html", "")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✓ HTML 저장 완료: {filepath}")
        return {"success": True, "filepath": filepath, "filename": filename}

    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"HTML 저장 오류: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
