class ServiceError(Exception):
    pass


class ImageProcessingError(ServiceError):
    pass


class FileStorageError(ServiceError):
    pass
