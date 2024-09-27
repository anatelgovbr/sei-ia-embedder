"""Modulo de Embedding para RAG."""
import logging

import numpy as np
import torch
from langchain.text_splitter import RecursiveCharacterTextSplitter as RecursiveSplitter
from sentence_transformers import SentenceTransformer
from transformers import AutoModel, AutoTokenizer

from embedder.extract_docs.extract_content import get_doc_from_id
from embedder.extract_docs.metadata_sei import get_doc_metadata_from_id
from embedder.http_exceptions import HTTPException422
from embedder.persist_table_embeddings import persist_embeddings

logger = logging.getLogger(__name__)

SEPARATORS = ["\n\n", "\n", ".", ",", "\u200B", "\uff0c", "\u3001", "\uff0e", "\u3002", ""]

def embed_long_text(text: str, model_path: str, max_length: int) -> list:
    """Embebe um texto longo dividindo-o em blocos, codificando cada bloco usando modelo fornecido e calculando a media.

    Parâmetros:
        text (str): O texto de entrada a ser embebido.
        model_path (str): O caminho para o modelo usado para codificação.
        max_length (int): O comprimento máximo de cada bloco.

    Retorna:
        np.ndarray: A embelezamento final do texto inteiro.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path)
    chunks = split_into_chunks(text, max_length)

    chunk_embeddings = []
    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", padding="max_length", max_length=max_length)
        with torch.no_grad():
            outputs = model(**inputs)
        chunk_embeddings.append(outputs.last_hidden_state.mean(dim=1).squeeze().numpy())

    return np.mean(chunk_embeddings, axis=0)


def create_embeddings(
        text: str,
        model: str ,
        ) -> np.ndarray:
    """Funcao de embedding para RAG.

    Args:
        text (str): Texto de entrada.
        model (str): Nome do modelo usado para embeddings
            (padrão é o modelo especificado).

    Returns:
        numpy.ndarray: Embeddings gerado para o texto de entrada.
    """
    logger.debug("entrou no create_embeddings")
    model = SentenceTransformer(model)
    if isinstance(text, str):
        embeddings = model.encode([text])
        return embeddings[0]
    if isinstance(text, list):
        return model.encode(text)
    raise HTTPException422

def split_into_chunks(text: str, max_length: int) -> list:
    """Divide o texto de entrada em pedaços de um comprimento máximo especificado.

    Parâmetros:
        text (str): O texto de entrada a ser dividido em pedaços.
        max_length (int): O comprimento máximo de cada pedaço.

    Retorna:
        list: Uma lista de pedaços onde cada pedaço é uma substring do texto de entrada.
    """
    tokens = text.split()
    chunks = []
    for i in range(0, len(tokens), max_length):
        chunk = " ".join(tokens[i:i + max_length])
        chunks.append(chunk)

    for i in range(len(chunks)):
        if len(chunks[i].split()) < max_length:
            chunks[i] = chunks[i] + " [PAD]" * (max_length - len(chunks[i].split()))

    return chunks


def split_chunks(
            doc: str,
            model_path: str ,
            chunk_size: int = 400,
            chunk_overlap: int = 50,
            separators: list = SEPARATORS,
            *,
            return_positions: bool = False,
            ) -> list:
    """Funcao para dividir o texto em chunks.

    Args:
        doc: Texto a ser dividido.
        model_path (str): Caminho do modelo (padrão é o modelo especificado).
        chunk_size (int): Tamanho do chunk (padrão é 400).
        chunk_overlap (int): Sobreposição entre chunks (padrão é 50).
        separators (list): Lista de separadores (padrão é a lista especificada)
        return_positions (bool): Se deve retornar as posicoes dos chunks (padrão é False).

    Returns:
        list: Lista de chunks do texto.
    """
    logger.debug("entrou no split_chunks")
    tokenizer = AutoTokenizer.from_pretrained(model_path, add_special_tokens=False)
    text_splitter = RecursiveSplitter.from_huggingface_tokenizer(
        tokenizer=tokenizer,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )

    chunks = text_splitter.split_text(doc)
    positions = []

    if return_positions:
        for chunk in chunks:
            start = doc.find(chunk)
            if start != -1:
                end = start + len(chunk)
                positions.append((start, end))
        return chunks, positions

    return chunks, positions


def create_embeddings_for_docs(
    id_documento: int,
    model: str ,
    max_length: int = 128,
    *,
    overwrite: bool = False,
) -> list:
    """Função de embedding para documentos do SEI RAG.

    Args:
        id_documento (int): ID do documento.
        model (str): Nome do modelo usado para embeddings
            (padrão é o modelo especificado).
        max_length (int): Tamanho máximo de cada chunk (padrão é 128).
        overwrite (bool): Sobrescrever embeddings existentes.

    Returns:
        list: Lista de IDs dos embeddings criados.
    """
    logger.debug("entrou no create_embeddings_for_docs")
    doc, _ = get_doc_from_id(id_documento)
    doc_chunks, positions = split_chunks(doc,
                                         chunk_size=max_length,
                                         chunk_overlap=50,
                                         return_positions=True)
    doc_chunks_emb = []
    for chunk in doc_chunks:
        if len(chunk) > max_length:
            doc_chunks_emb.append(embed_long_text(chunk, model_path=model, max_length=max_length))
        else:
            doc_chunks_emb.append(create_embeddings(text=chunk, model=model))
    doc_metadata = get_doc_metadata_from_id(id_documento=id_documento)
    ids = []
    for i, (emb_text, embedding, pos) in enumerate(
        zip(doc_chunks, doc_chunks_emb, positions, strict=True)):
        persist_embeddings(
            id_documento=id_documento,
            chunk_id=i,
            embedding=embedding,
            emb_text=emb_text,
            metadata_=doc_metadata,
            id_procedimento=doc_metadata["id_procedimento"],
            start_position=pos[0],
            finished_position=pos[1],
            overwrite=overwrite,
        )
        ids.append(i)
    return ids
