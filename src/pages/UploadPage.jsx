import Navbar from "../components/Navbar";
import FileUpload from "../components/FileUpload";

function UploadPage() {
  return (
    <div className="flex-1 bg-gray-100 min-h-screen">
      <Navbar />

      <div className="p-6">
        <FileUpload />
      </div>
    </div>
  );
}

export default UploadPage;