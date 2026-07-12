 import { useState } from "react";

function FileUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setMessage("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      // Replace this URL with your teammate's backend URL
      const response = await fetch("http://localhost:8000/api/upload",  {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        setMessage("✅ File uploaded successfully!");
      } else {
        setMessage("❌ Upload failed.");
      }
    } catch (error) {
      console.error(error);
      setMessage("❌ Cannot connect to backend.");
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-lg">
      <h2 className="text-3xl font-bold mb-6">
        Upload File
      </h2>

      <div className="flex items-center gap-4">
        <input
          type="file"
          onChange={handleFileChange}
          className="border p-2 rounded"
        />

        <button
          onClick={handleUpload}
          className="bg-blue-600 text-white px-5 py-2 rounded hover:bg-blue-700"
        >
          Upload
        </button>
      </div>

      {message && (
        <p className="mt-4 font-medium">
          {message}
        </p>
      )}
    </div>
  );
}

export default FileUpload;