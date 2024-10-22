# Embedder Project

Projeto usado para a criacao de embeddings para RAG e similaridade de documentos.


## Instalação

Libs necessarias do SO
* GCC
* G++
* cmake
* poppler

```pip install .[dev]```

### Docker run
Dockerfiles estão na pasta ./dockerfiles

```bash
docker buildx build --load --build-arg GIT_TOKEN=${GIT_TOKEN} --network host -t assistente-${DATABASE_TYPE} -f ${DATABASE_TYPE}.dockerfile .
docker run --network docker-host-bridge --env-file ${DATABASE_TYPE}.env -d -p 8010:8080 -t assistente-${DATABASE_TYPE} bash
```

## Descrição
Este projeto é um sistema de extração, processamento e criação de embeddings para documentos do SEI (Sistema Eletrônico de Informações).

## Estrutura do Projeto

### src/embedder/extract_docs/
- **type_doc_sei.py**: Extrai o tipo e extensão do documento.
- **extract_doc_int_sei.py**: Extrai documentos internos.
- **metadata_sei.py**: Extrai metadados de documentos externos.
- **internal_sei.py**: Extrai documentos internos.
- **external_sei.py**: Extrai documentos externos.
- **extract_content.py**: Extrai conteúdo de documentos internos e externos.
- **__init__.py**: Módulo de consulta e extração de documentos.

### src/embedder/
- **embeddings.py**: Cria embeddings para documentos do SEI RAG.
- **text_preprocess.py**: Realiza o pré-processamento de textos, incluindo conversão de HTML para Markdown, remoção de espaços múltiplos, formatação de tabelas e divisão de texto em chunks.
- **persist_table_embeddings.py**: Gerencia a persistência de embeddings no banco de dados, incluindo a definição do modelo de dados para a tabela de embeddings.

## Funcionalidades Principais
- Extração de documentos internos e externos do SEI
- Extração de metadados de documentos
- Processamento de conteúdo de documentos
- Criação de embeddings para documentos
- Pré-processamento de texto e conversão de HTML para Markdown
- Persistência de embeddings em banco de dados
