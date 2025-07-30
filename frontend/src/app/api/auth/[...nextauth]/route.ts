import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import { getCurrentTenantSlug } from "@/lib/tenant"
import { encode } from "next-auth/jwt"

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        try {
          // Call your backend API here
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
              tenant_slug: getCurrentTenantSlug(),
            }),
          })

          if (!response.ok) {
            return null
          }

          const user = await response.json()
          
          // Return user data for NextAuth.js to create its own token
          // Use email as the NextAuth.js user ID to match backend expectations
          return {
            id: user.email, // Use email as NextAuth.js user ID
            email: user.email,
            name: user.name,
            role: user.role,
            tenant_slug: user.tenant_slug,
            database_id: user.id, // Store the actual database ID
          }
        } catch (error) {
          console.error('Authentication error:', error)
          return null
        }
      }
    })
  ],
  session: {
    strategy: "jwt",
    maxAge: 60 * 60, // 1 hour (session expires)
  },
  jwt: {
    secret: process.env.NEXTAUTH_SECRET,
    // @ts-ignore - encryption property exists in NextAuth.js but not in types
    encryption: false, // Turn off encryption so backend can decode the JWT
    maxAge: 15 * 60, // 15 minutes (access token expires)
  },
  pages: {
    signIn: '/auth/signin',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        // Store user data in the JWT token
        token.id = user.id // This will be the email (NextAuth.js user ID)
        token.email = user.email
        token.name = user.name
        token.role = user.role
        token.tenant_slug = user.tenant_slug
        token.database_id = user.database_id // Store the actual database ID
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        // Make user data available in the session
        session.user.id = token.id as string // This is the email (NextAuth.js user ID)
        session.user.role = token.role as string
        session.user.tenant_slug = token.tenant_slug as string
        
        // Encode the JWT token so it can be sent to the backend
        const encodedToken = await encode({
          token: token,
          secret: process.env.NEXTAUTH_SECRET!,
        })
        
        // Store the encoded JWT token
        session.accessToken = encodedToken
      }
      return session
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
})

export { handler as GET, handler as POST } 