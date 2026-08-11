import psycopg2
from urllib.parse import urlparse

url = 'postgresql://matumiz_db_user:YcCbxXN6L96YQwWK0Qc9k7hoCeJQPcqN@dpg-d9seajajnfac739biogg-a/matumiz_db'
parsed = urlparse(url)
print('parsed', parsed)
conn = psycopg2.connect(
    dbname=parsed.path.lstrip('/'),
    user=parsed.username,
    password=parsed.password,
    host=parsed.hostname,
    port=parsed.port,
    connect_timeout=5,
)
print('connected')
conn.close()
