MAX_TOKENS = 300
MIN_TOKENS = 80
OVERLAP = 40

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
    current_metadata = {}
    current_tokens = 0
    order = 0

    for block in structured_blocks:
        block_text = block["text"]
        block_tokens = estimate_tokens(block_text)

        score = compute_boundary_score(block, template)

        # Update metadata safely
        if block.get("section"):
            current_metadata["section"] = block["section"]

        if block.get("clause"):
            current_metadata["clause"] = block.get("clause")

        if "page_start" not in current_metadata:
            current_metadata["page_start"] = block["page"]

        current_metadata["page_end"] = block["page"]

        # Add block
        current_text.append(block_text)
        current_tokens += block_tokens

        # Decide boundary
        should_split = False

        if requires_consistency:
            # stricter splitting for legal/finance
            if score > 0.7:
                should_split = True

        if current_tokens >= MAX_TOKENS:
            should_split = True

        # Finalize chunk
        if should_split and current_tokens >= MIN_TOKENS:
            chunk_text = " ".join(current_text)

            chunks.append({
                "text": chunk_text,
                "metadata": current_metadata.copy(),
                "token_count": current_tokens,
                "order": order
            })

            order += 1

            # Overlap logic
            overlap_text = current_text[-OVERLAP:] if len(current_text) > OVERLAP else current_text

            current_text = overlap_text
            current_tokens = estimate_tokens(" ".join(current_text))
            current_metadata = {}

    # last chunk
    if current_text:
        chunks.append({
            "text": " ".join(current_text),
            "metadata": current_metadata,
            "token_count": current_tokens,
            "order": order
        })

    return chunks