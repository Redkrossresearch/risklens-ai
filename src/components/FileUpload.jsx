import { useState } from "react";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleUpload = async () => {
    if (!file) {
      setMessage({ type: "error", text: "Please select a file" });
      return;
    }

    let uploadUrl = "";
    const extension = file.name.split(".").pop().toLowerCase();
    if (extension === "pdf") {
      uploadUrl = "http://127.0.0.1:8001/upload/pdf";
    } else if (extension === "csv") {
      uploadUrl = "http://127.0.0.1:8001/upload/csv";
    } else if (extension === "xlsx") {
      uploadUrl = "http://127.0.0.1:8001/upload/xlsx";
    } else {
      setMessage({ type: "error", text: "Only PDF, CSV and XLSX files are supported." });
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    setMessage(null);

    try {
      const response = await fetch(uploadUrl, {
        method: "POST",
        body: formData,
      });
      const result = await response.json();

      if (response.ok) {
        setMessage({ type: "success", text: `Successfully analyzed ${result.total} vulnerabilities.` });
      } else {
        setMessage({ type: "error", text: "Upload failed" });
      }
    } catch (error) {
      setMessage({ type: "error", text: "Backend connection failed" });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-8 w-full max-w-lg">
      <h2 className="text-xl font-semibold text-gray-800 mb-2">Upload Vulnerability Report</h2>
      <p className="text-gray-500 text-sm mb-6">Supports CSV, XLSX, and PDF formats (Nessus, Qualys compatible)</p>

      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-4">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="w-full"
        />
        {file && <p className="text-sm text-gray-600 mt-2">Selected: {file.name}</p>}
      </div>

      {message && (
        <div
          className={`mb-4 p-3 rounded-lg text-sm ${
            message.type === "success"
              ? "bg-green-50 text-green-700 border border-green-200"
              : "bg-red-50 text-red-700 border border-red-200"
          }`}
        >
          {message.text}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={uploading}
        className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-6 py-2.5 rounded-lg font-medium w-full transition"
      >
        {uploading ? "Analyzing with AI... (this may take a minute)" : "Upload & Analyze"}
      </button>
    </div>
  );
}

export default FileUpload;