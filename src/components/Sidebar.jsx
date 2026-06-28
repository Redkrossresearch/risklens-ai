import { Link, useLocation } from "react-router-dom";

const links = [
  { label: "Upload", path: "/" },
  { label: "Dashboard", path: "/dashboard" },
];

export default function Sidebar() {
  const { pathname } = useLocation();
  return (
    <aside className="w-56 bg-white border-r border-gray-200 flex flex-col p-4">
      <h1 className="text-xl font-bold text-blue-600 mb-8">RiskLens AI</h1>
      <nav className="flex flex-col gap-2">
        {links.map((link) => (
          <Link
            key={link.path}
            to={link.path}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              pathname === link.path
                ? "bg-blue-50 text-blue-600"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}