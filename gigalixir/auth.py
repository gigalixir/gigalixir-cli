class AuthException(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        message = "Sorry, you do not have access to that app. Try passing the app name explicitly with the `-a` flag. If that doesn't work, try running `gigalixir login` or check your ~/.netrc file."
        super(AuthException, self).__init__(message)
