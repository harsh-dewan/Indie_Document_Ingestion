"""
Description:SQL Statements being used in the code
Author: @harshdewan
Date: 11-04-2026
"""

INSERT_DOCUMENT_RECORD="""
    INSERT INTO documents (id, filename, total_chunks, metadata) VALUES (%s, %s, %s, %s)
"""


SELECT_STRATEGY_ID="""
        SELECT id FROM chunking_strategies WHERE name = %s
    """

CREATE_STRATEGY_RECORD="""
    INSERT INTO chunking_strategies (name, config)
                VALUES (%s, %s)
                RETURNING id
"""

INSERT_EMBEDDINGS_IN_BATCH = """
    INSERT INTO chunks (
        document_id,
        strategy_id,
        chunk_index,
        content,
        embedding,
        metadata
    ) VALUES %s
"""