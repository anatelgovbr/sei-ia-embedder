"""Módulo de extração de documentos externos."""

import logging
import uuid
from pathlib import Path
from xml.etree import ElementTree

import poppler
import requests
from fastapi import HTTPException

from embedder.db_connection.instances import sei_db_instance
from embedder.db_connection.solr_handlers import SolrException, SolrRequests
from embedder.envs import SEI_IAWS_KEY, SEI_IAWS_URL, SEI_SOLR_ADDRESS, SEI_SOLR_CORE
from embedder.http_exceptions import (
    HTTPException204,
    HTTPException404,
    HTTPException406,
    HTTPException408,
    HTTPException409,
    HTTPException500,
    HTTPException503,
)
from embedder.query_templates.solr_template import PROD_SEI_SOLR
from embedder.query_templates.sql_templates import GET_NOME_DOCUMENTO_FROM_ID
from embedder.text_preprocess import pre_processamento_pdf

logger = logging.getLogger(__name__)

ERRO500 = (
    "Erro de conexão ao BD para busca do "
    "conteúdo do documento id {id_documento}."
)


def raise_http_exception(exc_class: Exception, message: str) -> Exception:
    """Função de workaround para erros pylint.

    Esta função centraliza o lançamento de exceções HTTP personalizadas
    e a geração de logs de exceção, permitindo que o código fique mais
    organizado e atenda às regras de estilo pylint, como TRY301.

    Args:
        exc_class (Exception): A classe da exceção HTTP a ser lançada.
        message (str): A mensagem de erro que será registrada no log e
                       associada à exceção.

    Raises:
        exc_class: Lança a exceção especificada pelo argumento `exc_class`.
    """
    logger.exception(message)
    raise exc_class


def get_doc_ext_from_id(
    id_documento: str, pag_ini: int | None = None, pag_fim: int | None = None
) -> str:
    """Extrai o conteúdo textual de um documento a partir de seu ID.

    Parâmetros:
    id_documento (str): Identificador do documento.
    pag_ini (int | None, opcional): Número da página inicial para extração, se aplicável. Padrão é None.
    pag_fim (int | None, opcional): Número da página final para extração, se aplicável. Padrão é None.

    Retorna:
    str: Conteúdo do documento.

    Exceções:
    Exception: Lança uma exceção se ocorrer um erro ao buscar o conteúdo do documento.
    HTTPException404: Lança uma exceção se o documento não for encontrado.
    HTTPException204: Lança uma exceção se o documento não tiver conteúdo.
    HTTPException409: Lança uma exceção se mais de um documento for encontrado para o ID fornecido.
    HTTPException500: Lança uma exceção se ocorrer um erro de conexão ao Solr do SEI.
    """
    logger.debug("entrou em get_doc_ext_from_id")
    if pag_ini or pag_fim:
        logger.debug(f"Foi solicitada a paginação do documento id {id_documento} ([{pag_ini}:{pag_fim}])")
        return get_paged_text_from_id(id_documento, pag_ini, pag_fim)

    try:
        url = PROD_SEI_SOLR.format(
            SEI_SOLR_ADDRESS=SEI_SOLR_ADDRESS,
            SEI_SOLR_CORE=SEI_SOLR_CORE,
            id_documento=id_documento,
        )
        response = SolrRequests.select(url, nested_fields=["response", "docs"])
        l_df = len(response)
        if l_df == 0:
            raise_http_exception(HTTPException404, f"Documento id {id_documento} nao encontrado")
        if l_df == 1:
            if "content" in response[0]:
                text = response[0]["content"][0]
                return pre_processamento_pdf(text)
            raise_http_exception(HTTPException204, f"Documento id {id_documento} está sem conteudo!")
        raise_http_exception(HTTPException409, f"Mais de um documento encontrado para o id {id_documento}!")
    except (
            HTTPException,
            HTTPException204,
            HTTPException404,
            HTTPException408,
            HTTPException409,
            HTTPException503,
            SolrException) as ex:
        logger.exception(
            f"Erro de conexão ao Solr do SEI para busca do conteúdo"
            f" do documento id {id_documento}!"
        )
        raise ex from ex
    except Exception as e:
        logger.exception(
            f"Erro de conexão ao Solr do SEI para busca do conteúdo"
            f" do documento id {id_documento}!"
        )
        raise HTTPException500(
            detail=ERRO500.format(id_documento=id_documento)) from e


def get_paged_text_from_id(id_documento: str, pag_ini: int | None, pag_fim: int | None) -> str:
    """Obtém o conteúdo de um arquivo PDF de um documento a partir do seu ID.

    Parâmetros:
    id_documento (str): Identificador do documento.
    pag_ini (int | None): Número da página inicial para extração. Padrão é None.
    pag_fim (int | None): Número da página final para extração. Padrão é None.

    Retorna:
    str: Texto extraído das páginas indicadas do documento PDF.

    Exceções:
    HTTPException406: Lança uma exceção se a seleção de páginas for solicitada para um documento que não é PDF.
    HTTPException500: Lança uma exceção se ocorrer um erro no processo de buscar e extrair páginas do PDF.
    """
    logger.debug("Entrou em get_paged_text_from_id")
    try:
        nome_documento = get_nome_documento_from_id(id_documento)
        tipo_documento = nome_documento.split(".")
        if len(tipo_documento) <= 1 or tipo_documento[-1].upper() != "PDF":
            msg = f"Documento id {id_documento} não é um PDF!"
            logger.error(msg)
            msg = "Não posso definir um intervalo de páginas para esse documento"
            raise_http_exception(HTTPException406, msg)

        pdf_file = download_pdf(id_documento)
        text = get_text_pdf_from_file(pdf_file, pag_ini, pag_fim)
        Path(pdf_file).unlink()
    except (HTTPException204,
            HTTPException404,
            HTTPException408,
            HTTPException409,
            HTTPException500,
            HTTPException503) as exc:
        logger.exception("Erro ao definir get_paged_text_from_id")
        raise exc from exc
    except HTTPException406 as e:
        msg = "Não posso definir um intervalo de páginas para esse documento"
        raise HTTPException406(detail=msg) from e
    except Exception as e:
        logger.debug(f"Entrou na excecao generica tipo {type(e)} do get_paged_text_from_id {e!s}")
        if "num_documento" not in locals():
            msg = f"Erro ao buscar o número do documento id {id_documento} no SEI!"
        elif "nome_documento" not in locals():
            msg = f"Erro ao buscar o nome do documento id {id_documento} no SEI!"
        elif "pdf_link" not in locals():
            msg = f"Erro ao buscar link do PDF para documento id {id_documento} na API SeiWS!"
        elif "pdf_file" not in locals():
            msg = f"Erro ao baixar o PDF do documento id {id_documento}!"
        else:
            msg = f"Erro ao extrair o conteúdo do PDF do documento id {id_documento}!"
        raise HTTPException500(detail=msg) from e
    else:
        return text


def download_pdf(id_documento: str) -> str:
    """Baixa um arquivo PDF.

    do id do documento no SEI e salva localmente com um nome de arquivo único.

    Args:
        id_documento (str): o id do documento cujo arquivo PDF será baixado.

    Returns:
        str: O nome do arquivo sob o qual o PDF foi salvo localmente se o
            download for bem-sucedido.
             Retorna None se ocorrer alguma falha durante o download.

    Raises:
        requests.RequestException: Levanta uma exceção se a resposta da URL
                                   falhar, indicando problemas como conexão
                                   interrompida ou URL inacessível.

    Example:
        >>> file_name = download_pdf("99999")
        >>> print(file_name)
        "8f14e45fceea167a5a36dedd4bea2543.pdf"
    """
    logger.debug("Entrou em download_pdf")
    try:
        file_name = f"{uuid.uuid4()}.pdf"

        headers = {
            "Content-Type": "text/xml;charset=UTF-8",
            "SOAPAction": "SeiIaAction"
        }

        soap_body = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Header/>
            <soapenv:Body>
                <parametros>
                    <IdentificacaoServico>{SEI_IAWS_KEY}</IdentificacaoServico>
                    <IdDocumento>{id_documento}</IdDocumento>
                    <SiglaSistema>Usuario_IA</SiglaSistema>
                </parametros>
            </soapenv:Body>
        </soapenv:Envelope>
        """

        response = requests.post(SEI_IAWS_URL, data=soap_body, headers=headers, timeout=60)

        content = extract_xml_from_multipart(response.content)
        if content is None:
            msg = f"Erro ao processar XML retornado pela API IaWS para o documento id {id_documento}"
            logger.debug(msg)
            msg = "Erro ao buscar conteúdo do documento."
            raise HTTPException500(detail=msg)  # noqa: TRY301

        # Parse da resposta XML
        root = ElementTree.fromstring(content)  # noqa: S314

        # Extraindo o conteúdo do PDF codificado em base64
        pdf_data = None
        for elem in root.iter():
            if elem.tag.endswith("Include"):
                href = elem.attrib.get("href")
                if href and href.startswith("cid:"):
                    cid = href.split(":", 1)[1]
                    pdf_data = extract_cid_content(response.content, cid)

        if pdf_data is None:
            msg = f"Conteúdo do PDF não encontrado no XML retornado pela API IaWS para o documento id {id_documento}"
            logger.debug(msg)
            msg = "O documento está sem conteúdo."
            raise HTTPException500(detail=msg)  # noqa: TRY301

        # Salvando o arquivo PDF
        with Path(file_name).open("wb") as f:
            f.write(pdf_data)

        logger.debug(f"Arquivo PDF '{file_name}' salvo com sucesso'.")

    except Exception as e:
        logger.debug(f"Entrou na excecao generica tipo {type(e)} do download_pdf {e!s}")
        logger.exception("Erro ao baixar o arquivo.")
        raise requests.RequestException from e
    else:
        return file_name


def extract_xml_from_multipart(response_content: bytes) -> str:
    """Função para extrair o conteúdo XML da resposta multipart."""
    boundary = response_content.split(b"\r\n--")[1].split(b"\r\n")[0].strip()
    parts = response_content.split(b"--" + boundary)

    for part in parts:
        if b"Content-Type: application/xop+xml" in part:
            return part.split(b"\r\n\r\n", 1)[1].rsplit(b"\r\n", 1)[0]

    return None

def extract_cid_content(response_content: str, cid: str) -> str:
    """Função auxiliar para extrair conteúdo do CID da resposta multipart."""
    boundary = response_content.split(b"\r\n--")[1].split(b"\r\n")[0].strip()
    parts = response_content.split(b"--" + boundary)

    for part in parts:
        if f"Content-ID: <{cid}>".encode() in part:
            return part.split(b"\r\n\r\n", 1)[1].split(b"\r\n--")[0]

    return None


def get_nome_documento_from_id(id_documento: str) -> str:
    """Recupera o nome de um documento a partir de seu ID.

    Este método executa uma consulta SQL para obter o nome do documento correspondente
    ao ID fornecido. Se o número do documento não estiver presente, um erro será registrado
    e uma exceção HTTP 204 será levantada.

    Args:
        id_documento (str): O ID do documento do qual se deseja obter o número.

    Returns:
        str: O número do documento associado ao ID fornecido.

    Raises:
        HTTPException204: Exceção lançada se o nome do documento não estiver disponível.
    """
    logger.debug("Entrou em get_nome_documento_from_id")
    sql = GET_NOME_DOCUMENTO_FROM_ID.format(id_documento)
    nome_documento = sei_db_instance.select(sql=sql)
    if not nome_documento["nome_doc"][0]:
        logger.error(f"Nome do documento id {id_documento} está vazio!")
        raise HTTPException204
    return str(nome_documento["nome_doc"][0])

def get_text_pdf_from_file(
    pdf_file: str,
    pag_ini: int | None,
    pag_fim: int | None) -> str:
    """Extrai o texto de um arquivo PDF especificado entre as págs indicadas.

    Args:
    pdf_file (str): Caminho para o arquivo PDF do qual o texto será extraído.
    pag_ini (int): Número da página inicial a partir da qual o texto será
        extraído (1-based index).
    pag_fim (int): Número da página final até onde o texto será extraído
        (inclusive).

    Returns:
    str: Retorna todo o texto extraído das páginas especificadas, processado e
        concatenado em uma única string.

    Raises:
    FileNotFoundError: Se o arquivo PDF não puder ser encontrado no caminho
        especificado.
    ValueError: Se os números de páginas forem inválidos (e.g., pag_ini >
        pag_fim ou valores negativos).

    Note:
    Se pag_ini for 0 ou None, a extração começará da primeira página.
    Se pag_fim for maior que o número de páginas no PDF ou None, a extração
        irá até a última página do documento.
    O texto extraído é também submetido a uma função de pré-processamento
        antes de ser retornado.
    """
    logger.debug("Entrou em get_text_pdf_from_file")
    try:
        pdf = poppler.load_from_file(pdf_file)
        pag_ini = pag_ini - 1 if pag_ini else 0
        if not pag_fim or pag_fim > pdf.pages:
            pag_fim = pdf.pages
        pages = []
        for page_index in range(pag_ini, pag_fim):
            page = pdf.create_page(page_index)
            text = page.text()
            pages.append(text)
        text = "\n".join(pages)
        return pre_processamento_pdf(text)
    except Exception as e:
        logger.debug(f"Entrou na excecao generica tipo {type(e)} do get_text_pdf_from_file {e!s}")
        msg = "Erro ao extrair o texto do PDF!"
        raise Exception(msg) from e  # noqa: TRY002

def check_exist_content_doc_ext_from_id(id_documento: str) -> bool:
    """Checa se existe o conteúdo textual de um documento a partir de seu ID.

    Parâmetros:
    id_documento (str): Identificador do documento.

    Retorna:
    bool: Tem conteúdo?
    """
    url = PROD_SEI_SOLR.format(
        SEI_SOLR_ADDRESS=SEI_SOLR_ADDRESS,
        SEI_SOLR_CORE=SEI_SOLR_CORE,
        id_documento=id_documento,
    )
    response = SolrRequests.select(url.replace(
        "fl=id_prot,content,content_type",
        "fl=id_prot,content_type&hl=on&hl.fl=content&f.content.hl.alternateField=content&f.content.hl.maxAlternateFieldLength=5"))
    l_df = len([v for v in response.get("highlighting").values() if v.get("content")])
    if l_df >= 1:
        return True
    if l_df == 0:
        return False
    