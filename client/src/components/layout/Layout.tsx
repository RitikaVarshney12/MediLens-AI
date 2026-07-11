import { Outlet } from "react-router-dom";

import Header from "@/components/layout/Header";
import DisclaimerBanner from "@/components/ui/DisclaimerBanner";

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-surface-subtle">
      <Header />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">
        <Outlet />
      </main>
      <DisclaimerBanner />
    </div>
  );
}
