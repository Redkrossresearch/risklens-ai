 import { BrowserRouter, Routes, Route } from "react-router-dom";
 import Sidebar from "./components/Sidebar";
 import UploadPage from "./pages/UploadPage";
 import DashboardPage from "./pages/DashboardPage";

 export default function App() {
 return (
 <BrowserRouter>
 <div className="flex h-screen bg-gray-50">
 <Sidebar />
 <main className="flex-1 overflow-auto p-6">
 <Routes>
 <Route path="/" element={<UploadPage />} />
 <Route path="/dashboard" element={<DashboardPage />} />
 </Routes>
 </main>
 </div>
 </BrowserRouter>
);
}
