class AuthException(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        message = "Sorry, you do not have access. Try running gigalixir login or checking your ~/.netrc file."
        super(AuthException, self).__init__(message)
