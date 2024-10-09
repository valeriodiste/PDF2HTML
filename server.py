
# Flask endpoint that transforms PDF files into HTML files

# Check if running locally or on a PythonAnywhere server (and import the Flask library accordingly)
running_locally = False
try:
	from server import Flask, request
except ImportError:
	running_locally = True

from spire.pdf import PdfDocument, FileFormat, Stream
import PyPDF2
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_text_to_fp
from io import BytesIO
from pdfminer.converter import HTMLConverter

# Create a Flask application
app = None
if not running_locally:
	app = Flask(__name__)
else:
	# Add a fake function ".route" to the Flask "app" object to avoid errors when running locally
	def fake_route(*args, **kwargs):
		def wrapper(func):
			return func
		return wrapper
	app = type('FakeFlask', (object,), {'route': fake_route})()

# Define a route to transform PDF files into HTML files
@app.route('/pdf2html', methods=['POST'])
def pdf2html():
	try:
		# Get the URL parameter 'simple' from the request
		simple_convertion = request.args.get('simple') == 'true'
		# Get the PDF file from the request
		pdf_file = request.files.get('pdf')		# FileStorage object
		# Read the PDF file as a byte array 
		pdf_bytes_data = pdf_file.read()	# bytes object
		# Convert the PDF file to an HTML file (using either simple or advanced conversion)
		response = convertPDF(pdf_bytes_data, simple_convertion)
		# Return the response as a JSON object
		return response
	except Exception as e:
		# Return an error message if an exception occurs
		return {
			'error': str(e)	# Error message
		}
def convertPDF(pdf_bytes_data, simple_conversion):
	if simple_conversion:
		# Use the pdfminer library to convert the received PDF file into an HTML file
		# Create an in-memory buffer to store the HTML output
		output_buffer = BytesIO()
		# Convert the PDF to HTML and write the HTML to the buffer
		# laParams = LAParams(
		# 	line_overlap=0.5,
		# 	char_margin=0.2,
		# 	line_margin=0.5,
		# 	word_margin=0.175,
		# 	boxes_flow=0.5,
		# 	detect_vertical=True,
		# 	all_texts=False
		# )
		laParams = LAParams()
		method = 'html'
		# method = 'text'
		# layout_mode = 'exact'
		layout_mode = 'normal'
		extract_text_to_fp(BytesIO(pdf_bytes_data), output_buffer, output_type=method, codec='utf-8', laparams=laParams, layoutmode=layout_mode)
		# Retrieve the HTML content from the buffer
		html_bytes_obj = output_buffer.getvalue()
		# Return the HTML content as a string
		html_str = html_bytes_obj.decode('utf-8')
		html_documents = [html_str]
		return {
			'html_documents': html_documents	# List of HTML document strings
		}
	else:
		# Use the spire.pdf library to convert PDF files to 1:1 replicas as HTML files
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

# For debug, test the endpoint locally by simply calling the pdf2html function with a PDF file
# NOTE: don't include this function in the actual server
if __name__ == '__main__':
	# Create a PDF file object
	pdf_file = open('./test.pdf', 'rb')
	# Call the pdf2html function with the request object
	print("\nCalling the pdf2html function with a PDF file...")
	response = convertPDF(pdf_file.read(), True)
	print("> Response received")
	# Sabe the response text to a file
	html_file_name = './test.html'
	html_file = open(html_file_name, 'w', encoding='utf-8')
	html_file.write(response['html_documents'][0])
	print("HTML file saved as \"", html_file_name , "\"", sep='')
	# Close the HTML file
	html_file.close()
	# Close the PDF file
	pdf_file.close()
	