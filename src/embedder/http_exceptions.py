"""Modulo de excecoes da API."""
from fastapi import HTTPException


class HTTPException204(HTTPException):
    """Excecao para o codigo 204.

    Args:
        HTTPException (Exception): Documento sem conteudo
    """

    def __init__(
            self,
            status_code: int = 204,
            detail: str = "Documento sem conteudo") -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 204.
            detail (str, optional): The detail message for the exception.
                Defaults to "Documento sem conteudo".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


class HTTPException400(HTTPException):
    """Exceção para o código 400.

    Args:
        HTTPException (Exception): Bad Request - Não possui numero de documento
    """

    def __init__(
            self,
            status_code: int = 400,
            detail: str = "Bad Request - Não possui numero de documento",
    ) -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 400.
            detail (str, optional): The detail message for the exception.
                Defaults to "Bad Request - Não possui numero de documento".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


class HTTPException401(HTTPException):
    """Exceção para o código 401.

    Args:
        HTTPException (Exception): Falta chave para GPT
    """

    def __init__(
            self,
            status_code: int = 401,
            detail: str = "Falta chave(s) no config.json"
    ) -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 401.
            detail (str, optional): The detail message for the exception.
                Defaults to "Falta chave para GPT".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


class HTTPException404(HTTPException):
    """Exceção para o código 404.

    Args:
        HTTPException (Exception): Documento nao encontrado
    """

    def __init__(
            self,
            status_code: int = 404,
            detail: str = "Documento nao encontrado"
    ) -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 404.
            detail (str, optional): The detail message for the exception.
                Defaults to "Documento nao encontrado".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


class HTTPException406(HTTPException):
    """Exceção para o código 406.

    Args:
        HTTPException (Exception): Documento nao encontrado
    """

    def __init__(
            self,
            status_code: int = 406,
            detail: str = "Documento nao aceitavel"
    ) -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 406.
            detail (str, optional): The detail message for the exception.
                Defaults to "Documento nao aceitavel".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


class HTTPException408(HTTPException):
    """Exceção para o código 408.

    Args:
        HTTPException (Exception): Error: Request Timeout
    """

    def __init__(
            self,
            status_code: int = 408,
            detail: str = "Error: Request Timeout"
    ) -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 408.
            detail (str, optional): The detail message for the exception.
                Defaults to "Error: Request Timeout".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


class HTTPException409(HTTPException):
    """Exceção para o código 409.

    Args:
        HTTPException (Exception): Mais de um documento encontrado
    """

    def __init__(
            self,
            status_code: int = 409,
            detail: str = "Mais de um documento encontrado"
    ) -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 409.
            detail (str, optional): The detail message for the exception.
                Defaults to "Mais de um documento encontrado".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)



class HTTPException413(HTTPException):
    """Exceção para o código 413.

    Args:
        HTTPException (Exception): Texto muito longo
    """

    def __init__(
            self,
            status_code: int = 413,
            detail: str = "Texto muito longo") -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 413.
            detail (str, optional): The detail message for the exception.
                Defaults to "Texto muito longo".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


class HTTPException422(HTTPException):
    """Exceção para o código 422.

    Args:
        HTTPException (Exception): Texto no formato incorreto
    """

    def __init__(
            self,
            status_code: int = 422,
            detail: str = "Texto no formato incorreto"
    ) -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 422.
            detail (str, optional): The detail message for the exception.
                Defaults to "Texto no formato incorreto".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


class HTTPException429(HTTPException):
    """Exceção para o código 429.

    Args:
        HTTPException (Exception): Erro de rate limit na api version
    """

    def __init__(
            self,
            status_code: int = 429,
            detail: str = "Erro de rate limit na api version"
    ) -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 429.
            detail (str, optional): The detail message for the exception.
                Defaults to "Erro de rate limit na api version".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


class HTTPException500(HTTPException):
    """Exceção para o código 500.

    Args:
        HTTPException (Exception): Erro interno do servidor
    """

    def __init__(
            self,
            status_code: int = 500,
            detail: str = "Internal Server Error") -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 500.
            detail (str, optional): The detail message for the exception.
                Defaults to "Internal Server Error".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


class HTTPException501(HTTPException):
    """Exceção para o código 501.

    Args:
        HTTPException (Exception): Refine summary not implemented
    """

    def __init__(
            self,
            status_code: int = 501,
            detail: str = "Refine summary not implemented"
    ) -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 501.
            detail (str, optional): The detail message for the exception.
                Defaults to "Refine summary not implemented".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


class HTTPException503(HTTPException):
    """Exceção para o código 503.

    Args:
        HTTPException (Exception): Error: Service Unavailable
    """

    def __init__(
            self,
            status_code: int = 503,
            detail: str = "Error: Service Unavailable"
    ) -> None:
        """Initializes the class with the given status code and detail message.

        Args:
            status_code (int, optional): The HTTP status code for the
                exception. Defaults to 503.
            detail (str, optional): The detail message for the exception.
                Defaults to "Error: Service Unavailable".

        Returns:
            None
        """
        super().__init__(status_code=status_code, detail=detail)


fast_api_responses = {
    204: {"description": "Documento sem conteúdo"},
    400: {"description": "Bad Request - Não possui numero de documento"},
    401: {"description": "Falta chave para GPT"},
    404: {"description": "Documento não encontrado"},
    406: {"description": "Documento não aceitável para seleção de páginas"},
    408: {"description": "timeout interno"},
    409: {"description": "Mais de um documento encontrado"},
    413: {"description": "Texto muito longo"},
    422: {"description": "Texto no formato incorreto"},
    429: {"description": "Erro de rate limit na api version"},
    500: {"description": "Internal Server Error"},
    501: {"description": "Refine summary not implemented"},
    503: {"description": "Error: Service Unavailable"},
    504: {"description": "Timeout"},
}
