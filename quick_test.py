import requests

try:
    r = requests.post(
        'http://127.0.0.1:8000/api/templates/extract-phrases',
        json={'content': 'test content', 'filename': 'test.md'}
    )
    print('Status:', r.status_code)
    if r.status_code != 200:
        print('Error:', r.text[:500])
    else:
        print('OK')
except Exception as e:
    print('Error:', e)
