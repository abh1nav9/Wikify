import { Outlet } from "react-router-dom";
import NavigationBar from "../Components/layout/NavigationBar";
import Footer from "../Components/layout/Footer";

function MainLayout() {
  return (
    <>
    <NavigationBar />
    <div>
      <Outlet />
    </div>
    <Footer />
    </>
  )
}

export default MainLayout;