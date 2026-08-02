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
  const critical = stats ? stats.critical : 0;
  const medium = stats ? stats.medium : 0;

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 mb-2">Dashboard</h1>
      <p className="text-gray-500 mb-8">Overview of your organization's security posture</p>

      <div className="grid grid-cols-4 gap-6 mb-8">
        <DashboardCard title="Total Vulnerabilities" value={total} color="blue" />
        <DashboardCard title="Critical" value={critical} color="red" />
        <DashboardCard title="High Risk" value={highRisk} color="orange" />
        <DashboardCard title="Medium" value={medium} color="yellow" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Risk Distribution</h2>
          <RiskChart
            critical={stats ? stats.critical : 0}
            high={stats ? stats.high : 0}
            medium={stats ? stats.medium : 0}
            low={stats ? stats.low : 0}
          />
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Compliance Scores</h2>
          <div className="space-y-3">
            {stats && stats.compliance &&
              Object.entries(stats.compliance).map(([framework, score]) => (
                <div key={framework}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{framework}</span>
                    <span className="font-medium">{score}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        score >= 75 ? "bg-green-500" : score >= 55 ? "bg-yellow-500" : "bg-red-500"
                      }`}
                      style={{ width: `${score}%` }}
                    ></div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;