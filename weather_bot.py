import requests
import datetime

# -------------------------
# 1. API 설정
# -------------------------
API_KEY = "vlmg_uHYTy2ZoP7h2G8tJQ"

# 구로구 좌표 (nx, ny) - 기상청 격자 좌표
NX, NY = 58, 125  

# -------------------------
# 2. 텔레그램 설정
# -------------------------
TELEGRAM_TOKEN = "텔레그램봇토큰"
CHAT_ID = "내_채팅방_ID"
TG_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def get_weather():
    """기상청 단기예보에서 오늘 강수확률 가져오기"""
    now = datetime.datetime.now()

    # 발표 시각 (API는 0200, 0500, 0800, ... 식으로 발표)
    base_date = now.strftime("%Y%m%d")
    base_time = "0500"  # 가장 안정적인 시간대 선택 (05시 발표본)

    BASE_URL = f"https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtNcst"


    params = {
        "authKey": API_KEY,
        "numOfRows": "1000",
        "pageNo": "1",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": NX,
        "ny": NY,
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    print(data)
    print(params)

    try:
        items = data["response"]["body"]["items"]["item"]
    except KeyError:
        return None

    # 현재 시각 이후 3시간 예보만 확인
    rain_info = []
    for item in items:
        if item["category"] == "POP":  # 강수확률
            fcst_time = item["fcstTime"]
            fcst_value = int(item["fcstValue"])  # %
            rain_info.append((fcst_time, fcst_value))

    return rain_info


def send_message(text):
    """텔레그램 메시지 전송"""
    requests.post(TG_URL, data={"chat_id": CHAT_ID, "text": text})


def main():
    rain_info = get_weather()
    if not rain_info:
        send_message("⚠️ 날씨 정보를 가져올 수 없습니다.")
        return

    # 3시간 이내 강수확률 체크
    now = datetime.datetime.now()
    next_hours = [int(now.strftime("%H")) + i for i in range(1, 4)]

    will_rain = False
    for time_str, pop in rain_info:
        hour = int(time_str[:2])
        if hour in next_hours and pop >= 50:  # 50% 이상이면 비 온다고 가정
            will_rain = True
            send_message(f"☔ {hour}시에 비 올 확률이 {pop}%입니다. 우산 챙기세요!")
            break

    if not will_rain:
        send_message("🌞 앞으로 3시간 동안 비 예보가 없습니다.")


if __name__ == "__main__":
    main()
