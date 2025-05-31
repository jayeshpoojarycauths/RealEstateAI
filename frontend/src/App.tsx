import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { DashboardPage } from './pages/DashboardPage';
import { LeadsPage } from './pages/LeadsPage';
import { LeadUploadPage } from './pages/LeadUploadPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { LoginPage } from './pages/LoginPage';
import { PrivateRoute } from './components/PrivateRoute';
import { useMaterialTailwind } from './hooks/useMaterialTailwind';
import { Typography } from '@material-tailwind/react';
import { ProfilePage } from './pages/ProfilePage';
import { OutreachPage } from './pages/OutreachPage';
import { Stats } from './pages/Stats';
import { MFAVerification } from './components/auth/MFAVerification';
import { SimpleLayout } from './layouts/SimpleLayout';
import { LeadsNewPage } from './pages/LeadsNewPage';
import { LeadsImportExportPage } from './pages/LeadsImportExportPage';

const router = {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
  },
};

const App: React.FC = () => {
  const { getTypographyProps } = useMaterialTailwind();

  return (
    <BrowserRouter future={router.future}>
      <Routes>
        {/* Auth routes: use SimpleLayout */}
        <Route element={<SimpleLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/mfa-verify" element={<MFAVerification />} />
        </Route>

        {/* Dashboard routes: use DashboardLayout and PrivateRoute */}
        <Route element={<PrivateRoute><DashboardLayout /></PrivateRoute>}>
          <Route index element={<Navigate to="/leads" replace />} />
          <Route path="leads" element={<LeadsPage />} />
          <Route path="leads/new" element={<LeadsNewPage />} />
          <Route path="leads/import-export" element={<LeadsImportExportPage />} />
          <Route path="leads/upload" element={<LeadUploadPage />} />
          <Route path="projects" element={<ProjectsPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="outreach" element={<OutreachPage />} />
          <Route path="stats" element={<Stats />} />
          <Route path="dashboard" element={<DashboardPage />} />
        </Route>

        {/* 404 route */}
        <Route
          path="*"
          element={
            <div className="flex items-center justify-center h-full">
              <Typography
                variant="h4"
                color="blue-gray"
                {...getTypographyProps() as any}
                onResize={undefined}
                onResizeCapture={undefined}
                onPointerEnterCapture={undefined}
                onPointerLeaveCapture={undefined}
                placeholder={undefined}
              >
                404 - Page Not Found
              </Typography>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
};

export default App; 