from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
import urllib.parse

app = FastAPI()

# UUID پیش‌فرض (اگر خواستی می‌تونی توی URL با پارامتر uuid تغییرش بدی)
DEFAULT_UUID = "d341d1ea-45b2-4e13-9e7b-71a7d0a9a7b8"

@app.get("/", response_class=PlainTextResponse)
async def generate_config(
    request: Request,
    # پارامترهای اصلی
    uuid: str = Query(DEFAULT_UUID, description="UUID برای VLESS"),
    ip: str = Query("188.114.97.6", description="آی‌پی کلودفلر یا سرور شما"),
    port: int = Query(443, description="پورت"),
    net: str = Query("ws", description="نوع اتصال: ws, xhttp, grpc"),
    path: str = Query("/vless", description="مسیر WebSocket یا XHTTP"),
    
    # پارامترهای عبور از فایروال (بر اساس متن شما)
    ech: str = Query("cloudflare-ech.com+udp://1.1.1.1", description="ECH Config"),
    final_mask: str = Query("", description="FinalMask"),
    cipher_suites: str = Query("", description="CipherSuites"),
    fp: str = Query("chrome", description="فینگرپرینت (chrome یا unsafe)"),
    alpn: str = Query("h2,http/1.1", description="ALPN"),
    xudp: bool = Query(True, description="فعال‌سازی XUDP"),
    security: str = Query("tls", description="نوع امنیت: tls یا none")
):
    # 1. پیدا کردن خودکار Host از روی دامنه ورودی
    host = request.headers.get("host", "your-domain.vercel.app")
    if ":" in host:
        host = host.split(":")[0]

    # 2. ساخت query string
    params = {
        "type": net,
        "security": security,
        "sni": host,
        "host": host,
        "path": path,
        "fp": fp,
        "alpn": alpn,
    }
    
    # اضافه کردن پارامترهای فایروال در صورت وجود
    if ech: params["echConfigList"] = ech
    if final_mask: params["finalMask"] = final_mask
    if cipher_suites: params["cipherSuites"] = cipher_suites
    if xudp: params["packetEncoding"] = "xudp"

    # 3. ساخت لینک نهایی
    query = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v])
    vless_link = f"vless://{uuid}@{ip}:{port}?{query}#Vercel-Auto-Config"

    # 4. خروجی متن ساده
    return f"""🔹 کانفیگ VLESS شما آماده است:

{vless_link}

----------------------------------------
📌 مشخصات خودکار:
- Host (SNI): {host}
- IP: {ip}
- FinalMask: {final_mask if final_mask else 'خالی'}
- CipherSuites: {cipher_suites if cipher_suites else 'خالی'}
- Fingerprint: {fp}
- ECH: {ech if ech else 'خالی'}
- XUDP: {'فعال' if xudp else 'غیرفعال'}
"""
