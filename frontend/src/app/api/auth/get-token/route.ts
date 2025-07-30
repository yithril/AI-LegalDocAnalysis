import { getToken } from "next-auth/jwt"
import { NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  try {
    // Get the JWT token using NextAuth.js getToken helper
    const token = await getToken({ 
      req: request,
      secret: process.env.NEXTAUTH_SECRET 
    })
    
    if (token) {
      // Return the token data (this includes the actual JWT)
      return NextResponse.json({ 
        token: token,
        hasToken: true 
      })
    } else {
      // Not signed in
      return NextResponse.json({ 
        hasToken: false 
      }, { status: 401 })
    }
  } catch (error) {
    console.error('Error getting token:', error)
    return NextResponse.json({ 
      error: 'Failed to get token' 
    }, { status: 500 })
  }
} 