'use client';

import { getLogoUrl } from '../lib/theme-utils';

/**
 * Dynamic Logo Component
 * Displays the tenant-specific logo
 */
export default function Logo({ className = '', alt = 'Logo', ...props }) {
  const logoUrl = getLogoUrl();
  
  return (
    <img 
      src={logoUrl} 
      alt={alt}
      className={className}
      {...props}
    />
  );
}
