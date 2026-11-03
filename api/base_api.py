import requests

class BaseAPI:
    def __init__(self, config, logger):
        self.base_url = config['base_url']
        self.timeout = config.get('timeout', 10)
        self.session = requests.Session()
        self.log = logger

    def _request(self, method, path, token = None, **kwargs):
        url = f"{self.base_url}{path}"
        headers = kwargs.pop('headers', {})
        if token:
            headers['Cookie'] = f'token={token}'
        self.log.info(f'{method}{url}')
        resp = self.session.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
        self.log.info(f'{resp.status_code}')
        return resp