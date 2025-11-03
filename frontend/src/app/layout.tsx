import { Providers } from '@/components/providers'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Dynamic Compression Algorithms - Advanced AI-Powered Compression System',
  description: 'Next-generation compression algorithms with meta-recursive learning, quantum-biological integration, and comprehensive system analytics',
  keywords: 'compression, AI, machine learning, quantum computing, algorithms, optimization',
  authors: [{ name: 'Dynamic Compression Team' }],
  robots: 'index, follow',
  openGraph: {
    title: 'Dynamic Compression Algorithms',
    description: 'Advanced AI-powered compression system with meta-recursive learning',
    type: 'website',
    locale: 'en_US',
  },
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <head>
        <script src="http://localhost:8097"></script>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className={`${inter.className} h-full antialiased`}>
        <Providers>
          <div className="min-h-screen bg-slate-900 text-white">
            {children}
          </div>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1e293b',
                color: '#f8fafc',
                border: '1px solid #475569',
                borderRadius: '8px',
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}
