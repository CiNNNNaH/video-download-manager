from __future__ import annotations

from models.app_error import AppError


class ErrorHandler:
    @staticmethod
    def classify_analyze_error(message: str, detail: str = "") -> AppError:
        blob = f"{message} | {detail}".lower()

        if "unsupported url" in blob or "unsupported site" in blob:
            return AppError(
                code="unsupported_url",
                title="Unsupported Link",
                message="This link may not be supported by yt-dlp.",
                detail=detail or message,
                suggestion="Try a different link or update yt-dlp and try again.",
            )
        if "login" in blob or "sign in" in blob or "private" in blob or "members only" in blob:
            return AppError(
                code="login_required",
                title="Login Required",
                message="Valid browser cookies may be required to access this content.",
                detail=detail or message,
                suggestion="Open the link in the selected browser, sign in, and analyze again.",
            )
        if "age-restricted" in blob or "confirm your age" in blob:
            return AppError(
                code="age_gate",
                title="Age Restriction",
                message="This content may require additional authorization because of an age restriction.",
                detail=detail or message,
                suggestion="Sign in with the selected browser and try again using the same browser.",
            )
        if "geo" in blob or "not available in your country" in blob or "this video is not available in your country" in blob:
            return AppError(
                code="geo_blocked",
                title="Regional Restriction",
                message="This content may not be available in your region.",
                detail=detail or message,
                suggestion="Try again with a different access condition.",
            )
        if "cookie" in blob and ("decrypt" in blob or "dpapi" in blob):
            return AppError(
                code="cookie_decrypt",
                title="Cookie Decryption Error",
                message="The selected browser cookie data could not be read or decrypted.",
                detail=detail or message,
                suggestion="Choose another browser or open the link in that browser and try again.",
            )
        if "cookie" in blob:
            return AppError(
                code="cookie_access",
                title="Cookie Access Error",
                message="No valid cookies were obtained from the selected browser.",
                detail=detail or message,
                suggestion="Change the browser selection or enable fallback.",
            )
        if "js challenge" in blob or "n challenge" in blob or "deno" in blob:
            return AppError(
                code="js_challenge",
                title="JS Challenge Resolution Error",
                message="No format information was returned because of site challenge protection.",
                detail=detail or message,
                suggestion="Update Deno and yt-dlp, then try again.",
            )
        if "429" in blob or "too many requests" in blob or "rate limit" in blob:
            return AppError(
                code="rate_limited",
                title="Rate Limit",
                message="The site temporarily detected too many requests.",
                detail=detail or message,
                suggestion="Wait a while, check the browser/cookie mode, and try again.",
            )
        if "403" in blob or "forbidden" in blob:
            return AppError(
                code="forbidden",
                title="Access Denied",
                message="The server denied access. The issue may be cookies, region, or protection.",
                detail=detail or message,
                suggestion="Check the browser session, yt-dlp version, and target access.",
            )
        if "format is not available" in blob or "only images are available" in blob or "requested format is not available" in blob:
            return AppError(
                code="format_unavailable",
                title="Format Not Found",
                message="The link was analyzed but no downloadable format was returned.",
                detail=detail or message,
                suggestion="Open advanced view or update yt-dlp and analyze again.",
            )
        if "network" in blob or "timed out" in blob or "connection" in blob:
            return AppError(
                code="network_error",
                title="Connection Error",
                message="A network or site access error occurred.",
                detail=detail or message,
                suggestion="Check the internet connection and target site access.",
            )
        return AppError(
            code="analyze_error",
            title="Analysis Error",
            message=message or "Link analysis failed.",
            detail=detail,
            suggestion="Check the detailed log and update dependencies if needed.",
        )

    @staticmethod
    def classify_download_error(message: str) -> AppError:
        blob = (message or "").lower()

        if "stopped by the user" in blob or "cancel" in blob or "download stopped" in blob:
            return AppError(
                code="download_cancelled",
                title="Download Stopped",
                message="The download was stopped by the user.",
                detail=message,
                suggestion="Try again with the same format if needed.",
            )
        if "requested format is not available" in blob:
            return AppError(
                code="format_unavailable",
                title="Selected Format Unavailable",
                message="The selected format is no longer available or depends on a missing stream.",
                detail=message,
                suggestion="Analyze the link again and choose a different format.",
            )
        if "ffmpeg" in blob and ("not found" in blob or "missing" in blob):
            return AppError(
                code="ffmpeg_missing",
                title="FFmpeg Missing",
                message="FFmpeg is required for merging or remux but was not found.",
                detail=message,
                suggestion="Install FFmpeg from the setup dialog and try again.",
            )
        if "permission" in blob or "access is denied" in blob:
            return AppError(
                code="write_permission",
                title="Write Permission Error",
                message="There is no write permission for the output folder or the file is locked.",
                detail=message,
                suggestion="Choose a different output folder and check file permissions.",
            )
        if "429" in blob or "too many requests" in blob or "rate limit" in blob:
            return AppError(
                code="rate_limited",
                title="Rate Limit",
                message="The site has temporarily rate-limited download requests.",
                detail=message,
                suggestion="Wait a while and then try again.",
            )
        if "403" in blob or "forbidden" in blob:
            return AppError(
                code="forbidden",
                title="Access Denied",
                message="The download request was rejected. There may be an authorization or protection issue.",
                detail=message,
                suggestion="Check the browser session, yt-dlp version, and target access.",
            )
        if "network" in blob or "timed out" in blob or "connection" in blob:
            return AppError(
                code="network_error",
                title="Download Connection Error",
                message="The network connection dropped during download or the site did not respond.",
                detail=message,
                suggestion="Check the connection and try again.",
            )
        if "login" in blob or "private" in blob or "members only" in blob or "age-restricted" in blob:
            return AppError(
                code="login_required",
                title="Protected Content",
                message="This content requires a valid session or authorization.",
                detail=message,
                suggestion="Sign in with the selected browser and try again using the same browser.",
            )
        if "yt-dlp error" in blob or "yt-dlp hatasi" in blob:
            return AppError(
                code="yt_dlp_error",
                title="yt-dlp Error",
                message="The download ended with a yt-dlp error.",
                detail=message,
                suggestion="Check the yt-dlp version and review the log details.",
            )
        return AppError(
            code="download_error",
            title="Download Error",
            message="The download operation failed.",
            detail=message,
            suggestion="Check the detailed log, analyze again if needed, and retry.",
        )
