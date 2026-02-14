import type { Metadata } from 'next'
import { AuthProvider } from '@/core/auth/AuthProvider'
import { QueryProvider } from '@/core/providers/QueryProvider'
import '../../styles/globals.css'

export const metadata: Metadata = {
  title: 'CareOps',
  description: 'CareOps Management Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  )
}
