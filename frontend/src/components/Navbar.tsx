'use client'

import { useSession, signOut } from 'next-auth/react'
import { useTheme } from '@/components/providers/ThemeProvider'
import { getRoleDisplayName } from '@/lib/roles'

export default function Navbar() {
  const { data: session, status } = useSession()
  const { theme } = useTheme()
  const isAuthenticated = status === 'authenticated'
  const isLoading = status === 'loading'

  const handleLogout = async () => {
    await signOut({ callbackUrl: '/auth/signin' })
  }

  return (
    <nav 
      className="bg-white shadow-sm border-b"
      style={{ borderColor: theme.secondaryColor }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Brand */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 
                className="text-xl font-bold"
                style={{ color: theme.textColor }}
              >
                {theme.name}
              </h1>
            </div>
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {isLoading ? (
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"></div>
            ) : isAuthenticated ? (
              <div className="flex items-center space-x-4">
                {/* User Info */}
                <div className="hidden md:block">
                  <div className="text-sm">
                    <p 
                      className="font-medium"
                      style={{ color: theme.textColor }}
                    >
                      {session?.user?.name || session?.user?.email}
                    </p>
                    <p 
                      className="text-xs"
                      style={{ color: theme.secondaryColor }}
                    >
                      {getRoleDisplayName(session?.user?.role || 'viewer')}
                    </p>
                  </div>
                </div>

                {/* Logout Button */}
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                  style={{ backgroundColor: theme.accentColor }}
                >
                  Sign out
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <a
                  href="/auth/signin"
                  className="text-sm font-medium"
                  style={{ color: theme.accentColor }}
                >
                  Sign in
                </a>
                <a
                  href="/auth/signup"
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                  style={{ backgroundColor: theme.accentColor }}
                >
                  Sign up
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
} 