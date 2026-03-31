import re

import docx.document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches
from docx.text.paragraph import Paragraph


def add_custom_element(caption: Paragraph, name: str, key: str, value: str):
    run = caption.add_run()
    element = OxmlElement(name)
    element.set(qn(key), value)
    run._r.append(element)

    return element


def replace_placeholder_with_figure(doc: docx.document.Document, before: str, field_name: str, caption_text: str):
    for p in doc.paragraphs:
        match = re.match(r"^\{\{ (.+?) \}\}$", p.text)
        if not match:
            continue

        p.text = ""  # Clear the placeholder text
        img_path = f"{match.group(1)}.png"  # Extract the image path from the placeholder

        width = 16 / 2.54  # Convert cm to inches, full width in default document
        p.add_run().add_picture(img_path, width=Inches(width))

        caption_p = p.insert_paragraph_before(style="Caption")
        p._p.addnext(caption_p._p)
        caption_p.add_run(f"{before} ")

        # 1. Begin marker
        add_custom_element(caption_p, "w:fldChar", "w:fldCharType", "begin")

        # 2. Field instruction (SEQ)
        txt = add_custom_element(caption_p, "w:instrText", "xml:space", "preserve")
        txt.text = f" SEQ {field_name} \\* ARABIC "

        # 3. Separate marker
        add_custom_element(caption_p, "w:fldChar", "w:fldCharType", "end")

        # 4. Cached result (placeholder before update)
        caption_p.add_run("<invalid, update fields>")

        # 5. End marker
        add_custom_element(caption_p, "w:fldChar", "w:fldCharType", "end")

        # Add the actual description
        caption_p.add_run(": " + caption_text)


def example():
    document = docx.Document("base.docx")

    replace_placeholder_with_figure(document, "Figure", "Figure", "This is a sample figure.")

    document.save("edited.docx")


if __name__ == "__main__":
    example()
