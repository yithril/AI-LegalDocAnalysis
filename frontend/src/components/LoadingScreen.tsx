'use client'

import { ReactNode } from 'react'
import Image from 'next/image'
import { useTheme } from './providers/ThemeProvider'

interface LoadingScreenProps {
  message?: string
  size?: 'sm' | 'md' | 'lg'
  showLogo?: boolean
}

export default function LoadingScreen({ 
  message = "Loading...", 
  size = 'lg',
  showLogo = true
}: LoadingScreenProps) {
  const { theme } = useTheme()
  
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-16 w-16', 
    lg: 'h-32 w-32'
  }

  return (
    <div 
      className="min-h-screen flex items-center justify-center"
      style={{ backgroundColor: theme.backgroundColor }}
    >
      <div className="text-center">
        {/* Tenant Logo */}
        {showLogo && (
          <div className="mb-8">
            <Image
              src={theme.logo}
              alt={theme.logoAlt}
              width={200}
              height={80}
              className="mx-auto"
              priority
            />
          </div>
        )}
        
        {/* Animated spinner */}
        <div 
          className={`animate-spin rounded-full border-b-2 mx-auto mb-4 ${sizeClasses[size]}`}
          style={{ borderColor: theme.accentColor }}
        ></div>
        
        {/* Loading message */}
        <p 
          className="text-lg font-medium mb-4"
          style={{ color: theme.textColor }}
        >
          {message}
        </p>
        
        {/* Optional: Dots animation */}
        <div className="flex justify-center space-x-1">
          <div 
            className="w-2 h-2 rounded-full animate-bounce"
            style={{ backgroundColor: theme.accentColor }}
          ></div>
          <div 
            className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"
            style={{ 
              backgroundColor: theme.accentColor,
              animationDelay: '0.1s' 
            }}
          ></div>
          <div 
            className="w-2 h-2 rounded-full animate-bounce"
            style={{ 
              backgroundColor: theme.accentColor,
              animationDelay: '0.2s' 
            }}
          ></div>
        </div>
      </div>
    </div>
  )
} 