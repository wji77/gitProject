"""
학교알리미(SchoolInfo) Open API 조회 스크립트
- 은평구 관할 초등학교 기본정보 조회
- '서울응암초등학교' 상세 기본정보 필터링 및 출력
"""

import json
import sys
import requests

# 1. API 키 및 조회 조건 설정
API_KEY = "983ec1b685364d3498975d0c2e67e66b"
BASE_URL = "https://www.schoolinfo.go.kr/openApi.do"

# 기본 조회 조건
PARAMS = {
    "apiKey": API_KEY,
    "apiType": "0",         # 0: 학교기본정보
    "sidoCode": "11",       # 11: 서울특별시
    "sggCode": "11380",     # 11380: 은평구
    "schulKndCode": "02",   # 02: 초등학교
}

# 검색할 학교명 (기본값: 응암초등학교, 인자가 있으면 인자 사용)
SEARCH_NAME = sys.argv[1] if len(sys.argv) > 1 else "응암초등학교"


def fetch_school_info():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print("=" * 60)
    print(" 🏫 학교알리미 Open API 정보 조회 시작")
    print(" • 대상 지역: 서울특별시 은평구 (초등학교)")
    print(f" • 검색 대상 학교명 키워드: '{SEARCH_NAME}'")
    print("=" * 60)

    try:
        # 2. GET 요청 전송
        response = requests.get(BASE_URL, params=PARAMS, headers=headers, timeout=10)
        response.raise_for_status()

        # 3. JSON 파싱
        data = response.json()

        result_code = data.get("resultCode")
        if result_code != "success":
            print(f"❌ API 호출 실패: {data.get('resultMsg', '응답 코드 확인 필요')}")
            return False

        school_list = data.get("list", [])
        print(f"✔ 총 {len(school_list)}개 학교 정보 수신 완료\n")

        # 4. 대상 학교 필터링
        target_school = next(
            (s for s in school_list if SEARCH_NAME in s.get("SCHUL_NM", "")),
            None
        )

        if not target_school:
            print(f"⚠️ 은평구 초등학교 목록에서 '{SEARCH_NAME}'을(를) 찾을 수 없습니다.")
            print(" [은평구 초등학교 목록]")
            for idx, s in enumerate(school_list, 1):
                print(f"  {idx:2d}. {s.get('SCHUL_NM')}")
            return False

        # 5. 상세 정보 출력
        print("=" * 60)
        print(f"  [{target_school.get('SCHUL_NM')}] 기본 정보 조회 결과")
        print("=" * 60)
        print(f"• 학교명               : {target_school.get('SCHUL_NM')}")
        print(f"• 정보공시 학교코드    : {target_school.get('SCHUL_CODE')}")
        print(f"• 관할 교육청          : {target_school.get('ATPT_OFCDC_ORG_NM')}")
        print(f"• 관할 교육지원청      : {target_school.get('JU_ORG_NM')}")
        print(f"• 설립구분 / 설립유형  : {target_school.get('FOND_SC_CODE')} / {target_school.get('SCHUL_FOND_TYP_CODE')}")
        print(f"• 개교기념일 / 설립일  : {target_school.get('FOAS_MEMRD')} / {target_school.get('FOND_YMD')}")
        print(f"• 남녀공학 구분        : {target_school.get('COEDU_SC_CODE')}")
        print(f"• 도로명 주소          : {target_school.get('SCHUL_RDNMA')}{target_school.get('SCHUL_RDNDA', '')}")
        print(f"• 우편번호             : {target_school.get('ZIP_CODE')} (도로명: {target_school.get('SCHUL_RDNZC', '').strip()})")
        print(f"• 교무실 전화번호      : {target_school.get('USER_TELNO_SW') or target_school.get('USER_TELNO')}")
        print(f"• 행정실 전화번호      : {target_school.get('USER_TELNO_GA')}")
        print(f"• 팩스번호             : {target_school.get('PERC_FAXNO')}")
        print(f"• 홈페이지 주소        : {target_school.get('HMPG_ADRES')}")
        print(f"• 위치 좌표 (위도/경도): {target_school.get('LTTUD')} / {target_school.get('LGTUD')}")
        print(f"• 폐교 / 분교 여부     : 폐교({target_school.get('CLOSE_YN')}) / 분교({target_school.get('ABSCH_YN')})")
        print("=" * 60)
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 요청 오류 발생: {e}")
        return False
    except json.JSONDecodeError:
        print("❌ 응답 데이터를 JSON 형태로 파싱할 수 없습니다.")
        return False


if __name__ == "__main__":
    fetch_school_info()
