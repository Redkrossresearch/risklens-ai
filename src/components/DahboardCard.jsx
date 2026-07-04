function DashboardCard({ title, value }) {
  return (
    <div className="border rounded-lg p-4 shadow">
      <h3>{title}</h3>
      <h2>{value}</h2>
    </div>
  );
}

export default DashboardCard;