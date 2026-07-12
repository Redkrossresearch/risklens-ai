function Sidebar() {
  return (
    <div className="w-64 h-screen bg-gray-900 text-white p-5">
      <h1 className="text-2xl font-bold mb-8">
        RiskLens AI
      </h1>

      <ul className="space-y-4">
        <li className="cursor-pointer hover:text-blue-400">
          Dashboard
        </li>

        <li className="cursor-pointer hover:text-blue-400">
          Upload File
        </li>

        <li className="cursor-pointer hover:text-blue-400">
          Reports
        </li>

        <li className="cursor-pointer hover:text-blue-400">
          Settings
        </li>
      </ul>
    </div>
  );
}

export default Sidebar;