import React from 'react';
import { Outlet } from 'react-router-dom';
import { BackgroundImage } from '../components/BackgroundImage';

const DashboardLayout = () => (
  <div className="relative min-h-screen">
    <BackgroundImage />
    <Outlet />
  </div>
);

export default DashboardLayout; 