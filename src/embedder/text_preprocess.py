"""Processamento de textos."""
import logging
import re  # Para trabalhar com expressões regulares

import pandas as pd
import tiktoken
from bs4 import BeautifulSoup  # Para processar dados HTML

logger = logging.getLogger(__name__)

encoder = tiktoken.get_encoding("cl100k_base")

# Listas de Números Romanos e de Letras fora das funções
ROMAN_NUMERALS = [
        "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI",
        "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
        "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII",
        "XXIX", "XXX", "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV", "XXXVI",
        "XXXVII", "XXXVIII", "XXXIX", "XL", "XLI", "XLII", "XLIII", "XLIV",
        "XLV", "XLVI", "XLVII", "XLVIII", "XLIX", "L", "LI", "LII", "LIII",
        "LIV", "LV", "LVI", "LVII", "LVIII", "LIX", "LX", "LXI", "LXII",
        "LXIII", "LXIV", "LXV", "LXVI", "LXVII", "LXVIII", "LXIX", "LXX",
        "LXXI", "LXXII", "LXXIII", "LXXIV", "LXXV", "LXXVI", "LXXVII",
        "LXXVIII", "LXXIX", "LXXX", "LXXXI", "LXXXII", "LXXXIII", "LXXXIV",
        "LXXXV", "LXXXVI", "LXXXVII", "LXXXVIII", "LXXXIX", "XC", "XCI",
        "XCII", "XCIII", "XCIV", "XCV", "XCVI", "XCVII", "XCVIII", "XCIX",
        "C", "CI", "CII", "CIII", "CIV", "CV", "CVI", "CVII", "CVIII", "CIX",
        "CX", "CXI", "CXII", "CXIII", "CXIV", "CXV", "CXVI", "CXVII", "CXVIII",
        "CXIX", "CXX", "CXXI", "CXXII", "CXXIII", "CXXIV", "CXXV", "CXXVI",
        "CXXVII", "CXXVIII", "CXXIX", "CXXX", "CXXXI", "CXXXII", "CXXXIII",
        "CXXXIV", "CXXXV", "CXXXVI", "CXXXVII", "CXXXVIII", "CXXXIX", "CXL",
        "CXLI", "CXLII", "CXLIII", "CXLIV", "CXLV", "CXLVI", "CXLVII",
        "CXLVIII", "CXLIX", "CL", "CLI", "CLII", "CLIII", "CLIV", "CLV", "CLVI", "CLVII",
        "CLVIII", "CLIX", "CLX", "CLXI", "CLXII", "CLXIII", "CLXIV", "CLXV",
        "CLXVI", "CLXVII", "CLXVIII", "CLXIX", "CLXX", "CLXXI", "CLXXII",
        "CLXXIII", "CLXXIV", "CLXXV", "CLXXVI", "CLXXVII", "CLXXVIII", "CLXXIX", "CLXXX",
        "CLXXXI", "CLXXXII", "CLXXXIII", "CLXXXIV", "CLXXXV", "CLXXXVI", "CLXXXVII",
        "CLXXXVIII", "CLXXXIX", "CXC", "CXCI", "CXCII", "CXCIII", "CXCIV", "CXCV", "CXCVI",
        "CXCVII", "CXCVIII", "CXCIX", "CC"]
LETTERS = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
    "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "aa", "ab",
    "ac", "ad", "ae", "af", "ag", "ah", "ai", "aj", "ak", "al", "am", "an",
    "ao", "ap", "aq", "ar", "as", "at", "au", "av", "aw", "ax", "ay", "az",
    "ba", "bb", "bc", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bk", "bl",
    "bm", "bn", "bo", "bp", "bq", "br", "bs", "bt", "bu", "bv", "bw", "bx",
    "by", "bz", "ca", "cb", "cc", "cd", "ce", "cf", "cg", "ch", "ci", "cj",
    "ck", "cl", "cm", "cn", "co", "cp", "cq", "cr", "cs", "ct", "cu", "cv",
    "cw", "cx", "cy", "cz", "da", "db", "dc", "dd", "de", "df", "dg", "dh",
    "di", "dj", "dk", "dl", "dm", "dn", "do", "dp", "dq", "dr", "ds", "dt",
    "du", "dv", "dw", "dx", "dy", "dz"]


# Função para processar os filhos de um elemento HTML e converter para Markdown
def process_children(tag: str) -> str:
    """Função para proc os filhos de um elemento HTML e converter Markdown.

    Args:
        tag (_type_): _description_

    Returns:
        _type_: _description_
    """
    content = ""
    for child in tag.children:
        # Verificando se o filho é uma tag <br /> e substituindo por uma
        # quebra de linha no Markdown
        if child.name == "br":
            content += "\n"
        # Se o filho for uma string, simplesmente adicione ao conteúdo
        elif child.name is None:
            content += child.string
        # Para outras tags, obtenha seu texto
        else:
            content += child.get_text()
    return content


def process_item_nivel(
        markdown: str,
        element: str,
        counters: tuple | list
        ) -> tuple:
    """Funcao de processamento de item nivel.

    Args:
        markdown (str): conteudo markdown ja formatado
        element (str): Elemento css
        counters (tuple|list): contadores

    Returns:
        tuple: markdown, counters
    """
    (
        level1_counter,
        level2_counter,
        level3_counter,
        level4_counter,
        paragrafo_num1_counter,
        paragrafo_num2_counter,
        paragrafo_num3_counter,
        paragrafo_num4_counter,
        roman_counter,
        letter_counter,
    ) = counters
    if "Item_Nivel1" in element.get("class"):
        level1_counter += 1
        (level2_counter, level3_counter, level4_counter, roman_counter) = (
            0, 0, 0, 0,
        )
        markdown += (
            f"# **{level1_counter}. {process_children(element).upper()}"
            "**\n\n"
        )
    elif "Item_Nivel2" in element.get("class"):
        level2_counter += 1
        (level3_counter, level4_counter, roman_counter) = (0, 0, 0)
        markdown += (
            f"{level1_counter}.{level2_counter}."
            f" {process_children(element)}\n\n"
        )
    elif "Item_Nivel3" in element.get("class"):
        level3_counter += 1
        (level4_counter, roman_counter) = (0, 0)
        markdown += (f"{level1_counter}.{level2_counter}.{level3_counter}."
                     f" {process_children(element)}\n\n")
    elif "Item_Nivel4" in element.get("class"):
        level4_counter += 1
        (roman_counter) = 0
        markdown += (f"{level1_counter}.{level2_counter}."
                     f"{level3_counter}.{level4_counter}. "
                     f"{process_children(element)}\n\n")
    counters = (
        level1_counter,
        level2_counter,
        level3_counter,
        level4_counter,
        paragrafo_num1_counter,
        paragrafo_num2_counter,
        paragrafo_num3_counter,
        paragrafo_num4_counter,
        roman_counter,
        letter_counter,
    )
    return markdown, counters


def process_pagragrafo_numerado(
        markdown: str,
        element: str,
        counters: tuple | list
        ) -> tuple:
    """Funcao de processamento de paragrafo numerado.

    Args:
        markdown (str): conteudo markdown ja formatado
        element (str): Elemento css
        counters (tuple): contadores

    Returns:
        tuple: markdown, counters
    """
    (
        level1_counter,
        level2_counter,
        level3_counter,
        level4_counter,
        paragrafo_num1_counter,
        paragrafo_num2_counter,
        paragrafo_num3_counter,
        paragrafo_num4_counter,
        roman_counter,
        letter_counter,
    ) = counters
    if "Paragrafo_Numerado_Nivel1" in element.get("class"):
        paragrafo_num1_counter += 1
        (
            paragrafo_num2_counter,
            paragrafo_num3_counter,
            paragrafo_num4_counter,
            roman_counter,
        ) = (0, 0, 0, 0)
        markdown += (f"{paragrafo_num1_counter}."
                     f" {process_children(element)}\n\n")
    elif "Paragrafo_Numerado_Nivel2" in element.get("class"):
        paragrafo_num2_counter += 1
        (paragrafo_num3_counter, paragrafo_num4_counter, roman_counter) = (
            0, 0, 0)
        markdown += (f"{paragrafo_num1_counter}.{paragrafo_num2_counter}."
                     f" {process_children(element)}\n\n")
    elif "Paragrafo_Numerado_Nivel3" in element.get("class"):
        paragrafo_num3_counter += 1
        (paragrafo_num4_counter, roman_counter) = (0, 0)
        markdown += (f"{paragrafo_num1_counter}.{paragrafo_num2_counter}."
                     f"{paragrafo_num3_counter}."
                     f" {process_children(element)}\n\n")
    elif "Paragrafo_Numerado_Nivel4" in element.get("class"):
        paragrafo_num4_counter += 1
        (roman_counter) = 0
        markdown += (f"{paragrafo_num1_counter}.{paragrafo_num2_counter}."
                     f"{paragrafo_num3_counter}.{paragrafo_num4_counter}."
                     f" {process_children(element)}\n\n")
    counters = (
        level1_counter,
        level2_counter,
        level3_counter,
        level4_counter,
        paragrafo_num1_counter,
        paragrafo_num2_counter,
        paragrafo_num3_counter,
        paragrafo_num4_counter,
        roman_counter,
        letter_counter)
    return markdown, counters


def process_romanos(
        markdown: str,
        element: str,
        counters: tuple | list,
        roman_numerals: list,
        ) -> tuple:
    """Funcao de processamento de paragrafo numerado.

    Args:
        markdown (str): conteudo markdown ja formatado
        element (str): Elemento css
        counters (tuple): contadores
        roman_numerals (list): lista de algarismos romanos

    Returns:
        tuple: markdown, counters
    """
    (
        level1_counter,
        level2_counter,
        level3_counter,
        level4_counter,
        paragrafo_num1_counter,
        paragrafo_num2_counter,
        paragrafo_num3_counter,
        paragrafo_num4_counter,
        roman_counter,
        letter_counter,
    ) = counters
    if "Item_Inciso_Romano" in element.get("class"):
        roman_counter += 1
        roman_numeral = (
            roman_numerals[roman_counter - 1]
            if roman_counter <= len(roman_numerals)
            else str(roman_counter)
        )
        markdown += f"{roman_numeral} - {process_children(element)}\n\n"
    counters = (
        level1_counter,
        level2_counter,
        level3_counter,
        level4_counter,
        paragrafo_num1_counter,
        paragrafo_num2_counter,
        paragrafo_num3_counter,
        paragrafo_num4_counter,
        roman_counter,
        letter_counter)
    return markdown, counters


def process_others(
        markdown: str,
        element: str,
        counters: tuple | list,
        letters: list
        ) -> tuple:
    """Funcao de processamento de paragrafo numerado.

    Args:
        markdown (str): conteudo markdown ja formatado
        element (str): Elemento css
        counters (tuple): contadores
        letters (list): lista de letras

    Returns:
        tuple: markdown, counters
    """
    (
        level1_counter,
        level2_counter,
        level3_counter,
        level4_counter,
        paragrafo_num1_counter,
        paragrafo_num2_counter,
        paragrafo_num3_counter,
        paragrafo_num4_counter,
        roman_counter,
        letter_counter,
    ) = counters
    if "Item_Alinea_Letra" in element.get("class"):
        letter_counter += 1
        letter = (
            letters[letter_counter - 1]
            if letter_counter <= len(letters)
            else chr(96 + letter_counter)
        )
        markdown += f"{letter}) {process_children(element)}\n\n"
    # Tratando parágrafos com classe de Citação
    elif "Citacao" in element.get("class"):
        markdown += f"```markdown\n{process_children(element)}\n```\n\n"
    # Tratando parágrafos com classes que força o texto em maiúsculo com
    # negrito
    elif any(
        cls in element.get("class")
        for cls in [
            "Texto_Centralizado_Maiusculas_Negrito",
            "Texto_Fundo_Cinza_Maiusculas_Negrito",
        ]
    ):
        markdown += f"**{process_children(element).upper()}**\n\n"
    # Tratando parágrafos com classes que força o texto em maiúsculo
    elif any(
        cls in element.get("class")
        for cls in [
            "Texto_Alinhado_Esquerda_Espacamento_Simples_Maiusc",
            "Texto_Centralizado_Maiusculas",
            "Texto_Justificado_Maiusculas",
        ]
    ):
        markdown += f"{process_children(element).upper()}\n\n"
    # Tratando parágrafos com classes que força o texto em negrito
    elif "Texto_Fundo_Cinza_Negrito" in element.get("class"):
        markdown += f"**{process_children(element)}**\n\n"
    else:
        markdown += process_children(element) + "\n\n"
    counters = (
        level1_counter,
        level2_counter,
        level3_counter,
        level4_counter,
        paragrafo_num1_counter,
        paragrafo_num2_counter,
        paragrafo_num3_counter,
        paragrafo_num4_counter,
        roman_counter,
        letter_counter)
    return markdown, counters


def process_paragraph(  # noqa: C901, PLR0912, PLR0915
        element: any,
        counters: tuple,
        roman_numerals: list,
        letters: list) -> str:
    """Função para processar parágrafos HTML e convertê-los em Markdown.

    aplicando formatações específicas com base nas classes CSS.

    Args:
        element (_type_): elementos
        counters (_type_): contadores
        roman_numerals (list): lista com numeros romanos
        letters (list): lista com letras

    Returns:
        str: String markdown
    """
    # Inicializando a string Markdown e contadores para formatação estruturada
    markdown = ""
    (
        level1_counter,
        level2_counter,
        level3_counter,
        level4_counter,
        paragrafo_num1_counter,
        paragrafo_num2_counter,
        paragrafo_num3_counter,
        paragrafo_num4_counter,
        roman_counter,
        letter_counter,
    ) = counters

    # Processamento para diferentes tipos de parágrafos com base nas
    # classes CSS
    paragraph_class = element.get("class")
    if paragraph_class:
        # Resetando o contador de 'Item_Alinea_Letra' conforme necessário
        if any(
            cls in paragraph_class
            for cls in [
                "Item_Nivel1",
                "Item_Nivel2",
                "Item_Nivel3",
                "Item_Nivel4",
                "Paragrafo_Numerado_Nivel1",
                "Paragrafo_Numerado_Nivel2",
                "Paragrafo_Numerado_Nivel3",
                "Paragrafo_Numerado_Nivel4",
                "Item_Inciso_Romano",
            ]
        ):
            letter_counter = 0

        # Tratando parágrafos com classes Item_Nivel1 a Item_Nivel4
        if "Item_Nivel1" in paragraph_class:
            level1_counter += 1
            (level2_counter, level3_counter, level4_counter, roman_counter) = (
                0,
                0,
                0,
                0,
            )
            markdown += (
                f"# **{level1_counter}. {process_children(element).upper()}**\n\n"
            )
        elif "Item_Nivel2" in paragraph_class:
            level2_counter += 1
            (level3_counter, level4_counter, roman_counter) = (0, 0, 0)
            markdown += (
                f"{level1_counter}.{level2_counter}. {process_children(element)}\n\n"
            )
        elif "Item_Nivel3" in paragraph_class:
            level3_counter += 1
            (level4_counter, roman_counter) = (0, 0)
            markdown += f"{level1_counter}.{level2_counter}.{level3_counter}. {process_children(element)}\n\n"
        elif "Item_Nivel4" in paragraph_class:
            level4_counter += 1
            (roman_counter) = 0
            markdown += (f"{level1_counter}.{level2_counter}.{level3_counter}"
                         f".{level4_counter}. {process_children(element)}\n\n")
        # Tratando parágrafos com classes Paragrafo_Numerado_Nivel1 a
        # Paragrafo_Numerado_Nivel4
        elif "Paragrafo_Numerado_Nivel1" in paragraph_class:
            paragrafo_num1_counter += 1
            (
                paragrafo_num2_counter,
                paragrafo_num3_counter,
                paragrafo_num4_counter,
                roman_counter,
            ) = (0, 0, 0, 0)
            markdown += f"{paragrafo_num1_counter}. {process_children(element)}\n\n"
        elif "Paragrafo_Numerado_Nivel2" in paragraph_class:
            paragrafo_num2_counter += 1
            (paragrafo_num3_counter, paragrafo_num4_counter, roman_counter) = (0, 0, 0)
            markdown += f"{paragrafo_num1_counter}.{paragrafo_num2_counter}. {process_children(element)}\n\n"
        elif "Paragrafo_Numerado_Nivel3" in paragraph_class:
            paragrafo_num3_counter += 1
            (paragrafo_num4_counter, roman_counter) = (0, 0)
            markdown += (f"{paragrafo_num1_counter}.{paragrafo_num2_counter}."
                         f"{paragrafo_num3_counter}. {process_children(element)}\n\n")
        elif "Paragrafo_Numerado_Nivel4" in paragraph_class:
            paragrafo_num4_counter += 1
            (roman_counter) = 0
            markdown += (f"{paragrafo_num1_counter}.{paragrafo_num2_counter}."
                         f"{paragrafo_num3_counter}.{paragrafo_num4_counter}. {process_children(element)}\n\n")
        # Tratamento de listas romano
        elif "Item_Inciso_Romano" in paragraph_class:
            roman_counter += 1
            roman_numeral = (
                roman_numerals[roman_counter - 1]
                if roman_counter <= len(roman_numerals)
                else str(roman_counter)
            )
            markdown += f"{roman_numeral} - {process_children(element)}\n\n"
        # Tratamento de listas alfabéticas
        elif "Item_Alinea_Letra" in paragraph_class:
            letter_counter += 1
            letter = (
                letters[letter_counter - 1]
                if letter_counter <= len(letters)
                else chr(96 + letter_counter)
            )
            markdown += f"{letter}) {process_children(element)}\n\n"
        # Tratando parágrafos com classe de Citação
        elif "Citacao" in paragraph_class:
            markdown += f"```markdown\n{process_children(element)}\n```\n\n"
        # Tratando parágrafos com classes que força o texto em maiúsculo com
        # negrito
        elif any(
            cls in paragraph_class
            for cls in [
                "Texto_Centralizado_Maiusculas_Negrito",
                "Texto_Fundo_Cinza_Maiusculas_Negrito",
            ]
        ):
            markdown += f"**{process_children(element).upper()}**\n\n"
        # Tratando parágrafos com classes que força o texto em maiúsculo
        elif any(
            cls in paragraph_class
            for cls in [
                "Texto_Alinhado_Esquerda_Espacamento_Simples_Maiusc",
                "Texto_Centralizado_Maiusculas",
                "Texto_Justificado_Maiusculas",
            ]
        ):
            markdown += f"{process_children(element).upper()}\n\n"
        # Tratando parágrafos com classes que força o texto em negrito
        elif "Texto_Fundo_Cinza_Negrito" in paragraph_class:
            markdown += f"**{process_children(element)}**\n\n"
        else:
            markdown += process_children(element) + "\n\n"
    else:
        markdown += process_children(element) + "\n\n"

    # Atualizando os contadores
    counters = [
        level1_counter,
        level2_counter,
        level3_counter,
        level4_counter,
        paragrafo_num1_counter,
        paragrafo_num2_counter,
        paragrafo_num3_counter,
        paragrafo_num4_counter,
        roman_counter,
        letter_counter,
    ]
    return markdown, counters


def process_table(element: str) -> str:
    """Definindo uma função para processar tabelas HTML para  Markdown."""
    # Verificando a existência de células mescladas
    if any(
        cell.has_attr("rowspan") or cell.has_attr("colspan")
        for cell in element.find_all(["th", "td"])
    ):
        return str(element)  # Retorna o HTML original da tabela
    markdown = ""
    rows = element.find_all("tr")
    for i, row in enumerate(rows):
        row_markdown = "|"
        for cell in row.find_all(["th", "td"]):
            cell_content = process_children(cell).strip()  # Processa
            # o conteúdo da célula
            if not cell_content:  # Substitui conteúdo vazio por espaço simples
                cell_content = " "
            row_markdown += f" {cell_content} |"
        markdown += row_markdown + "\n"
        # Adicionando a linha de separação após a primeira linha (cabeçalho)
        if i == 0:  # A primeira linha é tratada como cabeçalho
            markdown += "|---" * len(row.find_all(["th", "td"])) + "|\n"

    return markdown + "\n"


def replace_html_special_characters(html: str) -> str:
    """Substituições de caracteres especiais HTML por caracteres.

    apropriados ou strings vazias.

    Args:
        html (_type_): _description_

    Returns:
        _type_: _description_
    """
    return (
        html.replace("&nbsp;", " ")  # Espaço não quebrável
        .replace("&#8239;", " ")  # Espaço estreito não quebrável
        .replace("&#8203;", "")  # Zero width space
        .replace("&#64257;", "fi")  # Ligadura fi
        .replace("&shy;", "")
    )  # Soft hyphen


def remove_html_comments(html: str) -> str:
    """Função para remover comentários HTML.

    Args:
        html (_type_): _description_

    Returns:
        _type_: _description_
    """
    return re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)


def remove_specific_elements(html: str) -> str:
    """Função para remover diversos elementos HTML sem perder o conteúd.

    Args:
        html (_type_): _description_

    Returns:
        _type_: _description_
    """
    soup = BeautifulSoup(html, "html.parser")
    # Lista de tags para remover, mantendo o conteúdo interno
    tags_to_remove = ["span", "div", "main", "section",
                      "blockquote", "center", "nav"]
    # Lógica para remover elementos com 'display: none', incluindo seu
    # conteúdo interno
    for element in soup.find_all(
        style=lambda value: value and "display: none" in value
    ):
        element.decompose()

    for tag in tags_to_remove:
        [match.unwrap() for match in soup.find_all(tag)]

    return soup


def html_to_markdown(html: str) -> str:  # noqa: C901, PLR0912
    """Função para converter conteúdo HTML em Markdown.

    Args:
        html (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        html = replace_html_special_characters(html)
        html = remove_html_comments(html)
        soup = remove_specific_elements(html)
        markdown = ""
        counters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for element in soup.body:
            # Convertendo cabeçalhos HTML (h1-h9) para Markdown
            if element.name in ["h1", "h2", "h3", "h4",
                                "h5", "h6", "h7", "h8", "h9"]:
                header_level = int(element.name[1])
                markdown += ("#" * header_level +
                             f" {element.get_text().strip()}\n\n")
            # Mantendo o HTML original para os elementos listados
            elif element.name in ["code", "pre"]:
                markdown += str(element)
            elif element.name == "p":
                paragraph_markdown, counters = process_paragraph(
                    element, counters, ROMAN_NUMERALS, LETTERS
                )
                markdown += paragraph_markdown
            elif element.name == "table":
                table_markdown = process_table(element)
                markdown += table_markdown
            elif element.name == "hr":
                markdown += "---\n"
            elif element.name == "ul":
                markdown += (
                    "\n".join(
                        [f"- {li.get_text().strip()}"
                            for li in element.find_all("li")]
                    )
                    + "\n\n"
                )
            elif element.name == "ol":
                markdown += (
                    "\n".join(
                        [f"1. {li.get_text().strip()}"
                            for li in element.find_all("li")]
                    )
                    + "\n\n"
                )
    except Exception as exc: # noqa: BLE001
        logger.debug(f"Erro na conversao markdown: {exc!s}")
        try:
            return remove_html_and_format_table(html)
        except Exception as exc: # noqa: BLE001
            logger.debug(exc)
            return f"Erro na conversão de HTML para Markdown.{exc!s}"
    else:
        try:
            return remove_html_and_format_table(markdown)
        except Exception as exc: # noqa: BLE001
            logger.debug(exc)
            return remove_html_tags(markdown)


def remove_multiple_spaces(row: str) -> str:
    """Remover espacos multiplos.

    Função para remover espaços múltiplos dentro de cada parágrafo, limpar
    quebras de linha com espaços,
    e remover espaços e quebras de linha no início e no final do conteúdo.

    Args:
        row (_type_): _description_

    Returns:
        _type_: _description_
    """
    text = row["TEXTO_LIMPO"]
    text = re.sub(r"[^\S\r\n]{2,}", " ", text)
    text = re.sub(r"(\r?\n\s*)+\r?\n", "\n\n", text)
    text = text.strip()
    row["TEXTO_LIMPO"] = text
    return row


def process_html_to_markdown(df: pd.DataFrame) -> pd.DataFrame:
    """Função para processar e converter HTML em Markdown no DataFrame.

    Args:
        df (_type_): _description_

    Returns:
        _type_: _description_
    """
    df["TEXTO_LIMPO"] = df["HTML"].apply(
        lambda x: html_to_markdown(x) if
        isinstance(x, str) and x.strip() else ""
    )
    return df.drop(columns=["HTML"])


def split_by_sections(text: str) -> dict:
    """Slit text por secoes.

    Args:
        text (str): _description_

    Returns:
        dict: _description_
    """
    padrao_quebra = r"# \*\*(.*?)\*\*"
    if text[:2] != "**":
        text = "# **INICIO**" + text
    secoes = re.split(padrao_quebra, text)
    secoes = [secao.strip() for secao in secoes if secao.strip()]
    dicionario_secoes = {}
    for i in range(0, len(secoes), 2):
        chave = secoes[i]
        valor = secoes[i + 1] if i + 1 < len(secoes) else ""
        dicionario_secoes[chave] = [x for x in valor.splitlines() if x != ""]
    return dicionario_secoes


def split_chunks_old(
        splited: dict, max_tokens: int = 2048, overlap: int = 2) -> dict:
    """spliter.

    Divide um dicionário de textos em chunks com base no número máximo
    de tokens permitidos.

    Args:
        splited (dict): Um dicionário contendo textos divididos por chave.
        max_tokens (int, opcional): O número máximo de tokens permitidos
        por chunk. O padrão é 2048.
        overlap (int, opcional): O número de tokens de sobreposição entre
        chunks. O padrão é 2.

    Returns:
        dict: Um dicionário contendo o resumo dos textos e os chunks divididos.
    """
    summarize_chunk = [""]
    resumo_esp = []
    actual_chunk = 0
    actual_tokens = 0
    for key, value in splited.items():
        if "EMENTA" in key or "CONCLUSÃO" in key:
            resumo_esp.append(f"{key}\n" + "\n".join(value))
        elif (
            len(encoder.encode(f"{key}\n" + "\n".join(value))) + actual_tokens
            <= max_tokens
        ):
            summarize_chunk[actual_chunk] = (
                summarize_chunk[actual_chunk] + f"{key}\n" + "\n".join(value)
            )
            actual_tokens += len(encoder.encode(f"{key}\n" + "\n".join(value)))
        else:
            actual_chunk += 1
            actual_tokens = 0
            summarize_chunk.append("")
            if (
                len(encoder.encode(f"{key}\n" + "\n".join(value))) +
                actual_tokens
                <= max_tokens
            ):
                summarize_chunk[actual_chunk] = (
                    summarize_chunk[actual_chunk] +
                    f"{key}\n" + "\n".join(value)
                )
                actual_tokens += len(encoder.encode(f"{key}\n" +
                                                    "\n".join(value)))
            else:
                summarize_chunk[actual_chunk] = (
                    summarize_chunk[actual_chunk] + f"{key}\n"
                )
                actual_tokens += len(encoder.encode(f"{key}\n"))
                for line_n in range(len(value)):
                    if len(encoder.encode(value[line_n] + "\n")) >= max_tokens:
                        pass
                    elif (
                        len(encoder.encode(value[line_n] + "\n")) +
                        actual_tokens
                        <= max_tokens
                    ):
                        summarize_chunk[actual_chunk] = (
                            summarize_chunk[actual_chunk] + value[line_n] +
                            "\n"
                        )
                        actual_tokens += len(encoder.encode(value[line_n] +
                                                            "\n"))
                    else:
                        actual_chunk += 1
                        actual_tokens = 0
                        summarize_chunk.append(
                            f"{key}\n" + "\n".join(
                                value[line_n - overlap: line_n])
                        )
                        summarize_chunk[actual_chunk] = (
                            summarize_chunk[actual_chunk] + value[line_n] +
                            "\n"
                        )
                        actual_tokens += len(encoder.encode(value[line_n] +
                                                            "\n"))
    return {"Resumo": resumo_esp, "chunks": summarize_chunk}


def pre_processamento_pdf(text: str) -> str:
    """Funcao para preprocessamento de dados.

    remove espacos duplos e qubras de linha desnecessarios.

    Args:
        text (str): texto de entrada

    Returns:
        str: texto pre processado
    """
    text = re.sub(r"[ ]{2,}", " ", text.strip())
    return re.sub(r"[ \n]{2,}", "\n", text)


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from a given text string.

    Args:
        text (str): The input text with HTML tags.

    Returns:
        str: The text without HTML tags.
    """
    return re.sub(r"<.*?>", "", text)


def remove_html_and_format_table(html_content: str) -> str:
    """Remove HTML tags from the content and format any tables found in the HTML.

    This function parses the given HTML content, converts any tables found into
    pandas DataFrames, and replaces the tables in the HTML with their string
    representation. It then returns the cleaned text without HTML tags.

    Args:
        html_content (str): The input HTML content.

    Returns:
        str: The cleaned text with tables formatted as plain text.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    for table in soup.find_all("table"):
        data = pd.read_html(str(table))[0]
        table.replace_with(data.to_markdown(index=False))

    return soup.get_text()

def get_file_extension(filename: str) -> str:
    """Função auxiliar para extrair a extensão do arquivo.

    Args:
        filename (str): nome do arquivo
    """
    parts = filename.split(".")
    return parts[-1] if len(parts) > 1 else "html"
