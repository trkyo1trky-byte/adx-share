import type { Metadata } from 'next';
import { Cairo } from 'next/font/google';
import './globals.css';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from '@/providers/AuthProvider';
import { Layout } from '@/components/Layout/Layout';

const cairo = Cairo({ subsets: ['arabic'], weight: ['400', '600', '700', '900'] });

export const metadata: Metadata = {
  title: 'ADX SHARES - منصة التداول والاستثمار',
  description: 'منصة التداول والاستثمار والأسواق الرقمية',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl">
      <body className={cairo.className}>
        <AuthProvider>
          <Layout>
            {children}
          </Layout>
          <Toaster
            position="bottom-center"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1e293b',
                color: '#fff',
                direction: 'rtl',
              },
            }}
          />
        </AuthProvider>
      </body>
    </html>
  );
}