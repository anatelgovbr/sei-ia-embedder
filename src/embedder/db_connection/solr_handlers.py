"""Module for connecting with Solr."""
import logging

import requests
from fastapi import HTTPException
from requests.exceptions import ConnectionError, JSONDecodeError, Timeout

logger = logging.getLogger(__name__)

HTTP_OK = 200
HTTP_NOT_FOUND = 404


class ResourceNotFoundException(HTTPException):
    """Exception raised when a Solr index does not contain an ID."""


class JsonFieldException(HTTPException):
    """Exception raised when a Solr index does not contain an ID."""


class SolrException(HTTPException):
    """Exception raised when Solr is not working."""


class RowsNotFoundException(HTTPException):
    """Exception raised when a Solr index does not contain an ID."""


class FieldInURLException(HTTPException):
    """Exception raised when a Solr index does not contain an ID."""


class SolrRequests:
    """modulo de request do solr."""
    @staticmethod
    def check_solr_service(solr_url: str) -> bool | None:
        """Check if the Solr service is available."""
        try:
            response = requests.get(solr_url, timeout=10)
            return bool(
                response.status_code == HTTP_OK and
                "Apache SOLR" in response.text)
        except requests.RequestException as ex:
            logger.warning(ex)
            return False

    @staticmethod
    def check_core_exists(solr_url: str, core_name: str) -> bool:
        """Check if a Solr core exists."""
        core_status_url = f"{solr_url}/solr/{core_name}/admin/ping"
        try:
            response = requests.get(core_status_url, timeout=10)
        except requests.RequestException as ex:
            logger.warning(ex)
            return False
        return response.status_code == HTTP_OK

    @staticmethod
    def post(
        url: str,
        payload: dict,
        headers: dict | None = None,
        nested_fields: list | None = None,
        timeout: int = 60,
    ) -> str:
        """Perform a POST request to Solr."""
        headers = headers or {
            "Content-Type": "application/json; charset=utf-8"}
        nested_fields = nested_fields or []
        try:
            http_response = requests.post(
                url=url, json=payload, headers=headers, timeout=timeout
            )
        except ConnectionError as exc:
            raise SolrException(status_code=503, detail=str(exc)) from exc
        except Timeout as exc:
            raise SolrException(status_code=504, detail=str(exc)) from exc
        return SolrRequests.retrieve_response(http_response, nested_fields)

    @staticmethod
    def select(
        url: str,
        nested_fields: list | None = None,
        timeout: int = 60,
        params: dict | None = None,
    ) -> str:
        """Perform a SELECT request to Solr."""
        nested_fields = nested_fields or []
        try:
            if params:
                http_response = requests.get(
                    url=url, params=params, timeout=timeout)
            else:
                http_response = requests.get(url=url, timeout=timeout)
        except ConnectionError as exc:
            raise SolrException(status_code=503, detail=str(exc)) from exc
        except Timeout as exc:
            raise SolrException(status_code=504, detail=str(exc)) from exc
        return SolrRequests.retrieve_response(http_response, nested_fields)

    @staticmethod
    def retrieve_response(http_response: str, nested_fields: list) -> str:
        """Retrieve and process the HTTP response from Solr."""
        if isinstance(http_response, HTTPException):
            raise SolrException(
                status_code=503, detail=str(http_response)
            ) from http_response
        if not (
            hasattr(http_response, "status_code")
            and hasattr(http_response, "text")
        ):
            raise SolrException(
                status_code=500,
                detail="http_response must have the attributes: "
                "status_code and text",
            )
        if not (hasattr(http_response, "json")
                and callable(http_response.json)):
            raise SolrException(
                status_code=500, detail="http_response must have the method"
                " json()"
            )
        if http_response.status_code == HTTP_NOT_FOUND:
            raise SolrException(
                status_code=404,
                detail="URL de comunicacao com o Solr nao encontrado",
            )
        if http_response.status_code != HTTP_OK:
            raise SolrException(
                status_code=http_response.status_code,
                detail=http_response.text
            )
        try:
            requests_json = http_response.json()
        except JSONDecodeError as exc:
            raise SolrException(status_code=503, detail=str(exc)) from exc
        ret = requests_json
        for field in nested_fields:
            try:
                ret = ret[field]
            except (IndexError, KeyError, TypeError) as exc:
                raise JsonFieldException(status_code=503, field=field) from exc
        return ret
