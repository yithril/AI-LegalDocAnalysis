import { NextResponse } from 'next/server';
import { auth0 } from '../../../lib/auth0';

export async function GET() {
  try {
    // Get the session to extract user info
    const session = await auth0.getSession();
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get the tenant from the session or request
    const tenant = session.user?.['https://your-app.com/tenant_slug'] || 'gazdecki-consortium';
    
    // Call the FastAPI backend
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/${tenant}/user-groups`, {
      headers: {
        'Authorization': `Bearer ${session.accessToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const userGroups = await response.json();
    return NextResponse.json(userGroups);

  } catch (error) {
    console.error('Error fetching user groups:', error);
    return NextResponse.json(
      { error: 'Failed to fetch user groups' }, 
      { status: 500 }
    );
  }
}

export async function POST(request) {
  try {
    const session = await auth0.getSession();
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const tenant = session.user?.['https://your-app.com/tenant_slug'] || 'gazdecki-consortium';
    const body = await request.json();
    
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/${tenant}/user-groups`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${session.accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const userGroup = await response.json();
    return NextResponse.json(userGroup);

  } catch (error) {
    console.error('Error creating user group:', error);
    return NextResponse.json(
      { error: 'Failed to create user group' }, 
      { status: 500 }
    );
  }
} 