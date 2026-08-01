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

const data = {
  labels: ["Critical", "High", "Medium", "Low"],
  datasets: [
    {
      data: [12, 19, 8, 15],
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

export default function RiskChart() {
  return (
    <div style={{ width: "350px", height: "350px" }}>
      <Pie data={data} />
    </div>
  );
}