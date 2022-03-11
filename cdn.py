import json

from urllib.request import build_opener, HTTPHandler, Request
from urllib.parse import urlencode


class CDNAPIError(OSError):
    def __init__(self, **kwargs):
        """Use kwargs for logs"""
        self.errors = kwargs
        super().__init__()

    def __str__(self):
        return f"CDN API Error {json.dumps(self.errors)}"


class CDN():
    def __init__(
            self,
            username,
            password,
            account_name,
            url):

        self.username = username
        self.password = password
        self.account_name = account_name
        self.url = url
        self.token = ''

    def get_resource(self):
        api_path = f'cdn/api/v1/{self.account_name}/resource/http/'
        result = self.make_request(api_path)
        if ("status" in result) and (result["status"] == "error"):
            raise CDNAPIError(path=api_path, **result)
        return result

    def get_realtimestat(self):
        api_path = f'app/realtimestat/v1/accounts/{self.account_name}/resources'
        return self.make_request(api_path)

    def refresh_token(self):
        api_path = 'app/oauth/v1/token/'

        params = {}
        params['username'] = self.username
        params['password'] = self.password

        data = self.make_request(api_path, params, method='POST')

        self.token = data['token']

    def make_request(
            self,
            api_path,
            params=None,
            method='GET'):

        fullurl = f'{self.url}/{api_path}'

        headers = []
        if api_path != 'app/oauth/v1/token/':
            if not self.token:
                self.refresh_token()
            headers = [ ('cdn-auth-token', self.token) ]

        data = None
        if params:
            params_encoded = urlencode(params, doseq=1)
            if method == 'POST':
                data = params_encoded.encode('utf-8')
            else:
                fullurl = f'{fullurl}?{params_encoded}'

        opener = build_opener(HTTPHandler())
        opener.addheaders = headers

        request = Request(fullurl, data=data, method=method)

        response = opener.open(request)
        result = response.read().decode('utf-8')
        return json.loads(result)
