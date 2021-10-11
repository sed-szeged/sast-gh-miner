class GatherTypeException(Exception):
    def __init__(self, what, correct, given):
        c = correct.__name__
        g = type(given).__name__
        message = f'Gather class. Type of {what} should be `{c}` instead of `{g}`'
        super().__init__(message)