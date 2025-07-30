import NextAuth from "next-auth"

declare module "next-auth" {
  interface Session {
    user: {
      id: string
      email: string
      name: string
      role: string
      tenant_slug: string
    }
    accessToken?: string
  }

  interface User {
    id: string
    email: string
    name: string
    role: string
    tenant_slug: string
    database_id?: number
    access_token?: string
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id: string
    email: string
    name: string
    role: string
    tenant_slug: string
    database_id?: number
    access_token?: string
  }
} 