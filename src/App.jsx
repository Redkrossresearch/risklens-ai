import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import DashboardPage from "./pages/DashboardPage";
import UploadPage from "./pages/UploadPage";

function App() {
  return (
    <div className="flex">
      <Sidebar />

      <div className="flex-1">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;