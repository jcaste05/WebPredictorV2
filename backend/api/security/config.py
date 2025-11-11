DEFAULT_CSP = "; ".join(
    [
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "base-uri 'none'",
    ]
)

DOCS_CSP = "; ".join(
    [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com",
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://fonts.googleapis.com",
        "img-src 'self' https://cdn.jsdelivr.net https://unpkg.com https://fastapi.tiangolo.com",
        "font-src 'self' https://cdn.jsdelivr.net https://unpkg.com https://fonts.gstatic.com",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "base-uri 'none'",
    ]
)
