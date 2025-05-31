import React from 'react';
import { Outlet } from 'react-router-dom';

export const SimpleLayout = () => (
  <div className="min-h-screen bg-gray-100">
    <Outlet />
  </div>
); 