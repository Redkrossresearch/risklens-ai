function ReportsPage() {
  const downloadExecutive = () => {
    window.open("http://127.0.0.1:8001/report/executive/download", "_blank");
  };

  const downloadTechnical = () => {
    window.open("http://127.0.0.1:8001/report/technical/download", "_blank");
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Reports</h1>
      <div className="flex gap-4">
        <div className="bg-white p-6 rounded-lg shadow w-72">
          <h2 className="text-xl font-bold mb-4">Executive Report</h2>
          <p className="text-gray-600 mb-4">High-level summary for leadership.</p>
          <button
            onClick={downloadExecutive}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            Download PDF
          </button>
        </div>
        <div className="bg-white p-6 rounded-lg shadow w-72">
          <h2 className="text-xl font-bold mb-4">Technical Report</h2>
          <p className="text-gray-600 mb-4">Detailed vulnerability breakdown.</p>
          <button
            onClick={downloadTechnical}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            Download PDF
          </button>
        </div>
      </div>
    </div>
  );
}

export default ReportsPage;