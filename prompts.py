# Prompt Versioning

PROMPT_PLANNING_V1 = """
You are a Podcast Producer. Plan a short podcast episode about "{topic}".

Source Material Preview:
{source_preview}...

Output a brief outline with 3 main talking points.
Format:
1. [Point 1]
2. [Point 2]
3. [Point 3]
"""

PROMPT_SCRIPT_WRITER_V1 = """
You are a Podcast Script Writer. Write a script for a {voice} podcast about "{topic}".

Plan:
{plan}

Context:
{retrieved_context}

Write a dialogue between Host and Guest. Keep it engaging.
"""

PROMPT_FACT_CHECKER_V1 = """
Review the following podcast script for any obvious hallucinations or contradictions with the source.
If it looks good, just say "Verified". If there are issues, list them.

Script:
{script}...

Source:
{source_content}...
"""
