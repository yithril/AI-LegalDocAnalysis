'use client'

import { useSession } from 'next-auth/react'
import { useCallback } from 'react'

interface UseAuthenticatedFetchOptions {
  onError?: (error: string) => void
}

export function useAuthenticatedFetch(options: UseAuthenticatedFetchOptions = {}) {
  const { data: session } = useSession()

  const authenticatedFetch = useCallback(async (
    url: string, 
    options: RequestInit = {}
  ): Promise<Response> => {
    if (!session?.accessToken) {
      const error = 'No authentication token available'
      options.onError?.(error)
      throw new Error(error)
    }

    const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}${url}`
    
    const response = await fetch(apiUrl, {
      ...options,
      headers: {
        'Authorization': `Bearer ${session.accessToken}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      const error = `Request failed: ${response.status} ${response.statusText}`
      options.onError?.(error)
      throw new Error(error)
    }

    return response
  }, [session?.accessToken, options.onError])

  return {
    authenticatedFetch,
    hasToken: !!session?.accessToken,
  }
} 