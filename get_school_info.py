# -*- coding: utf-8 -*-
"""
학교알리미 OPEN API - 서울응암초등학교 기본정보 조회 샘플 소스
인코딩: UTF-8
"""

import requests
import json

# 1. API 키 및 요청 인자 설정
API_KEY = "983ec1b685364d3498975d0c2e67e66b"  # 학교알리미 발급 인증키
API_TYPE = "0"        # 0: 학교기본정보
SIDO_CODE = "11"      # 11: 서울특별시
SGG_CODE = "11380"    # 11380: 은평구 (응암초등학교 관할 시군구코드)
SCHUL_KND = "02"      # 02: 초등학교

# 2. 활용예시 규격에 맞춘 요청 URL 생성
BASE_URL = "https://www.schoolinfo.go.kr/openApi.do"
QUERY_STRING = (
    f"?apiKey={API_KEY}"
    f"&apiType={API_TYPE}"
    f"&sidoCode={SIDO_CODE}"
    f"&sggCode={SGG_CODE}"
    f"&schulKndCode={SCHUL_KND}"
)
TARGET_URL = BASE_URL + QUERY_STRING

def fetch_school_info():
    print(f"[요청 URL]\n{TARGET_URL}\n")
    
    try:
        # GET 요청 전송
        response = requests.get(TARGET_URL, timeout=10)
        response.raise_for_status()

        # UTF-8 JSON 응답 데이터 파싱
        data = response.json()

        if data.get("resultCode") == "success" and "list" in data:
            school_list = data["list"]

            # 은평구 관내 초등학교 목록 중 '응암초등학교' 검색
            target_school = next(
                (school for school in school_list if "응암초등학교" in school.get("SCHUL_NM", "")),
                None
            )

            if target_school:
                print("=" * 60)
                print(f"       [{target_school.get('SCHUL_NM')}] 학교 기본정보")
                print("=" * 60)
                print(f"• 학교명             : {target_school.get('SCHUL_NM')}")
                print(f"• 정보공시 학교코드   : {target_school.get('SCHUL_CODE')}")
                print(f"• 관할 교육청         : {target_school.get('ATPT_OFCDC_ORG_NM')}")
                print(f"• 관할 교육지원청     : {target_school.get('JU_ORG_NM')}")
                print(f"• 설립구분 / 설립유형 : {target_school.get('FOND_SC_CODE')} / {target_school.get('SCHUL_FOND_TYP_CODE')}")
                print(f"• 개교기념일 / 설립일 : {target_school.get('FOAS_MEMRD')} / {target_school.get('FOND_YMD')}")
                print(f"• 남녀공학 구분       : {target_school.get('COEDU_SC_CODE')}")
                print(f"• 도로명 주소         : {target_school.get('SCHUL_RDNMA')} {target_school.get('SCHUL_RDNDA', '')}")
                print(f"• 우편번호             : {target_school.get('ZIP_CODE')} (도로명: {target_school.get('SCHUL_RDNZC')})")
                print(f"• 전화번호(교무실)     : {target_school.get('USER_TELNO_SW')}")
                print(f"• 전화번호(행정실)     : {target_school.get('USER_TELNO_GA')}")
                print(f"• 팩스번호             : {target_school.get('PERC_FAXNO')}")
                print(f"• 홈페이지             : {target_school.get('HMPG_ADRES')}")
                print(f"• 위치 좌표(위도/경도) : {target_school.get('LTTUD')} / {target_school.get('LGTUD')}")
                print(f"• 휴교 / 폐교 여부     : 휴교({target_school.get('CLOSE_YN')}) / 폐교({target_school.get('ABSCH_YN')})")
                print("=" * 60)
            else:
                print("[알림] 은평구 초등학교 목록에서 '응암초등학교'를 찾을 수 없습니다.")
        else:
            print(f"[오류] API 호출 실패: {data.get('resultMsg', '응답 데이터 확인 필요')}")

    except requests.exceptions.RequestException as e:
        print(f"[네트워크 오류] {e}")
    except json.JSONDecodeError:
        print("[데이터 오류] 응답 데이터를 JSON으로 변환할 수 없습니다.")

if __name__ == "__main__":
    fetch_school_info()
