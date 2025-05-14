class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class DatabaseError(Error):
    """Exception raised for database-related errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ConfigurationError(Error):
    """Exception raised for configuration-related errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ValidationError(Error):
    """Exception raised for validation-related errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message) 