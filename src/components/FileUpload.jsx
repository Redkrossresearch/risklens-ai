import { useState } from "react";

function FileUpload() {
  const [file, setFile] = useState(null);

  return (
    <div className="border rounded-lg p-4">
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      {file && <p>Selected File: {file.name}</p>}

      <button className="mt-4 border px-4 py-2">
        Upload
      </button>
    </div>
  );
}

export default FileUpload;