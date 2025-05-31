import React from 'react';
import { useLocation } from 'react-router-dom';

const EXCLUDE_BG_PATHS = [/^\/login/, /^\/mfa/];

export const BackgroundImage = () => {
  const { pathname } = useLocation();
  const shouldHide = EXCLUDE_BG_PATHS.some((re) => re.test(pathname));
  if (shouldHide) return null;
  return (
    <div className="absolute top-0 h-full w-full bg-[url('/img/background-3.png')] bg-cover bg-center -z-10" />
  );
}; 