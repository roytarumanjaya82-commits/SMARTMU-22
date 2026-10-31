from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pengaturan import SECRET_KEY

COOKIE = "smartmu_sso"
UMUR = 60 * 60 * 12
_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="smartmu-sso")


def buat(data):
    return _serializer.dumps(data)


def baca(request):
    token = request.cookies.get(COOKIE, "")
    if not token:
        return None
    try:
        data = _serializer.loads(token, max_age=UMUR)
    except (BadSignature, SignatureExpired):
        return None
    if not isinstance(data, dict) or not data.get("username"):
        return None
    return data


def pasang(response, data):
    response.set_cookie(
        COOKIE,
        buat(data),
        max_age=UMUR,
        httponly=True,
        samesite="Lax",
        path="/",
    )
    return response


def hapus(response):
    response.delete_cookie(COOKIE, path="/")
    return response
