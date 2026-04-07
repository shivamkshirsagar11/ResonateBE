MAX_TOKENS = 400
MIN_TOKENS = 100
OVERLAP = 0

def compute_boundary_score(block, template):
    score = 0

    if block["type"] == "section":
        score += template["headers"]

    elif block["type"] == "clause":
        score += template["clauses"]

    elif block["type"] == "paragraph":
        score += template["paragraphs"]

    return score

def estimate_tokens(text: str):
    return len(text.split())  # simple for now

def create_chunks(structured_blocks, template, requires_consistency):
    chunks = []

    current_text = []
    current_tokens = 0
    current_metadata = {}
    order = 0

    for block in structured_blocks:
        block_text = block["text"]
        tokens = estimate_tokens(block_text)

        # only split on strong boundaries
        is_strong_boundary = block["type"] in ["section", "clause"]

        if is_strong_boundary and current_tokens >= MIN_TOKENS:
            chunks.append({
                "text": " ".join(current_text),
                "metadata": current_metadata.copy(),
                "token_count": current_tokens,
                "order": order
            })
            order += 1
            current_text = []
            current_tokens = 0

        current_text.append(block_text)
        current_tokens += tokens

        if current_tokens >= MAX_TOKENS:
            chunks.append({
                "text": " ".join(current_text),
                "metadata": current_metadata.copy(),
                "token_count": current_tokens,
                "order": order
            })
            order += 1
            current_text = []
            current_tokens = 0

        if block.get("section"):
            current_metadata["section"] = block["section"]

        if block.get("clause"):
            current_metadata["clause"] = block["clause"]

    if current_text:
        chunks.append({
            "text": " ".join(current_text),
            "metadata": current_metadata,
            "token_count": current_tokens,
            "order": order
        })

    return chunks