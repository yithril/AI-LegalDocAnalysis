'use client'

import { createContext, useContext, ReactNode } from 'react'
import { TenantTheme, getCurrentTenantTheme } from '@/lib/tenant-themes'

interface ThemeContextType {
  theme: TenantTheme
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const theme = getCurrentTenantTheme()

  return (
    <ThemeContext.Provider value={{ theme }}>
      <div 
        className="min-h-screen"
        style={{
          '--tenant-primary-color': theme.primaryColor,
          '--tenant-secondary-color': theme.secondaryColor,
          '--tenant-background-color': theme.backgroundColor,
          '--tenant-text-color': theme.textColor,
          '--tenant-accent-color': theme.accentColor,
        } as React.CSSProperties}
      >
        {children}
      </div>
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
} 