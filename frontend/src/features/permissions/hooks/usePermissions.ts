'use client'

import { useQuery } from '@tanstack/react-query'
import { usersApi } from '@/features/users/api/usersApi'
import { authApi } from '@/features/auth/api/authApi'

/**
 * Returns current user's permissions and helpers.
 * Owners are treated as having all permissions (from API).
 */
export function usePermissions() {
  const { data: user } = useQuery({
    queryKey: ['me'],
    queryFn: authApi.getMe,
  })
  const { data: permissionNames = [], isLoading } = useQuery({
    queryKey: ['me-permissions'],
    queryFn: usersApi.getMyPermissions,
    enabled: !!user,
  })

  const set = new Set(permissionNames)
  const can = (name: string) => user?.role === 'owner' || set.has(name)

  return {
    isLoading,
    role: user?.role,
    permissions: permissionNames,
    can,
    canRead: (module: string) => can(`${module}.read`),
    canWrite: (module: string) => can(`${module}.write`),
    canDelete: (module: string) => can(`${module}.delete`),
  }
}
