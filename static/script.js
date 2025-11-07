const optionSelect = document.getElementById("option");
const linkSection = document.getElementById("link-section");
const imageSection = document.getElementById("image-section");
const fileSection = document.getElementById("file-section");
const generateBtn = document.getElementById("generateBtn");
const qrImage = document.getElementById("qrImage");
const resultDiv = document.getElementById("result");
const downloadLink = document.getElementById("downloadLink");

// Show/hide input sections based on dropdown
optionSelect.addEventListener("change", () => {
  const value = optionSelect.value;
  linkSection.classList.add("hidden");
  imageSection.classList.add("hidden");
  fileSection.classList.add("hidden");

  if (value === "link") linkSection.classList.remove("hidden");
  else if (value === "image") imageSection.classList.remove("hidden");
  else if (value === "file") fileSection.classList.remove("hidden");
});

// Handle QR generation
generateBtn.addEventListener("click", async () => {
  const selected = optionSelect.value;
  let endpoint = "";
  let formData = new FormData();

  if (selected === "link") {
    const link = document.getElementById("linkInput").value.trim();
    if (!link) return alert("Please enter a valid link!");
    endpoint = "https://qr-generator-bniq.onrender.com/generate-qr-text/";
    formData.append("link", link);
  } else if (selected === "image") {
    const file = document.getElementById("imageInput").files[0];
    if (!file) return alert("Please upload an image file!");
    endpoint = "https://qr-generator-bniq.onrender.com/generate-qr-image/";
    formData.append("file", file);
  } else if (selected === "file") {
    const file = document.getElementById("fileInput").files[0];
    if (!file) return alert("Please upload a file!");
    endpoint = "https://qr-generator-bniq.onrender.com/generate-qr-file/";
    formData.append("file", file);
  }

  // Disable button while generating
  generateBtn.disabled = true;
  generateBtn.textContent = "Generating...";

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      body: formData,
    });

    const contentType = response.headers.get("content-type");

    // Handle errors
    if (!response.ok) {
      if (contentType && contentType.includes("application/json")) {
        const err = await response.json();
        alert("Error: " + (err.error || "Something went wrong."));
      } else {
        alert("Error: Something went wrong.");
      }
      return;
    }

    // Success — show QR
    const blob = await response.blob();
    const qrUrl = URL.createObjectURL(blob);

    qrImage.src = qrUrl;
    downloadLink.href = qrUrl;
    resultDiv.classList.remove("hidden");
  } catch (error) {
    alert("Error generating QR: " + error);
  } finally {
    // ✅ Always re-enable button
    generateBtn.disabled = false;
    generateBtn.textContent = "Generate QR";
  }
});
