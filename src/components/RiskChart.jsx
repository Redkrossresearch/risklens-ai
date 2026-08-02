import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Pie } from "react-chartjs-2";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
);

export default function RiskChart({ critical = 0, high = 0, medium = 0, low = 0 }) {
  const data = {
    labels: ["Critical", "High", "Medium", "Low"],
    datasets: [
      {
        data: [critical, high, medium, low],
        backgroundColor: [
          "#ef4444",
          "#f97316",
          "#eab308",
          "#22c55e",
        ],
        borderWidth: 1,
      },
    ],
  };

  return (
    <div style={{ width: "350px", height: "350px" }}>
      <Pie data={data} />
    </div>
  );
}