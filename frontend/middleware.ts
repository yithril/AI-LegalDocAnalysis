import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { auth0 } from "./lib/auth0"

console.log("Middleware file loaded"); // Added for debugging

export async function middleware(request: NextRequest) {
  console.log("Middleware triggered for:", request.nextUrl.pathname);

  const authRes = await auth0.middleware(request);

  // authentication routes — let the middleware handle it
  if (request.nextUrl.pathname.startsWith("/auth")) {
    console.log("auth route")
    return authRes;
  }

  const { origin } = new URL(request.url)
  const session = await auth0.getSession(request) // Fixed

  // user does not have a session — redirect to login
  if (!session) {
    console.log("No session found, redirecting to login");
    return NextResponse.redirect(`${origin}/auth/login`)
  }

  // User is authenticated, allow access to all routes
  console.log("User authenticated, allowing access");
  return authRes
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|api).*)",
  ],
} 