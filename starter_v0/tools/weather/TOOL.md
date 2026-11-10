---
name: weather
track: bonus
kind: live_api
provider: Open-Meteo
requires_env: []
inputs: [location]
outputs: [location, temperature, windspeed, weather_code, status]
side_effect: false
---
# weather

Tra cứu thông tin thời tiết hiện tại (nhiệt độ, tốc độ gió, trạng thái) tại một thành phố hoặc địa điểm cụ thể qua Open-Meteo API mở (miễn phí, không cần API key).
