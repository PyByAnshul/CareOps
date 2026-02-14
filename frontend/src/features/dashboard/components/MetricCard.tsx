import { LucideIcon } from 'lucide-react'
import Link from 'next/link'

interface MetricCardProps {
  icon: LucideIcon
  label: string
  value: number
  link?: string
  color: 'blue' | 'yellow' | 'green' | 'red'
}

const colorStyles = {
  blue: 'text-blue-600 bg-blue-50',
  yellow: 'text-yellow-600 bg-yellow-50',
  green: 'text-green-600 bg-green-50',
  red: 'text-red-600 bg-red-50',
}

export function MetricCard({ icon: Icon, label, value, link, color }: MetricCardProps) {
  const cardContent = (
    <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
      <div className={`w-12 h-12 rounded-lg ${colorStyles[color]} flex items-center justify-center mb-4`}>
        <Icon className="w-6 h-6" />
      </div>
      <p className="text-slate-600 text-sm font-medium mb-1">{label}</p>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
    </div>
  )

  if (link) {
    return (
      <Link href={link}>
        {cardContent}
      </Link>
    )
  }

  return cardContent
}
