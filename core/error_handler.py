from __future__ import annotations

from models.app_error import AppError


class ErrorHandler:
    @staticmethod
    def classify_analyze_error(message: str, detail: str = "") -> AppError:
        blob = f"{message} | {detail}".lower()

        if "unsupported url" in blob or "unsupported site" in blob:
            return AppError(
                code="unsupported_url",
                title="Desteklenmeyen Link",
                message="Bu baglanti yt-dlp tarafinda desteklenmiyor olabilir.",
                detail=detail or message,
                suggestion="Farkli bir link deneyin veya yt-dlp'yi guncelleyip tekrar deneyin.",
            )
        if "login" in blob or "sign in" in blob or "private" in blob or "members only" in blob:
            return AppError(
                code="login_required",
                title="Oturum Gerekli",
                message="Icerige erismek icin gecerli browser cookies gerekebilir.",
                detail=detail or message,
                suggestion="Linki secili browser'da acin, hesaba girin ve yeniden analiz edin.",
            )
        if "age-restricted" in blob or "confirm your age" in blob:
            return AppError(
                code="age_gate",
                title="Yas Siniri",
                message="Icerik yas siniri nedeniyle ek yetki istiyor olabilir.",
                detail=detail or message,
                suggestion="Secili browser'da hesaba girin ve ayni browser ile tekrar deneyin.",
            )
        if "geo" in blob or "not available in your country" in blob or "this video is not available in your country" in blob:
            return AppError(
                code="geo_blocked",
                title="Bolgesel Engelleme",
                message="Icerik bulundugunuz bolgede kullanilamiyor olabilir.",
                detail=detail or message,
                suggestion="Farkli hedef veya farkli erisim kosulu ile tekrar deneyin.",
            )
        if "cookie" in blob and ("decrypt" in blob or "dpapi" in blob):
            return AppError(
                code="cookie_decrypt",
                title="Cookie Cozme Hatasi",
                message="Secili browser cookie verisi okunamadi veya cozulmedi.",
                detail=detail or message,
                suggestion="Baska bir browser secin veya ilgili browser'da linki acip tekrar deneyin.",
            )
        if "cookie" in blob:
            return AppError(
                code="cookie_access",
                title="Cookie Erisim Hatasi",
                message="Secili browser'dan gecerli cookie alinmadi.",
                detail=detail or message,
                suggestion="Browser secimini degistirin veya fallback secenegini acin.",
            )
        if "js challenge" in blob or "n challenge" in blob or "deno" in blob:
            return AppError(
                code="js_challenge",
                title="JS Challenge Cozum Sorunu",
                message="Site challenge korumasi nedeniyle format bilgisi cikmadi.",
                detail=detail or message,
                suggestion="Deno ve yt-dlp surumlerini guncelleyin, sonra tekrar deneyin.",
            )
        if "429" in blob or "too many requests" in blob or "rate limit" in blob:
            return AppError(
                code="rate_limited",
                title="Hiz Siniri",
                message="Site gecici olarak cok fazla istek algiladi.",
                detail=detail or message,
                suggestion="Biraz bekleyin, browser/cookie modunu kontrol edin ve sonra tekrar deneyin.",
            )
        if "403" in blob or "forbidden" in blob:
            return AppError(
                code="forbidden",
                title="Erisim Reddedildi",
                message="Sunucu erisimi reddetti. Cookie, bolge veya koruma engeli olabilir.",
                detail=detail or message,
                suggestion="Browser oturumunu, yt-dlp surumunu ve hedef erisimi kontrol edin.",
            )
        if "format is not available" in blob or "only images are available" in blob or "requested format is not available" in blob:
            return AppError(
                code="format_unavailable",
                title="Format Bulunamadi",
                message="Link analiz edildi ama indirilebilir format cikmadi.",
                detail=detail or message,
                suggestion="Gelismis gorunumu acin veya yt-dlp'yi guncelleyip yeniden analiz edin.",
            )
        if "network" in blob or "timed out" in blob or "connection" in blob:
            return AppError(
                code="network_error",
                title="Baglanti Hatasi",
                message="Ag baglantisi veya site erisimi sirasinda hata olustu.",
                detail=detail or message,
                suggestion="Internet baglantisini ve hedef site erisimini kontrol edin.",
            )
        return AppError(
            code="analyze_error",
            title="Analiz Hatasi",
            message=message or "Link analizi basarisiz oldu.",
            detail=detail,
            suggestion="Detayli logu kontrol edin ve gerekirse bagimliliklari guncelleyin.",
        )

    @staticmethod
    def classify_download_error(message: str) -> AppError:
        blob = (message or "").lower()

        if "durduruldu" in blob or "cancel" in blob:
            return AppError(
                code="download_cancelled",
                title="Indirme Durduruldu",
                message="Indirme kullanici tarafindan durduruldu.",
                detail=message,
                suggestion="Gerekirse ayni formatla yeniden deneyin.",
            )
        if "requested format is not available" in blob:
            return AppError(
                code="format_unavailable",
                title="Secilen Format Kullanilamiyor",
                message="Secilen format artik kullanilabilir degil veya eksik akisa bagli.",
                detail=message,
                suggestion="Linki yeniden analiz edin ve farkli bir format secin.",
            )
        if "ffmpeg" in blob and ("not found" in blob or "missing" in blob):
            return AppError(
                code="ffmpeg_missing",
                title="FFmpeg Eksik",
                message="Birlesitirme veya remux icin ffmpeg gerekli ama bulunamadi.",
                detail=message,
                suggestion="Kurulum ekranindan ffmpeg'i kurup tekrar deneyin.",
            )
        if "permission" in blob or "access is denied" in blob:
            return AppError(
                code="write_permission",
                title="Yazma Izni Hatasi",
                message="Cikti klasorune yazma izni yok veya dosya kilitli.",
                detail=message,
                suggestion="Farkli bir cikti klasoru secin ve dosya izinlerini kontrol edin.",
            )
        if "429" in blob or "too many requests" in blob or "rate limit" in blob:
            return AppError(
                code="rate_limited",
                title="Hiz Siniri",
                message="Site indirme tarafinda gecici istek sinirina girdi.",
                detail=message,
                suggestion="Biraz bekleyin ve sonra tekrar deneyin.",
            )
        if "403" in blob or "forbidden" in blob:
            return AppError(
                code="forbidden",
                title="Erisim Reddedildi",
                message="Indirme istegi reddedildi. Yetki veya koruma sorunu olabilir.",
                detail=message,
                suggestion="Browser oturumunu, yt-dlp surumunu ve hedef erisimi kontrol edin.",
            )
        if "network" in blob or "timed out" in blob or "connection" in blob:
            return AppError(
                code="network_error",
                title="Indirme Baglanti Hatasi",
                message="Indirme sirasinda ag baglantisi koptu veya site cevap vermedi.",
                detail=message,
                suggestion="Baglantiyi kontrol edin ve yeniden deneyin.",
            )
        if "login" in blob or "private" in blob or "members only" in blob or "age-restricted" in blob:
            return AppError(
                code="login_required",
                title="Korumali Icerik",
                message="Icerik icin gecerli oturum veya yetki gerekiyor.",
                detail=message,
                suggestion="Secili browser'da oturum acin ve ayni browser ile tekrar deneyin.",
            )
        if "yt-dlp hatasi" in blob:
            return AppError(
                code="yt_dlp_error",
                title="yt-dlp Hatasi",
                message="Indirme yt-dlp tarafinda hata ile sonlandi.",
                detail=message,
                suggestion="yt-dlp surumunu kontrol edin ve log detayina bakin.",
            )
        return AppError(
            code="download_error",
            title="Indirme Hatasi",
            message="Indirme islemi basarisiz oldu.",
            detail=message,
            suggestion="Detayli logu kontrol edin, gerekirse yeniden analiz edip tekrar deneyin.",
        )
