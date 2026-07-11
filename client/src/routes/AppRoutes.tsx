import { Routes, Route } from "react-router-dom";

import Layout from "@/components/layout/Layout";
import LandingPage from "@/pages/LandingPage";
import DashboardPage from "@/pages/DashboardPage";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
      </Route>
    </Routes>
  );
}
