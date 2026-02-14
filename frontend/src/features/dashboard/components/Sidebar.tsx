'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Home,
  Calendar,
  Mail,
  Users,
  Package,
  Briefcase,
  FileText,
  Plug,
  Bell,
  Settings,
  CalendarCheck,
  FormInput,
  Video,
} from 'lucide-react'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: Home },
  { href: '/dashboard/bookings', label: 'Bookings', icon: Calendar },
  { href: '/dashboard/webex', label: 'Webex Meetings', icon: Video },
  { href: '/dashboard/inbox', label: 'Inbox', icon: Mail },
  { href: '/dashboard/contacts', label: 'Contacts', icon: Users },
  { href: '/dashboard/inventory', label: 'Inventory', icon: Package },
  { href: '/dashboard/services', label: 'Services', icon: Briefcase },
  { href: '/dashboard/forms', label: 'Forms', icon: FileText },
  { href: '/dashboard/google-forms', label: 'Google Forms', icon: FormInput },
  { href: '/dashboard/integrations', label: 'Integrations', icon: Plug },
  // { href: '/dashboard/alerts', label: 'Alerts', icon: Bell },
  { href: '/dashboard/settings', label: 'Settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-slate-900 text-white h-screen fixed left-0 top-0 overflow-y-auto">
      <div className="p-6 border-b border-slate-700">
        <h1 className="text-2xl font-bold">CareOps</h1>
      </div>

      <nav className="py-6">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/')

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-6 py-3 transition-colors ${
                isActive
                  ? 'bg-slate-800 border-r-4 border-blue-500 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
