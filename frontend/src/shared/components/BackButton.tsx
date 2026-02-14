'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

interface BackButtonProps {
  href: string
  label?: string
  className?: string
}

export function BackButton({ href, label, className = '' }: BackButtonProps) {
  return (
    <Link
      href={href}
      className={`inline-flex items-center gap-2 p-2 rounded-lg hover:bg-slate-100 text-slate-700 transition-colors ${className}`}
    >
      <ArrowLeft className="w-5 h-5" />
      {label && <span className="text-sm font-medium">{label}</span>}
    </Link>
  )
}
