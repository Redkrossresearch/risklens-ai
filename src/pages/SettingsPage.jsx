function SettingsPage() {
  const username = localStorage.getItem("username") || "User";
  const role = localStorage.getItem("role") || "N/A";

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>
      <div className="bg-white p-6 rounded-lg shadow w-96">
        <h2 className="text-xl font-bold mb-4">Account Information</h2>
        <div className="mb-4">
          <p className="text-sm text-gray-500">Username</p>
          <p className="text-lg font-medium">{username}</p>
        </div>
        <div className="mb-4">
          <p className="text-sm text-gray-500">Role</p>
          <p className="text-lg font-medium capitalize">{role}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">System</p>
          <p className="text-lg font-medium">RiskLens AI v1.0</p>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;