'use client'

import { ReactNode, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useRouter, usePathname } from 'next/navigation'

interface ProtectedRouteProps {
  children: ReactNode
  redirectTo?: string
}

export default function ProtectedRoute({ 
  children, 
  redirectTo = '/auth/signin' 
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  // Define public routes that don't require authentication
  const publicRoutes = ['/auth/signin', '/auth/signup']
  const isPublicRoute = publicRoutes.includes(pathname)

  useEffect(() => {
    if (!isLoading && !isAuthenticated && !isPublicRoute) {
      router.push(redirectTo)
    }
  }, [isAuthenticated, isLoading, router, redirectTo, isPublicRoute])

  // Show simple loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  // Allow access to public routes even when not authenticated
  if (isPublicRoute) {
    return <>{children}</>
  }

  // Don't render children if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
} 