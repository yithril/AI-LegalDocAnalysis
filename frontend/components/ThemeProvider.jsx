'use client';

import { useEffect } from 'react';
import { applyTheme } from '../lib/theme-utils';

/**
 * Theme Provider Component
 * Applies tenant-specific CSS variables to the document root
 */
export default function ThemeProvider({ children }) {
  useEffect(() => {
    // Apply theme when component mounts
    applyTheme();
  }, []);

  return <>{children}</>;
} 