import re


SECTION_PATTERN = re.compile(r"(Section\s+\d+[A-Z]*)", re.IGNORECASE)
CLAUSE_PATTERN = re.compile(r"^\(?[a-zA-Z0-9]+\)", re.IGNORECASE)


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

            # 🔹 Detect Section
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

            # 🔹 Detect Clause
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

            # 🔹 Default paragraph
            structured_blocks.append({
                "type": "paragraph",
                "section": current_section,
                "text": line,
                "page": page_number
            })

    return structured_blocks