from src.pdf_parser import PDFParser
import traceback

try:
    parser = PDFParser()
    result = parser.extract_from_pdf('data/samples/Insurance_Handbook_20103.pdf')
    print(f'Success!')
    print(f'Metadata: {result.metadata}')
    print(f'Text chunks: {len(result.text_chunks)}')
    print(f'Tables: {len(result.tables)}')
    print(f'Images: {len(result.images)}')
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
