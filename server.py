
# Flask endpoint that transforms PDF files into HTML files

from server import Flask, request
from spire.pdf import PdfDocument, FileFormat, Stream
import PyPDF2
from io import BytesIO

# Create a Flask application
app = Flask(__name__)

# Define a route to transform PDF files into HTML files
@app.route('/pdf2html', methods=['POST'])
def pdf2html():
	try:
		# Get the PDF file from the request
		pdf_file = request.files.get('pdf')		# FileStorage object
		# Read the PDF file as a byte array 
		pdf_bytes_data = pdf_file.read()	# bytes object
		# Auxiliary function to convert the PDF file (as a bytes stream) to an HTML file (max 10 pages per conversion)
		def convertPDFPages(pdf_bytes_data):
			#Convert the pdf data to a stream
			pdf_stream = Stream(pdf_bytes_data)
			# Create a PDF document from the stream
			pdf = PdfDocument(pdf_stream)
			# Set the conversion options
			pdf.ConvertOptions.SetPdfToHtmlOptions(True,True)
			# Convert the PDF document to an HTML document
			html_stream = Stream()
			pdf.SaveToStream(html_stream, FileFormat.HTML)
			# Convert the HTML stream to a byte array
			html_bytes_data = html_stream.ToArray()
			bytes_object = bytes(html_bytes_data)
			# Return the HTML document as a string
			return bytes_object.decode('utf-8')
		# Auxiliary function to split the PDF file into chunks of 10 pages using the library PyPDF2, returning a list of byte arrays
		def splitPDFPages(pdf_bytes_data):
			# Create a PdfFileReader object from the PDF file
			pdf_reader = PyPDF2.PdfFileReader(BytesIO(pdf_bytes_data))
			# Get the number of pages in the PDF file
			num_pages = pdf_reader.getNumPages()
			# Initialize the list of byte arrays
			pdf_chunks = []
			# Split the PDF file into chunks of 10 pages
			for i in range(0, num_pages, 10):
				# Create a PdfFileWriter object
				pdf_writer = PyPDF2.PdfFileWriter()
				# Add 10 pages to the PdfFileWriter object
				for j in range(i, min(i+10, num_pages)):
					pdf_writer.addPage(pdf_reader.getPage(j))
				# Create a byte array from the PdfFileWriter object
				pdf_chunk = BytesIO()
				pdf_writer.write(pdf_chunk)
				# Add the byte array to the list
				pdf_chunks.append(pdf_chunk.getvalue())
			# Return the list of byte arrays
			return pdf_chunks
		# Split the PDF file into chunks of 10 pages
		pdf_chunks = splitPDFPages(pdf_bytes_data)
		# Initialize the list of HTML documents
		html_documents = []
		# Convert each chunk of 10 pages into an HTML document
		for pdf_chunk in pdf_chunks:
			html_document = convertPDFPages(pdf_chunk)
			html_documents.append(html_document)
		# Return the list of HTML documents
		return {
			'html_documents': html_documents	# List of HTML document strings
		}
	except Exception as e:
		# Return an error message if an exception occurs
		return {
			'error': str(e)	# Error message
		}
