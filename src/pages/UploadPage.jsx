import FileUpload from "../components/FileUpload";

function UploadPage() {
  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 mb-2">Upload File</h1>
      <p className="text-gray-500 mb-8">Upload a vulnerability scan report for AI-powered risk analysis</p>
      <FileUpload />
    </div>
  );
}

export default UploadPage;