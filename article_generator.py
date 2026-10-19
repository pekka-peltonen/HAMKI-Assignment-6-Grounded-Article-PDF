from openai import OpenAI
from pydantic import BaseModel, Field
import openai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class Section(BaseModel):
    heading: str
    content: str
class Report(BaseModel):
    title: str
    abstract: str
    introduction: str
    sections: list[Section] = Field(min_length=1)
    conclusion: str
    references: list[str] = Field(min_length=1)

def read_sources():
    with open("sources.txt", "r", encoding="utf-8") as file:
        return file.read()


def generate_article(client, topic, sources):
    
    response = client.responses.parse(
        model="gpt-4o-mini",
        input=(
            "Write a short scientific article in English about: "
            + topic
            + "\n\nUse only these sources:\n"
            + sources
            + "\n\nInclude a title, abstract, introduction, "
            "main sections, conclusion and APA-style references. "
            "Use author-year citations in the text. "
            "Each main section must have a heading and a substantive content paragraph. "
            "Do not invent sources or publication details."
        ),
        text_format=Report,
    )

    return response.output_parsed

def create_pdf(article):
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(article.title, styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Abstract", styles["Heading2"]))
    story.append(Paragraph(article.abstract, styles["BodyText"]))

    story.append(Paragraph("Introduction", styles["Heading2"]))
    story.append(Paragraph(article.introduction, styles["BodyText"]))


    for section in article.sections:
        story.append(Spacer(1, 12))
        story.append(Paragraph(section.heading, styles["Heading2"]))
        story.append(Paragraph(section.content, styles["BodyText"]))
    story.append(Paragraph("Conclusion", styles["Heading2"]))
    story.append(Paragraph(article.conclusion, styles["BodyText"]))

    story.append(Paragraph("References", styles["Heading2"]))
    for reference in article.references:
        story.append(Paragraph(reference.replace("*", ""), styles["BodyText"]))

        story.append(Spacer(1, 6))
    pdf = SimpleDocTemplate("article.pdf")
    pdf.build(story)

def main():
    print("HAMKI Assignment #6 - Grounded Article Generator")

    topic = input("Enter article topic: ").strip()

    if not topic:
        print("Error: Please enter a topic.")
        return

    print("Selected topic:", topic)    
    sources = read_sources()
    print("Sources loaded successfully.")

    print("Searching for reliable sources...")

    try:
        client = OpenAI()

        response = client.responses.create(
            model="gpt-5.6",
            tools=[{"type": "web_search"}],
            input=(
                f"Find 3 to 5 reliable scientific or technical sources "
                f"about: {topic}. "
                "Prefer academic publications and official research reports. "
                "For each source provide the author or organization, "
                "publication title, publication year and original URL or DOI. "
                "Do not invent references. "
                "Explain briefly how each source relates to the topic."
            ),
        )



        print("\nSEARCH RESULTS:\n")
        print(response.output_text)
        sources = response.output_text
        article = generate_article(client, topic, sources)
        print("Article generated successfully.")

        create_pdf(article)
        print("PDF saved successfully: article.pdf")
    except openai.APIError as error:
        print(f"Web search failed: {error}")


if __name__ == "__main__":
    main()