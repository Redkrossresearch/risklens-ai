function ReportsPage() {
  const downloadExecutive = () => {
    window.open("http://127.0.0.1:8001/report/executive/download", "_blank");
  };

  const downloadTechnical = () => {
    window.open("http://127.0.0.1:8001/report/technical/download", "_blank");
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 mb-2">Reports</h1>
      <p className="text-gray-500 mb-8">Generate and download PDF reports for stakeholders</p>

      <div className="grid grid-cols-2 gap-6 max-w-3xl">
        <div className="bg-white rounded-xl shadow-sm p-6 border-t-4 border-red-500">
          <h2 className="text-lg font-semibold text-gray-800 mb-2">Executive Report</h2>
          <p className="text-gray-500 text-sm mb-6">
            High-level summary of risk posture and compliance status, designed for leadership review.
          </p>
          <button
            onClick={downloadExecutive}
            className="bg-red-500 hover:bg-red-600 text-white px-5 py-2.5 rounded-lg font-medium w-full transition"
          >
            Download PDF
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border-t-4 border-blue-500">
          <h2 className="text-lg font-semibold text-gray-800 mb-2">Technical Report</h2>
          <p className="text-gray-500 text-sm mb-6">
            Detailed vulnerability breakdown with remediation steps, for security teams.
          </p>
          <button
            onClick={downloadTechnical}
            className="bg-blue-500 hover:bg-blue-600 text-white px-5 py-2.5 rounded-lg font-medium w-full transition"
          >
            Download PDF
          </button>
        </div>
      </div>
    </div>
  );
}

export default ReportsPage;