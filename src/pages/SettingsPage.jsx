function SettingsPage() {
  const username = localStorage.getItem("username") || "User";
  const role = localStorage.getItem("role") || "N/A";

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 mb-2">Settings</h1>
      <p className="text-gray-500 mb-8">Manage your account and system preferences</p>

      <div className="bg-white rounded-xl shadow-sm p-6 max-w-md">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Account Information</h2>

        <div className="space-y-4">
          <div className="flex justify-between border-b pb-3">
            <span className="text-gray-500 text-sm">Username</span>
            <span className="font-medium text-gray-800">{username}</span>
          </div>
          <div className="flex justify-between border-b pb-3">
            <span className="text-gray-500 text-sm">Role</span>
            <span className="font-medium text-gray-800 capitalize">{role}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500 text-sm">System Version</span>
            <span className="font-medium text-gray-800">RiskLens AI v1.0</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;