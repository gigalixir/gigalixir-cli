class ApiException(Exception):
    def __init__(self, response):
        if response.status_code == 404:
            self._rollbar_ignore = True
        message = response.text
        super(ApiException, self).__init__(message)
