class DevFlowException(Exception):
    pass

class AutomationNotFoundException(DevFlowException):
    pass

class AutomationError(DevFlowException):
    pass

class CommandError(DevFlowException):
    def __init__(self, command: str, message: str):
        super().__init__(message)
        self.command = command

class ParameterError(DevFlowException):
    pass

class StorageError(DevFlowException):
    pass

class ExecutionError(DevFlowException):
    def __init__(self, command: str, exit_code: int, message: str):
        super().__init__(message)
        self.command = command
        self.exit_code = exit_code