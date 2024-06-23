class JSONFrameError(Exception):
    pass

class FileNotFoundError(JSONFrameError):
    pass

class JSONDecodeError(JSONFrameError):
    pass

class MemoryError(JSONFrameError):
    pass
