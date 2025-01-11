import { Outlet } from "react-router-dom";
import NavigationBar from "../Components/NavigationBar";
import Footer from "../Components/Footer";

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