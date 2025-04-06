import { Outlet } from "react-router-dom";
import NavigationBar from "../Components/layout/NavigationBar";
import Footer from "../Components/layout/Footer";

function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      <NavigationBar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

export default MainLayout;
