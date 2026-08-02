import { useState, useEffect } from "react";
import DashboardCard from "../components/DashboardCard";
import RiskChart from "../components/RiskChart";

function DashboardPage() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8001/api/stats")
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.error("Failed to load stats:", err));
  }, []);

  const total = stats ? stats.total_vulnerabilities : 0;
  const highRisk = stats ? stats.critical + stats.high : 0;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">
        Dashboard
      </h1>
      <div className="flex gap-4 mb-8">
        <DashboardCard title="Total Vulnerabilities" value={total} />
        <DashboardCard title="High Risk" value={highRisk} />
      </div>
      <RiskChart
        critical={stats ? stats.critical : 0}
        high={stats ? stats.high : 0}
        medium={stats ? stats.medium : 0}
        low={stats ? stats.low : 0}
      />
    </div>
  );
}

export default DashboardPage;