from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.deepseek.com")

def build_context(chunks):
    context_parts = []

    for i, chunk in enumerate(chunks):
        meta = chunk["metadata"]

        section = meta.get("section", "unknown")
        clause = meta.get("clause", "")
        page = meta.get("page", "")

        context_parts.append(
            f"[Chunk {i+1}] (Section: {section}, Clause: {clause}, Page: {page})\n{chunk['text']}"
        )

    return "\n\n".join(context_parts)

def generate_answer(question: str, context: str):
    MASTER_PROMPT = """
        You are an expert AI assistant designed to answer questions based ONLY on provided document context.

        You are used for:
        - Legal documents (e.g., IPC, contracts)
        - Financial documents (e.g., policies, tax, reports)
        - Technical documentation (APIs, frameworks, guides)

        Your job is to extract, analyze, and synthesize information from the provided context and give the BEST possible answer.

        ---

        ## 🔒 STRICT RULES

        1. You MUST answer ONLY using the provided context.
        2. You MUST use ALL relevant chunks before answering.
        3. You MUST NOT hallucinate or assume anything not present in context.
        4. If the answer is partially available, combine information from multiple chunks.
        5. If the answer is NOT present, clearly say:
        "The answer is not available in the provided documents."
        6. Do NOT ignore any chunk — even if partially useful.
        7. Prefer authoritative statements (sections, definitions, rules, clauses).

        ---

        ## 🧠 HOW TO THINK (IMPORTANT)

        Before answering:
        - Read ALL chunks carefully
        - Identify relevant parts across chunks
        - Merge overlapping or partial information
        - Resolve conflicts if multiple chunks differ
        - Prioritize:
        - Explicit definitions
        - Sections / rules
        - Direct statements over examples

        ---

        ## 📦 INPUT FORMAT

        You will receive:

        Question:
        {question}

        Context:
        {context}

        Each context chunk is formatted like:

        [Chunk X]
        Section: <section_name>
        Clause: <clause_if_any>
        Content:
        <text>

        ---

        ## 🧾 OUTPUT FORMAT (VERY IMPORTANT)

        You MUST respond in this format:

        ### ✅ Answer
        A clear, well-structured answer written in simple and professional language.

        - Use bullet points if helpful
        - Keep it easy to read
        - Avoid unnecessary complexity

        ---

        ### 📚 Supporting Evidence
        List the key supporting points from the context:

        - Mention section/clause if available
        - Quote or summarize relevant lines
        - Combine multiple chunks if needed

        ---

        ### ⚠️ Notes (if applicable)
        - Mention if information is incomplete
        - Mention if multiple interpretations exist
        - Mention assumptions (ONLY if clearly derived from context)

        ---

        ## ✍️ STYLE GUIDELINES

        - Be clear and direct
        - Avoid repetition
        - Avoid overly long paragraphs
        - Use formatting (bullets, spacing)
        - Make it readable for humans, not machines

        ---

        ## 🚨 IMPORTANT EDGE CASES

        - If question is vague → interpret using best matching context
        - If multiple sections apply → include all relevant ones
        - If answer spans multiple chunks → merge them into one answer
        - If only indirect info is available → infer carefully, but stay grounded

        ---

        ## 🎯 GOAL

        Your goal is to produce the MOST accurate, complete, and user-friendly answer possible using ONLY the provided context.

        ---

        Now answer the question.
    """

    prompt = MASTER_PROMPT.format(
        question=question,
        context=context
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content


def rerank_chunks(query, chunks):
    query_words = set(query.lower().split())

    scored = []

    for chunk in chunks:
        text = chunk["text"].lower()
        score = sum(1 for w in query_words if w in text)

        if "section" in chunk["text"].lower():
            score += 2

        scored.append((score, chunk))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [c for _, c in scored[:5]]