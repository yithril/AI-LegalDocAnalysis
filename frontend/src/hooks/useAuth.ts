'use client'

import { useSession } from 'next-auth/react'
import { useCallback } from 'react'
import { UserRole, hasRole, hasAnyRole, isAdmin, isPM, isAnalyst, isViewer } from '@/lib/roles'

export function useAuth() {
  const { data: session, status } = useSession()

  const isAuthenticated = status === 'authenticated'
  const isLoading = status === 'loading'
  const isUnauthenticated = status === 'unauthenticated'

  const user = session?.user
  const userRole = user?.role || 'viewer'

  // Role checking functions
  const hasPermission = useCallback((requiredRole: UserRole) => {
    return isAuthenticated && hasRole(userRole, requiredRole)
  }, [isAuthenticated, userRole])

  const hasAnyPermission = useCallback((requiredRoles: UserRole[]) => {
    return isAuthenticated && hasAnyRole(userRole, requiredRoles)
  }, [isAuthenticated, userRole])

  // Convenience methods using the imported functions
  const isAdminUser = useCallback(() => isAuthenticated && isAdmin(userRole), [isAuthenticated, userRole])
  const isPMUser = useCallback(() => isAuthenticated && isPM(userRole), [isAuthenticated, userRole])
  const isAnalystUser = useCallback(() => isAuthenticated && isAnalyst(userRole), [isAuthenticated, userRole])
  const isViewerUser = useCallback(() => isAuthenticated && isViewer(userRole), [isAuthenticated, userRole])

  return {
    // Session state
    session,
    user,
    isAuthenticated,
    isLoading,
    isUnauthenticated,
    
    // User info
    userRole,
    
    // Permission checks
    hasPermission,
    hasAnyPermission,
    isAdmin: isAdminUser,
    isPM: isPMUser,
    isAnalyst: isAnalystUser,
    isViewer: isViewerUser
  }
} 