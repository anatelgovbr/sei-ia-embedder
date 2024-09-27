"""Querys sql."""

from embedder.envs import DB_SEI_SCHEMA

INTERNAL_DOCS_FROM_PROCESS_TEMPLATE = f"""SELECT
        -- p.protocolo_formatado,
        p.id_protocolo,
        pd.protocolo_formatado nr_documento,
        COALESCE(pd.descricao,'') documento_especificacao,
        s.id_serie id_type_document,
        dc.conteudo content_doc,
        'html' content_type,
        pd.dta_inclusao,
        COALESCE(s.nome,'') name_id_type_doc,
        da.id_documento id_protocolo_documento
    FROM
        {DB_SEI_SCHEMA}.protocolo p
    INNER JOIN
        {DB_SEI_SCHEMA}.documento da
        ON da.id_procedimento = p.id_protocolo
    INNER JOIN
        {DB_SEI_SCHEMA}.protocolo pd
        ON da.id_documento = pd.id_protocolo
    LEFT JOIN
        {DB_SEI_SCHEMA}.documento_conteudo dc
        ON dc.id_documento = da.id_documento
    INNER JOIN
        {DB_SEI_SCHEMA}.serie s
        ON da.id_serie = s.id_serie
    WHERE
	pd.sta_estado = '0'
	AND da.sta_documento <> 'x'
	AND da.id_documento = {{}}
"""

CHECK_IF_HAS_CONTENT_TEMPLATE = f"""
SELECT
    CASE 
        WHEN dc.conteudo IS NULL THEN 0
        ELSE 1
    END AS status_content_doc
FROM
    {DB_SEI_SCHEMA}.protocolo p
INNER JOIN
    {DB_SEI_SCHEMA}.documento da ON da.id_procedimento = p.id_protocolo
INNER JOIN
    {DB_SEI_SCHEMA}.protocolo pd ON da.id_documento = pd.id_protocolo
LEFT JOIN
    {DB_SEI_SCHEMA}.documento_conteudo dc ON dc.id_documento = da.id_documento
INNER JOIN
    {DB_SEI_SCHEMA}.serie s ON da.id_serie = s.id_serie
WHERE
    pd.sta_estado = '0'
    AND da.sta_documento <> 'x'
    AND da.id_documento = {{}}
"""

GET_NOME_DOCUMENTO_FROM_ID = f"""
SELECT
    nome as nome_doc
FROM
    {DB_SEI_SCHEMA}.anexo
WHERE
    id_protocolo = {{}}
"""

TYPE_DOC_TEMPLATE = f"""
SELECT
    da.sta_documento type_doc,
    COALESCE(an.nome,'') formato_arquivo,
    p.protocolo_formatado num_proc,
    pd.protocolo_formatado num_doc
FROM    {DB_SEI_SCHEMA}.documento da
LEFT JOIN {DB_SEI_SCHEMA}.anexo an
    ON (da.id_documento = an.id_protocolo)
LEFT JOIN {DB_SEI_SCHEMA}.protocolo p
    ON da.id_procedimento = p.id_protocolo
LEFT JOIN {DB_SEI_SCHEMA}.protocolo pd
    ON (da.id_documento = pd.id_protocolo)
WHERE da.id_documento = {{}}
"""

METADATA_DOCUMENTO_TEMPLATE = f"""
SELECT
    p.protocolo_formatado  id_protocolo_formatado,
    p.id_protocolo id_procedimento,
    pd.protocolo_formatado id_documento_formatado,
    COALESCE(pd.descricao,'') documento_especificacao,
    s.id_serie id_tipo_documento,
    COALESCE(an.nome, 'html') formato_arquivo,
    pd.dta_inclusao,
    COALESCE(s.nome,'')  nome_id_tipo_documento,
    da.id_documento  id_documento
FROM
    {DB_SEI_SCHEMA}.protocolo p
INNER JOIN
    {DB_SEI_SCHEMA}.documento da
    ON da.id_procedimento = p.id_protocolo
INNER JOIN
    {DB_SEI_SCHEMA}.protocolo pd
    ON da.id_documento = pd.id_protocolo
LEFT JOIN
    {DB_SEI_SCHEMA}.documento_conteudo dc
    ON dc.id_documento = da.id_documento
INNER JOIN
    {DB_SEI_SCHEMA}.serie s
    ON da.id_serie = s.id_serie
LEFT JOIN
    (SELECT
        id_protocolo, id_anexo, sin_ativo, nome
     FROM {DB_SEI_SCHEMA}.anexo
     WHERE sin_ativo= 'S') an
    ON (da.id_documento = an.id_protocolo)
WHERE
    1=1
    AND da.id_documento = '{{id_documento}}'
"""

SELECT_METADATA_MYSQL = f"""

with
	base_docs_nao_cancelados_externos as (
		SELECT
			d.id_documento,
			d.id_procedimento,
			SUBSTRING_INDEX(a.nome, '.', -1) as formato_arquivo,
			d.sin_bloqueado,
			d.sta_documento,
			pd.protocolo_formatado as doc_formatado,
			pp.protocolo_formatado as procedimento_formatado,
			a.hash as hash_anexo_doc_externo
		FROM {DB_SEI_SCHEMA}.documento d
		left join {DB_SEI_SCHEMA}.protocolo pd
			on pd.id_protocolo = d.id_documento
		left join {DB_SEI_SCHEMA}.protocolo pp
			on pp.id_protocolo = d.id_procedimento
		left join {DB_SEI_SCHEMA}.anexo a
			on a.id_protocolo = pd.id_protocolo
		WHERE
			d.sta_documento = 'X'
			AND pd.sta_estado = 0
	),
	base_docs_nao_cancelados_nao_externos as (
		SELECT
			d.id_documento,
			d.id_procedimento,
			NULL as formato_arquivo,
			d.sin_bloqueado,
			d.sta_documento,
			pd.protocolo_formatado as doc_formatado,
			pp.protocolo_formatado as procedimento_formatado,
			NULL as hash_anexo_doc_externo
		FROM {DB_SEI_SCHEMA}.documento d
		left join {DB_SEI_SCHEMA}.protocolo pd
			on pd.id_protocolo = d.id_documento
		left join {DB_SEI_SCHEMA}.protocolo pp
			on pp.id_protocolo = d.id_procedimento
		WHERE
			d.sta_documento <> 'X'
			AND pd.sta_estado = 0
	),
	base_docs_nao_cancelados as (
	SELECT * from base_docs_nao_cancelados_externos
	UNION
		SELECT * from base_docs_nao_cancelados_nao_externos
	),
	base_docs_bloqueados as (
		SELECT
			id_documento,
			sin_bloqueado,
			id_procedimento,
			sta_documento,
			doc_formatado,
			procedimento_formatado,
			NULL as hash_anexo_doc_externo,
			NULL as max_dth_atualizacao_vsd_doc_interno,
			id_documento as hash_versao
		FROM base_docs_nao_cancelados
		WHERE sin_bloqueado = 'S'
	),
	prep_base_docs_nao_bloqueados as (
		SELECT
			bdnc.id_documento,
			max(vsd.dth_atualizacao) as max_dth_atualizacao_vsd_doc_interno
		FROM base_docs_nao_cancelados bdnc
		left join secao_documento sd
		on bdnc.id_documento = sd.id_documento
		left join versao_secao_documento vsd
			on sd.id_secao_documento = vsd.id_secao_documento
		WHERE
			sin_bloqueado = 'N'
			AND sta_documento IN ('X', 'I') # POR ENQUANTO, OLHA APENAS X e I PARA NAO BLOQUEADO
		GROUP BY
			bdnc.id_documento
	),
	base_docs_nao_bloqueados as (
		SELECT
			bdnc.id_documento,
			bdnc.sin_bloqueado,
			bdnc.id_procedimento,
			bdnc.sta_documento,
			bdnc.doc_formatado,
			procedimento_formatado,
			bdnc.hash_anexo_doc_externo,
			pbdnc.max_dth_atualizacao_vsd_doc_interno,
			md5(CONCAT(bdnc.id_documento,
				COALESCE(bdnc.hash_anexo_doc_externo, ''),
				COALESCE(pbdnc.max_dth_atualizacao_vsd_doc_interno, '')
			)) AS hash_versao
		FROM prep_base_docs_nao_bloqueados pbdnc
		LEFT JOIN base_docs_nao_cancelados bdnc ON pbdnc.id_documento = bdnc.id_documento
		),
	base_final as (
		SELECT * from base_docs_bloqueados
	UNION
		SELECT * from base_docs_nao_bloqueados
	)
select
	*
from base_final
-- where
	-- sin_bloqueado = 'S' -- 'N' # 'S'
	-- AND sta_documento = 'I' # 'X' 'I' 'A' 'F'
"""


SELECT_METADATA_ORACLE = f"""
with
	docs_nao_canc_ext as (
		SELECT
			d.id_documento,
			d.id_procedimento,
			SUBSTR(a.nome, INSTR(a.nome, '.', -1) + 1) as formato_arquivo,
			d.sin_bloqueado,
			d.sta_documento,
			pd.protocolo_formatado as doc_formatado,
			pp.protocolo_formatado as procedimento_formatado,
			a.hash as hash_anexo_doc_externo
		FROM {DB_SEI_SCHEMA}.documento d
		left join {DB_SEI_SCHEMA}.protocolo pd
			on pd.id_protocolo = d.id_documento
		left join {DB_SEI_SCHEMA}.protocolo pp
			on pp.id_protocolo = d.id_procedimento
		left join {DB_SEI_SCHEMA}.anexo a
			on a.id_protocolo = pd.id_protocolo
		WHERE
			d.sta_documento = 'X'
			AND pd.sta_estado = 0
	),
	docs_nao_canc_nao_ext as (
		SELECT
			d.id_documento,
			d.id_procedimento,
			'' as formato_arquivo,
			d.sin_bloqueado,
			d.sta_documento,
			pd.protocolo_formatado  doc_formatado,
			pp.protocolo_formatado  procedimento_formatado,
			''  hash_anexo_doc_externo
		FROM {DB_SEI_SCHEMA}.documento d
		left join {DB_SEI_SCHEMA}.protocolo pd
			on pd.id_protocolo = d.id_documento
		left join {DB_SEI_SCHEMA}.protocolo pp
			on pp.id_protocolo = d.id_procedimento
		WHERE
			d.sta_documento <> 'X'
			AND pd.sta_estado = 0
	),
	docs_nao_canc as (
		SELECT * from docs_nao_canc_ext
	UNION
		SELECT * from docs_nao_canc_nao_ext
	),
docs_bloq as (
    SELECT
        id_documento,
        sin_bloqueado,
        id_procedimento,
        sta_documento,
        doc_formatado,
        procedimento_formatado,
        '' as hash_anexo_doc_externo,
        CAST(NULL AS DATE) as max_dth_atualiz_vsd_doc_int,
        TO_CHAR(id_documento) || '' || '' as hash_versao
    FROM docs_nao_canc
    WHERE sin_bloqueado = 'S'
),
	prep_docs_nao_bloq as (
		SELECT
			bdnc.id_documento,
			max(vsd.dth_atualizacao) max_dth_atualiz_vsd_doc_int
		FROM docs_nao_canc bdnc
		left join {DB_SEI_SCHEMA}.secao_documento sd
			on bdnc.id_documento = sd.id_documento
		left join {DB_SEI_SCHEMA}.versao_secao_documento vsd
			on sd.id_secao_documento = vsd.id_secao_documento
		WHERE
			sin_bloqueado = 'N'
			AND sta_documento IN ('X', 'I') -- POR ENQUANTO, OLHA APENAS X e I PARA NAO BLOQUEADO
		GROUP BY
			bdnc.id_documento
	),
docs_nao_bloq as (
    SELECT
        bdnc.id_documento,
        bdnc.sin_bloqueado,
        bdnc.id_procedimento,
        bdnc.sta_documento,
        bdnc.doc_formatado,
        procedimento_formatado,
        bdnc.hash_anexo_doc_externo,
        pbdnc.max_dth_atualiz_vsd_doc_int,
        bdnc.id_documento ||
        COALESCE(bdnc.hash_anexo_doc_externo, '') ||
        COALESCE(TO_CHAR(pbdnc.max_dth_atualiz_vsd_doc_int), '') as hash_versao
    FROM prep_docs_nao_bloq pbdnc
    LEFT JOIN docs_nao_canc bdnc
    ON pbdnc.id_documento = bdnc.id_documento
),
	base_final as (
		SELECT * from docs_bloq
	UNION
		SELECT * from docs_nao_bloq
	)
select
    id_documento,
    sin_bloqueado,
    id_procedimento,
    sta_documento,
    doc_formatado,
    procedimento_formatado,
    hash_anexo_doc_externo,
    max_dth_atualiz_vsd_doc_int,
    LOWER(RAWTOHEX(DBMS_CRYPTO.HASH(UTL_RAW.CAST_TO_RAW(hash_versao), 2))) as hash_versao -- Algoritmo MD5
from base_final
-- where
-- 	sin_bloqueado = 'S' -- 'N' # 'S'
	-- AND sta_documento = 'I' # 'X' 'I' 'A' 'F'
"""

# ruff: noqa: S608
SELECT_METADATA_MSSQL = f"""
WITH base_docs_nao_cancelados_externos AS (
    SELECT
        d.id_documento,
        d.id_procedimento,
        REVERSE(LEFT(REVERSE(a.nome), CHARINDEX('.', REVERSE(a.nome)) - 1)) formato_arquivo,
        d.sin_bloqueado,
        d.sta_documento,
        pd.protocolo_formatado doc_formatado,
        pp.protocolo_formatado procedimento_formatado,
        a.hash hash_anexo_doc_externo
    FROM {DB_SEI_SCHEMA}.documento d
    LEFT JOIN {DB_SEI_SCHEMA}.protocolo pd ON pd.id_protocolo = d.id_documento
    LEFT JOIN {DB_SEI_SCHEMA}.protocolo pp ON pp.id_protocolo = d.id_procedimento
    LEFT JOIN {DB_SEI_SCHEMA}.anexo a ON a.id_protocolo = pd.id_protocolo
    WHERE
        d.sta_documento = 'X'
        AND pd.sta_estado = 0
),
base_docs_nao_cancelados_nao_externos AS (
    SELECT
        d.id_documento,
        d.id_procedimento,
        NULL formato_arquivo,
        d.sin_bloqueado,
        d.sta_documento,
        pd.protocolo_formatado doc_formatado,
        pp.protocolo_formatado procedimento_formatado,
        NULL hash_anexo_doc_externo
    FROM {DB_SEI_SCHEMA}.documento d
    LEFT JOIN {DB_SEI_SCHEMA}.protocolo pd ON pd.id_protocolo = d.id_documento
    LEFT JOIN {DB_SEI_SCHEMA}.protocolo pp ON pp.id_protocolo = d.id_procedimento
    WHERE
        d.sta_documento <> 'X'
        AND pd.sta_estado = 0
),
base_docs_nao_cancelados AS (
    SELECT * FROM base_docs_nao_cancelados_externos
    UNION ALL
    SELECT * FROM base_docs_nao_cancelados_nao_externos
),
base_docs_bloqueados AS (
    SELECT
        id_documento,
        sin_bloqueado,
        id_procedimento,
        sta_documento,
        doc_formatado,
        procedimento_formatado,
        NULL AS hash_anexo_doc_externo,
        NULL AS max_dth_atualizacao_vsd_doc_interno,
        CAST(id_documento AS VARCHAR(36)) AS hash_versao
    FROM base_docs_nao_cancelados
    WHERE sin_bloqueado = 'S'
),
prep_base_docs_nao_bloqueados AS (
    SELECT
        bdnc.id_documento,
        MAX(vsd.dth_atualizacao) max_dth_atualizacao_vsd_doc_interno
    FROM base_docs_nao_cancelados bdnc
    LEFT JOIN secao_documento sd ON bdnc.id_documento = sd.id_documento
    LEFT JOIN versao_secao_documento vsd ON sd.id_secao_documento = vsd.id_secao_documento
    WHERE
        sin_bloqueado = 'N'
        AND sta_documento IN ('X', 'I')
    GROUP BY
        bdnc.id_documento
),
base_docs_nao_bloqueados AS (
    SELECT
        bdnc.id_documento,
        bdnc.sin_bloqueado,
        bdnc.id_procedimento,
        bdnc.sta_documento,
        bdnc.doc_formatado,
        bdnc.procedimento_formatado,
        bdnc.hash_anexo_doc_externo,
        pbdnc.max_dth_atualizacao_vsd_doc_interno,
        CONVERT(VARCHAR(32), HASHBYTES('MD5', CONCAT(
            CAST(bdnc.id_documento AS VARCHAR(36)),
            ISNULL(bdnc.hash_anexo_doc_externo, ''),
            ISNULL(CAST(pbdnc.max_dth_atualizacao_vsd_doc_interno AS VARCHAR(23)), '')
        )), 2) AS hash_versao
    FROM prep_base_docs_nao_bloqueados pbdnc
    LEFT JOIN base_docs_nao_cancelados bdnc ON pbdnc.id_documento = bdnc.id_documento
),
base_final AS (
    SELECT * FROM base_docs_bloqueados
    UNION ALL
    SELECT * FROM base_docs_nao_bloqueados
)
SELECT *
FROM base_final                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
-- WHERE
	-- sin_bloqueado = 'S' -- 'N' # 'S'
	-- AND sta_documento = 'I' # 'X' 'I' 'A' 'F'
"""
