 import { useState } from "react";

function FileUpload() {
  const [file, setFile] = useState(null);

  return (
    <div className="bg-white p-6 rounded-lg shadow-md w-[500px]">
      <h2 className="text-2xl font-bold mb-4">Upload File</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />

      {file && (
        <p className="mb-4 text-green-600">
          Selected File: {file.name}
        </p>
      )}

      <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Upload
      </button>
    </div>
  );
}

export default FileUpload;