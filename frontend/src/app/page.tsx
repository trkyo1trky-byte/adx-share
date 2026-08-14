'use client'

import { useAuth } from '@/providers/AuthProvider'
import Link from 'next/link'

export default function Home() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold mb-4">🌴 ADX SHARES</h1>
        <p className="text-xl text-slate-600 dark:text-slate-300 mb-8">
          منصة التداول والاستثمار والأسواق الرقمية
        </p>
        
        {user ? (
          <div>
            <p className="text-lg mb-4">مرحباً بك، {user.full_name}!</p>
            <Link
              href="/dashboard"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
            >
              الذهاب إلى لوحة التحكم
            </Link>
          </div>
        ) : (
          <div className="flex gap-4 justify-center">
            <Link
              href="/login"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
            >
              تسجيل الدخول
            </Link>
            <Link
              href="/register"
              className="bg-emerald-600 text-white px-6 py-3 rounded-lg hover:bg-emerald-700 transition"
            >
              إنشاء حساب
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}