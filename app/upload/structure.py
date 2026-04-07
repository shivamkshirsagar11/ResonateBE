import re


SECTION_PATTERN = re.compile(r"(Section\s+\d+[A-Z]*)", re.IGNORECASE)
CLAUSE_PATTERN = re.compile(r"^\([a-zA-Z0-9]+\)", re.IGNORECASE)

def is_noise_line(line: str):
    line = line.strip()

    # too many dots → TOC
    if line.count(".") > 3:
        return True

    # page numbers only
    if line.isdigit():
        return True

    # lines like: "1 WhettingYourAppetite 3"
    if re.search(r"\d+\s+[A-Za-z]+\s+\d+", line):
        return True

    # if re.search(r"(\b[A-Za-z]+\s+\d+\s+){3,}", line):
    #     return True

    # too short
    if len(line.split()) < 3:
        return True

    # all caps short lines (headers noise)
    if line.isupper() and len(line.split()) < 6:
        return True

    return False

def clean_toc_noise(text: str):
    # remove patterns like: "Title 23"
    text = re.sub(r"[A-Za-z][A-Za-z\s\-]+?\s+\d+", "", text)

    # remove repeated spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def is_noise_block(text: str):
    text = text.strip()

    # pattern: "Title 23 Title 45 Title 67"
    matches = re.findall(r"[A-Za-z][A-Za-z\s\-]+?\s+\d+", text)

    # if too many such patterns → it's TOC
    if len(matches) >= 3:
        return True
    
    # too many dots → TOC
    if text.count("......") > 2:
        return True
    
    if text.count(". . .") > 2:
        return True

    # contains CONTENTS keyword
    if "contents" in text.lower():
        return True

    # repeated short headings (TOC style)
    words = text.split()
    if len(words) > 20:
        short_caps = [w for w in words if w.istitle() and len(w) < 15]
        if len(short_caps) > len(words) * 0.4:
            return True

    return False

def merge_lines_to_paragraphs(blocks):
    merged = []
    buffer = []

    for block in blocks:
        text = block["text"]

        # strong boundary → flush
        if block["type"] in ["section", "clause"]:
            if buffer:
                merged.append({
                    "type": "paragraph",
                    "text": " ".join(buffer),
                    "section": block.get("section"),
                    "page": block.get("page")
                })
                buffer = []

            merged.append(block)
            continue

        buffer.append(text)

        if text.endswith("."):
            merged.append({
                "type": "paragraph",
                "text": " ".join(buffer),
                "section": block.get("section"),
                "page": block.get("page")
            })
            buffer = []

    if buffer:
        merged.append({
            "type": "paragraph",
            "text": " ".join(buffer),
            "section": block.get("section"),
            "page": block.get("page")
        })

    return merged

def detect_structure(pages_data):
    structured_blocks = []

    current_section = None

    for page_data in pages_data:
        page_number = page_data["page"]
        text = page_data["text"]

        if not text:
            continue

        lines = text.split("\n")

        for line in lines:
            line = line.strip()

            if not line:
                continue
            
            # if is_noise_line(line):
            #     continue

            # Detect Section
            section_match = SECTION_PATTERN.search(line)
            if section_match:
                current_section = section_match.group(1)

                structured_blocks.append({
                    "type": "section",
                    "section": current_section,
                    "text": line,
                    "page": page_number
                })
                continue

            # Detect Clause
            clause_match = CLAUSE_PATTERN.match(line)
            if clause_match:
                structured_blocks.append({
                    "type": "clause",
                    "section": current_section,
                    "clause": clause_match.group(),
                    "text": line,
                    "page": page_number
                })
                continue

            # Default paragraph
            structured_blocks.append({
                "type": "paragraph",
                "section": current_section,
                "text": line,
                "page": page_number
            })

    return structured_blocks
