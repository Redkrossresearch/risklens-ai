import DashboardCard from "../components/DashboardCard";
import RiskChart from "../components/RiskChart";

function DashboardPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">
        Dashboard
      </h1>

      <div className="flex gap-4 mb-8">
        <DashboardCard title="Total Hosts" value="25" />
        <DashboardCard title="High Risk" value="6" />
      </div>

      <RiskChart />
    </div>
  );
}

export default DashboardPage;