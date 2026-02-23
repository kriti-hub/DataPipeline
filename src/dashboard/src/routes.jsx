import { Routes, Route } from "react-router-dom";
import Hero from "./pages/Hero";
import Architecture from "./pages/Architecture";
import StaffingDashboard from "./pages/StaffingDashboard";
import DataQuality from "./pages/DataQuality";
import SQLShowcase from "./pages/SQLShowcase";
import HowIBuiltThis from "./pages/HowIBuiltThis";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Hero />} />
      <Route path="/architecture" element={<Architecture />} />
      <Route path="/dashboard" element={<StaffingDashboard />} />
      <Route path="/data-quality" element={<DataQuality />} />
      <Route path="/sql-showcase" element={<SQLShowcase />} />
      <Route path="/how-i-built-this" element={<HowIBuiltThis />} />
    </Routes>
  );
}
