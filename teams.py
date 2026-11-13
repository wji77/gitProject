"""
2022 카타르 월드컵 16강 진출 16개국 데이터 및 국기 렌더러
"""

import math
import pygame


def create_flag_surface(code: str, width: int = 54, height: int = 36) -> pygame.Surface:
    """국가 코드를 기반으로 정밀한 국기 Surface를 생성합니다."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    w, h = width, height

    if code == "KOR":  # 대한민국 🇰🇷
        surf.fill((255, 255, 255))
        cx, cy = w // 2, h // 2
        r = h // 4
        pygame.draw.arc(surf, (205, 46, 58), (cx - r, cy - r, 2 * r, 2 * r), 0, math.pi, r)
        pygame.draw.arc(surf, (0, 71, 160), (cx - r, cy - r, 2 * r, 2 * r), math.pi, 2 * math.pi, r)
        pygame.draw.circle(surf, (205, 46, 58), (cx - r // 2, cy), r // 2)
        pygame.draw.circle(surf, (0, 71, 160), (cx + r // 2, cy), r // 2)
        for ox, oy in [(-r - 5, -r + 2), (r - 2, -r + 2), (-r - 5, r - 6), (r - 2, r - 6)]:
            pygame.draw.rect(surf, (0, 0, 0), (cx + ox, cy + oy, 8, 4))

    elif code == "JPN":  # 일본 🇯🇵
        surf.fill((255, 255, 255))
        pygame.draw.circle(surf, (188, 0, 45), (w // 2, h // 2), h // 3)

    elif code == "BRA":  # 브라질 🇧🇷
        surf.fill((0, 156, 59))
        points = [(w // 2, 4), (w - 6, h // 2), (w // 2, h - 4), (6, h // 2)]
        pygame.draw.polygon(surf, (255, 223, 0), points)
        pygame.draw.circle(surf, (0, 39, 118), (w // 2, h // 2), h // 4)

    elif code == "ARG":  # 아르헨티나 🇦🇷
        stripe = h // 3
        pygame.draw.rect(surf, (116, 172, 223), (0, 0, w, stripe))
        pygame.draw.rect(surf, (255, 255, 255), (0, stripe, w, stripe))
        pygame.draw.rect(surf, (116, 172, 223), (0, stripe * 2, w, h - stripe * 2))
        pygame.draw.circle(surf, (246, 180, 14), (w // 2, h // 2), 4)

    elif code == "FRA":  # 프랑스 🇫🇷
        sw = w // 3
        pygame.draw.rect(surf, (0, 35, 149), (0, 0, sw, h))
        pygame.draw.rect(surf, (255, 255, 255), (sw, 0, sw, h))
        pygame.draw.rect(surf, (237, 41, 57), (sw * 2, 0, w - sw * 2, h))

    elif code == "ENG":  # 잉글랜드 🏴󠁧󠁢󠁥󠁮󠁧󠁿
        surf.fill((255, 255, 255))
        pygame.draw.rect(surf, (206, 17, 38), (w // 2 - 3, 0, 6, h))
        pygame.draw.rect(surf, (206, 17, 38), (0, h // 2 - 3, w, 6))

    elif code == "ESP":  # 스페인 🇪🇸
        r_h = h // 4
        y_h = h - 2 * r_h
        pygame.draw.rect(surf, (170, 21, 27), (0, 0, w, r_h))
        pygame.draw.rect(surf, (241, 191, 0), (0, r_h, w, y_h))
        pygame.draw.rect(surf, (170, 21, 27), (0, r_h + y_h, w, r_h))

    elif code == "POR":  # 포르투갈 🇵🇹
        gw = int(w * 0.4)
        pygame.draw.rect(surf, (0, 102, 0), (0, 0, gw, h))
        pygame.draw.rect(surf, (255, 0, 0), (gw, 0, w - gw, h))
        pygame.draw.circle(surf, (255, 215, 0), (gw, h // 2), 6)

    elif code == "CRO":  # 크로아티아 🇭🇷
        sh = h // 3
        pygame.draw.rect(surf, (255, 0, 0), (0, 0, w, sh))
        pygame.draw.rect(surf, (255, 255, 255), (0, sh, w, sh))
        pygame.draw.rect(surf, (23, 70, 160), (0, sh * 2, w, h - sh * 2))
        pygame.draw.rect(surf, (200, 30, 30), (w // 2 - 4, sh - 2, 8, 8))

    elif code == "MAR":  # 모로코 🇲🇦
        surf.fill((193, 39, 45))
        cx, cy = w // 2, h // 2
        pts = []
        for i in range(10):
            ang = i * (math.pi / 5) - math.pi / 2
            r = 9 if i % 2 == 0 else 4
            pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        pygame.draw.polygon(surf, (0, 98, 51), pts)

    elif code == "NED":  # 네덜란드 🇳🇱
        sh = h // 3
        pygame.draw.rect(surf, (174, 28, 40), (0, 0, w, sh))
        pygame.draw.rect(surf, (255, 255, 255), (0, sh, w, sh))
        pygame.draw.rect(surf, (33, 70, 139), (0, sh * 2, w, h - sh * 2))

    elif code == "USA":  # 미국 🇺🇸
        for i in range(7):
            c = (179, 25, 66) if i % 2 == 0 else (255, 255, 255)
            pygame.draw.rect(surf, c, (0, i * (h // 7), w, h // 7 + 1))
        pygame.draw.rect(surf, (10, 49, 97), (0, 0, int(w * 0.4), int(h * 0.55)))

    elif code == "SUI":  # 스위스 🇨🇭
        surf.fill((218, 41, 28))
        cx, cy = w // 2, h // 2
        pygame.draw.rect(surf, (255, 255, 255), (cx - 3, cy - 8, 6, 16))
        pygame.draw.rect(surf, (255, 255, 255), (cx - 8, cy - 3, 16, 6))

    elif code == "POL":  # 폴란드 🇵🇱
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, w, h // 2))
        pygame.draw.rect(surf, (220, 20, 60), (0, h // 2, w, h - h // 2))

    elif code == "SEN":  # 세네갈 🇸🇳
        sw = w // 3
        pygame.draw.rect(surf, (0, 133, 63), (0, 0, sw, h))
        pygame.draw.rect(surf, (253, 239, 66), (sw, 0, sw, h))
        pygame.draw.rect(surf, (227, 27, 35), (sw * 2, 0, w - sw * 2, h))
        pygame.draw.circle(surf, (0, 133, 63), (w // 2, h // 2), 4)

    elif code == "AUS":  # 호주 🇦🇺
        surf.fill((0, 32, 91))
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, w // 2, h // 2))
        pygame.draw.rect(surf, (200, 16, 46), (w // 4 - 2, 0, 4, h // 2))
        pygame.draw.rect(surf, (200, 16, 46), (0, h // 4 - 2, w // 2, 4))
        pygame.draw.circle(surf, (255, 255, 255), (int(w * 0.75), h // 2), 3)

    pygame.draw.rect(surf, (80, 80, 80), (0, 0, w, h), 1)
    return surf


# 2022 카타르 월드컵 16강 진출 16개국 상세 정보
TEAMS_DATA = [
    {
        "code": "KOR",
        "name": "대한민국",
        "name_en": "South Korea",
        "color": (230, 25, 45),       # 붉은 악마 레드
        "secondary": (25, 25, 30),    # 블랙
        "accent": (255, 255, 255),
        "skin": (245, 205, 175),
        "hair": (30, 30, 30),
    },
    {
        "code": "ARG",
        "name": "아르헨티나",
        "name_en": "Argentina",
        "color": (116, 172, 223),     # 알비셀레스테 하늘색
        "secondary": (25, 25, 30),
        "accent": (255, 255, 255),
        "skin": (240, 200, 170),
        "hair": (50, 35, 25),
    },
    {
        "code": "FRA",
        "name": "프랑스",
        "name_en": "France",
        "color": (15, 45, 120),       # 레 블뢰 네이비
        "secondary": (240, 240, 240),
        "accent": (210, 30, 45),
        "skin": (150, 100, 70),
        "hair": (25, 25, 25),
    },
    {
        "code": "CRO",
        "name": "크로아티아",
        "name_en": "Croatia",
        "color": (215, 30, 35),       # 체크 레드
        "secondary": (255, 255, 255),
        "accent": (20, 50, 150),
        "skin": (245, 210, 180),
        "hair": (70, 50, 35),
    },
    {
        "code": "BRA",
        "name": "브라질",
        "name_en": "Brazil",
        "color": (250, 210, 20),      # 카나리아 옐로우
        "secondary": (20, 70, 180),   # 삼바 블루
        "accent": (0, 140, 50),
        "skin": (180, 130, 95),
        "hair": (25, 25, 25),
    },
    {
        "code": "ENG",
        "name": "잉글랜드",
        "name_en": "England",
        "color": (250, 250, 250),     # 삼사자 군단 화이트
        "secondary": (20, 40, 95),    # 네이비
        "accent": (205, 25, 35),
        "skin": (245, 210, 180),
        "hair": (90, 65, 40),
    },
    {
        "code": "JPN",
        "name": "일본",
        "name_en": "Japan",
        "color": (15, 55, 145),       # 사무라이 블루
        "secondary": (250, 250, 250),
        "accent": (220, 30, 30),
        "skin": (245, 205, 175),
        "hair": (30, 30, 30),
    },
    {
        "code": "MAR",
        "name": "모로코",
        "name_en": "Morocco",
        "color": (195, 35, 40),       # 아틀라스 사자 레드
        "secondary": (0, 110, 55),    # 그린
        "accent": (240, 240, 240),
        "skin": (200, 150, 110),
        "hair": (25, 25, 25),
    },
    {
        "code": "POR",
        "name": "포르투갈",
        "name_en": "Portugal",
        "color": (195, 25, 30),       # 셀레상 버건디
        "secondary": (0, 100, 50),    # 그린
        "accent": (240, 200, 30),
        "skin": (230, 185, 150),
        "hair": (30, 25, 20),
    },
    {
        "code": "ESP",
        "name": "스페인",
        "name_en": "Spain",
        "color": (200, 20, 30),       # 무적함대 라 로하
        "secondary": (15, 35, 80),    # 네이비
        "accent": (240, 190, 20),
        "skin": (235, 190, 155),
        "hair": (40, 30, 25),
    },
    {
        "code": "NED",
        "name": "네덜란드",
        "name_en": "Netherlands",
        "color": (245, 105, 15),      # 오렌지 군단
        "secondary": (245, 105, 15),
        "accent": (20, 40, 90),
        "skin": (245, 210, 180),
        "hair": (140, 100, 50),
    },
    {
        "code": "USA",
        "name": "미국",
        "name_en": "USA",
        "color": (245, 245, 250),     # 화이트
        "secondary": (15, 35, 95),    # 블루
        "accent": (200, 25, 40),
        "skin": (240, 200, 170),
        "hair": (80, 55, 35),
    },
    {
        "code": "SUI",
        "name": "스위스",
        "name_en": "Switzerland",
        "color": (215, 25, 30),       # 레드
        "secondary": (245, 245, 245), # 화이트
        "accent": (255, 255, 255),
        "skin": (245, 210, 180),
        "hair": (70, 50, 30),
    },
    {
        "code": "POL",
        "name": "폴란드",
        "name_en": "Poland",
        "color": (245, 245, 245),     # 화이트
        "secondary": (205, 20, 40),   # 레드
        "accent": (205, 20, 40),
        "skin": (245, 210, 180),
        "hair": (110, 85, 50),
    },
    {
        "code": "SEN",
        "name": "세네갈",
        "name_en": "Senegal",
        "color": (0, 130, 60),        # 테랑가의 사자 그린
        "secondary": (0, 130, 60),
        "accent": (245, 215, 30),
        "skin": (70, 45, 35),
        "hair": (15, 15, 15),
    },
    {
        "code": "AUS",
        "name": "호주",
        "name_en": "Australia",
        "color": (245, 195, 20),      # 사커루 골드
        "secondary": (0, 95, 60),     # 그린
        "accent": (0, 95, 60),
        "skin": (240, 200, 170),
        "hair": (100, 75, 45),
    },
]


DIFFICULTIES = [
    {
        "id": "EASY",
        "name": "완전 허당 (Very Bad)",
        "desc": "엉성한 AI: 아주 느리고 헛발질을 남발하며 멍을 자주 때립니다.",
        "ai_speed": 1.7,
        "ai_shot_power": 3.8,
        "color": (46, 204, 113),
    },
    {
        "id": "NORMAL",
        "name": "동네 축구 (Clumsy)",
        "desc": "초보 AI: 반응이 느리고 슛 세기가 매우 약해 쉽게 이길 수 있습니다.",
        "ai_speed": 2.1,
        "ai_shot_power": 5.0,
        "color": (241, 196, 15),
    },
    {
        "id": "HARD",
        "name": "약간 서툼 (Slow)",
        "desc": "느린 AI: 발이 느리고 슛 정확도가 떨어져 플레이어가 압도합니다.",
        "ai_speed": 2.5,
        "ai_shot_power": 6.2,
        "color": (231, 76, 60),
    },
]


