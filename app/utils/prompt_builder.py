import json

from app.schemas.database_schema import DatabaseSchemaResponse


def build_sql_generation_prompt(
    question: str,
    schema: DatabaseSchemaResponse,
    previous_sql: str | None = None,
    execution_error: str | None = None,
) -> str:
    schema_json = json.dumps(
        {
            table_name: table_schema.model_dump()
            for table_name, table_schema in schema.items()
        },
        indent=2,
        sort_keys=True,
    )

    correction_context = ""
    if previous_sql and execution_error:
        correction_context = f"""
Previous SQL failed:
{previous_sql}

SQLite error:
{execution_error}

Correct the SQL using only the schema below.
"""

    return f"""
You are a senior data analyst that writes safe SQLite SELECT queries.

Task:
Convert the user's natural language question into one valid SQLite SQL query.

Hard rules:
- Return ONLY the SQL query.
- Do not use markdown.
- Do not include explanations, comments, labels, or code fences.
- Use SQLite dialect only.
- Use only tables and columns present in the schema JSON.
- Do not hallucinate table names or column names.
- Prefer explicit column names over SELECT *.
- Generate read-only SELECT statements only.
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, ATTACH, DETACH, or VACUUM statements.
- If the request cannot be answered from the schema, return a harmless empty SELECT:
  SELECT NULL WHERE 1 = 0

SQLite schema JSON:
{schema_json}

{correction_context}
User question:
{question}
""".strip()
