// Store the HTML response from the server (string) in a variable
var htmlParts = [];

// Function that is called when the DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
	// Add an event listener to the #pdf-form form to prevent its default behavior and call the upload
	let pdfForm = document.getElementById("pdf-form");
	pdfForm.addEventListener("submit", function (event) {
		event.preventDefault();
		uploadPDF();
	});

	// On click of button #try-again, try to redirect the user to a new page with the HTML content again
	let tryAgainButton = document.getElementById("try-again");
	tryAgainButton.addEventListener("click", function () {
		redirectToHTMLPages();
	});
});

// Function that takes as input a PDF file inputted by the user in the #pdf-form form and sends a POST request to the server with the PDF file as a FormData object
function uploadPDF() {
	let apiURL = "https://panecaldoaldo.pythonanywhere.com/pdf2html";
	let pdfForm = document.getElementById("pdf-form");
	let pdfFile = pdfForm.elements["pdf"].files[0];
	let debugText = document.getElementById("debug-text");
	debugText.innerHTML = "Uploading PDF file: " + pdfFile.name + "...";
	console.log("Uploading PDF file: " + pdfFile.name + "...");
	let formData = new FormData();
	formData.append("pdf", pdfFile);
	fetch(
		apiURL,
		{
			method: "POST",
			body: formData
		})
		.then(response => response.json())
		.then(data => {
			console.log("Received response from server:");
			console.log(data);
			debugText.innerHTML = "Received response from server!";
			// Open a blank window with the PDF HTML content
			let htmlDocumentsStringList = data["html_documents"];	// List of strings representing chunks of 10 pages each for the PDF
			htmlParts = htmlDocumentsStringList;
			redirectToHTMLPages();
			// Spawn buttons to download each art of the HTML content
			let downloadButtons = document.getElementById("download-buttons");
			for (let i = 0; i < htmlDocumentsStringList.length; i++) {
				let downloadButton = document.createElement("button");
				// On click of button #download, download the HTML response file
				downloadButton.addEventListener("click", function () {
					if (htmlParts.length > i) {
						let blob = new Blob([htmlParts[i]], { type: "text/html" });
						let url = URL.createObjectURL(blob);
						let a = document.createElement("a");
						a.href = url;
						a.download = "pdf_part_" + i + ".html";
						document.body.appendChild(a);
						a.click();
						window.URL.revokeObjectURL(url);
					}
				});
				downloadButton.innerHTML = "Download part " + i;
				downloadButtons.appendChild(downloadButton);
			}

		})
		.catch(error => console.error(error));
}

// Function to redirect the user to a new page with the HTML content again
function redirectToHTMLPages() {
	let useMultipleTabs = document.getElementById("multiple-tabs").checked;
	if (useMultipleTabs) {
		// Open multiple tabs with the PDF HTML content
		if (htmlParts.length > 0) {
			for (let i = 0; i < htmlParts.length; i++) {
				let htmlPart = htmlParts[i];
				// Open a blank window with the PDF HTML content
				let pdfWindow = window.open("", "_blank");
				pdfWindow.document.write(htmlPart);
			}
		}
	} else {
		// Open one new tab with the PDF HTML content, each part inside a different iframe
		let pdfWindow = window.open("", "_blank");
		let htmlContent = "";
		for (let i = 0; i < htmlParts.length; i++) {
			// Add an iframe with the HTML content (allowing to scroll inside the iframe)
			// Add as encoded html "data:text/html;charset=utf-8," + encodeURIComponent(htmlParts[i])
			// Convert "'s to &quot; to avoid breaking the iframe
			// htmlParts[i] = htmlParts[i].replace(/"/g, "&quot;").replace(/'/g, "&quot;");
			// htmlParts[i] = htmlParts[i].replace(/'/g, "&quot;");
			htmlParts[i] = htmlParts[i].replace(/"/g, "&quot;").replace(/'/g, "&quot;");
			htmlContent += "<iframe width='100vw' height='100vh' style='border: none;' scrolling='yes' src='data:text/html;charset=utf-8," + encodeURIComponent(htmlParts[i]) + "'></iframe>";
			// htmlContent += "<iframe width='100vw' height='100vh' style='border: none;' scrolling='yes' srcdoc=" + htmlParts[i] + "'></iframe>";
		}
		// Add a script to dynamically resize the iframe to the content size (after 1 second)
		// htmlContent += "<script>setTimeout(function() { var iframe = document.querySelector('iframe'); iframe.height = iframe.contentWindow.document.body.scrollHeight + 'px'; }, 1000);</script>";
		pdfWindow.document.write(htmlContent);
	}
}