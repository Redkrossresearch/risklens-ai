 import { useState } from "react";

function FileUpload() {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    let uploadUrl = "";

    const extension = file.name.split(".").pop().toLowerCase();

    if (extension === "pdf") {
      uploadUrl = "http://127.0.0.1:8000/upload/pdf";
    } else if (extension === "csv") {
      uploadUrl = "http://127.0.0.1:8000/upload/csv";
    } else if (extension === "xlsx") {
      uploadUrl = "http://127.0.0.1:8000/upload/xlsx";
    } else {
      alert("Only PDF, CSV and XLSX files are supported.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(uploadUrl, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      console.log(result);

      if (response.ok) {
        alert("File uploaded successfully!");
      } else {
        alert("Upload failed");
      }
    } catch (error) {
      console.error(error);
      alert("Backend connection failed");
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow w-96">
      <h2 className="text-2xl font-bold mb-4">
        Upload File
      </h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button
        onClick={handleUpload}
        className="bg-blue-600 text-white px-4 py-2 rounded mt-4"
      >
        Upload
      </button>
    </div>
  );
}

export default FileUpload;