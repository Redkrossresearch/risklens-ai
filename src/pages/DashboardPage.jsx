import DashboardCard from "../components/DashboardCard";

function DashboardPage() {
  return (
    <div className="flex gap-5 mb-8">

<DashboardCard
title="Total Hosts"
value="25"
/>

<DashboardCard
title="High Risk"
value="6"
/>

<DashboardCard
title="Medium Risk"
value="12"
/>

<DashboardCard
title="Low Risk"
value="7"
/>

</div>
  );
}

export default DashboardPage;