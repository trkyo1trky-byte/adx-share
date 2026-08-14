import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// المسارات المحمية (تتطلب تسجيل دخول)
const protectedPaths = ['/dashboard', '/profile', '/portfolio', '/trading', '/withdrawals']

// المسارات العامة (لا تتطلب تسجيل دخول)
const authPaths = ['/login', '/register', '/forgot-password', '/reset-password']

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname
  const token = request.cookies.get('access_token')?.value
  const isAuthenticated = !!token

  // إذا كان المستخدم مصادقاً ويحاول الوصول إلى صفحات المصادقة
  if (isAuthenticated && authPaths.some(p => path.startsWith(p))) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // إذا كان المستخدم غير مصادق ويحاول الوصول إلى صفحة محمية
  if (!isAuthenticated && protectedPaths.some(p => path.startsWith(p))) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('redirect', path)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/profile/:path*',
    '/portfolio/:path*',
    '/trading/:path*',
    '/withdrawals/:path*',
    '/login',
    '/register',
    '/forgot-password',
    '/reset-password',
  ],
}