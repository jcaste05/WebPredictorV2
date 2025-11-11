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

DOCS_CSP = "; ".join([
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
    "img-src 'self' https://cdn.jsdelivr.net",
    "font-src 'self' https://cdn.jsdelivr.net",
    "object-src 'none'",
    "frame-ancestors 'none'",
    "base-uri 'none'",
])
