function DashboardCard({ title, value, color = "blue" }) {
  const colorClasses = {
    blue: "border-blue-500 text-blue-600",
    red: "border-red-500 text-red-600",
    orange: "border-orange-500 text-orange-600",
    yellow: "border-yellow-500 text-yellow-600",
    green: "border-green-500 text-green-600",
  };

  return (
    <div className={`bg-white rounded-xl shadow-sm p-5 border-l-4 ${colorClasses[color]}`}>
      <p className="text-sm text-gray-500 mb-1">{title}</p>
      <p className="text-3xl font-bold text-gray-800">{value}</p>
    </div>
  );
}

export default DashboardCard;