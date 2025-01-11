import React from "react";
import MainLayout from "../Layout/MainLayout";
import Home from '../Pages/Home/Home';

const MainRoutes = {
  path: '/',
  element: React.createElement(MainLayout),
  children: [
    {
      index: true,
      element: React.createElement(Home),
    }
  ]
}

export default MainRoutes;
