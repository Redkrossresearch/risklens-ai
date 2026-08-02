import { useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const username = localStorage.getItem("username") || "User";
  const role = localStorage.getItem("role") || "";

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("username");
    navigate("/login");
  };

  return (
    <div className="bg-white shadow p-4 flex justify-between items-center">
      <h1 className="text-2xl font-bold">RiskLens AI Dashboard</h1>
      <div className="flex items-center gap-4">
        <p className="text-gray-600">
          Welcome, {username} ({role}) 👋
        </p>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-3 py-1 rounded text-sm"
        >
          Logout
        </button>
      </div>
    </div>
  );
}

export default Navbar;