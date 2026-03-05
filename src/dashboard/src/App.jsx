import { Analytics } from "@vercel/analytics/react";
import Navigation from "./components/layout/Navigation";
import Footer from "./components/layout/Footer";
import AppRoutes from "./routes";

export default function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navigation />
      <AppRoutes />
      <Footer />
      <Analytics />
    </div>
  );
}
