import base64
import base64
import PyPDF2
import io

def pdf_to_base64(file_path):
    with open(file_path, "rb") as pdf_file:
        # Read the PDF file content
        pdf_content = pdf_file.read()

        # Encode the binary content to Base64
        base64_encoded = base64.b64encode(pdf_content).decode("utf-8")

        return base64_encoded

def convert(pdf_file_path) -> str:
    # Specify the path to your PDF file
    # pdf_file_path = "path/to/your/file.pdf"

    # Convert PDF to Base64
    base64_content = pdf_to_base64(pdf_file_path)

    # Print the Base64 content
    # print(base64_content)

    return base64_content

# Function to extract text from base64-encoded PDF
def extract_text_from_base64_pdf(base64_content):
    decoded_content = base64.b64decode(base64_content)
    reader = PyPDF2.PdfReader(io.BytesIO(decoded_content))
    text = ""
    for page_num in range(len(reader.pages)):
        text += reader.pages[page_num].extract_text()
    return text


if __name__ == "__main__":
    content = convert("./article_c.pdf")
    print("extracting text: ")
    text = extract_text_from_base64_pdf(content)
    print(text)