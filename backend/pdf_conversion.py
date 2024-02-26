import base64

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
    print(base64_content)

    return base64_content


if __name__ == "__main__":
    convert("./article_a.pdf")