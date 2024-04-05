import requests

class ApiSession(requests.Session):
    def __init__(self, host, version, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.needs_warning = True
        self.version = version
        self.user_agent = "GigalixirCLI/" + version
        self.host = host

    def request(self, method, url, *args, **kwargs):
        # Add custom headers to all outbound requests
        kwargs.setdefault('headers', {}).update({
            'Content-Type': 'application/json',
            'User-Agent': self.user_agent,
        })
        url = self.host + url
        response = super().request(method, url, *args, **kwargs)

        # Parse response header
        if self.needs_warning:
          self.needs_warning = False
          latest_version = response.headers.get('x-latest-version')
          if latest_version and latest_version != self.version:
              print("Warning: A new version is available.")
              print("  Current version: ", self.version)
              print("  Latest version:  ", latest_version)

        return response
