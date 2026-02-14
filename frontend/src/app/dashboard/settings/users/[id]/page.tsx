'use client'

import { useParams } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { BackButton } from '@/shared/components/BackButton'
import { usersApi } from '@/features/users/api/usersApi'
import { permissionsApi } from '@/features/permissions/api/permissionsApi'
import { authApi } from '@/features/auth/api/authApi'
import { Mail, Shield, Calendar, Plus, X } from 'lucide-react'

interface Permission {
  id: number
  name: string
  description: string | null
  module: string
}

function groupByModule(permissions: Permission[]): Record<string, Permission[]> {
  const map: Record<string, Permission[]> = {}
  for (const p of permissions) {
    if (!map[p.module]) map[p.module] = []
    map[p.module].push(p)
  }
  for (const key of Object.keys(map)) {
    map[key].sort((a, b) => a.name.localeCompare(b.name))
  }
  return map
}

export default function SettingsUserDetailPage() {
  const params = useParams()
  const userId = params.id as string
  const queryClient = useQueryClient()

  const { data: currentUser } = useQuery({
    queryKey: ['me'],
    queryFn: authApi.getMe,
  })
  const isOwner = currentUser?.role === 'owner'

  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => usersApi.get(userId),
  })

  const { data: allPermissions = [], isLoading: allPermsLoading } = useQuery({
    queryKey: ['permissions'],
    queryFn: permissionsApi.list,
    enabled: isOwner,
  })

  const { data: userPermissions = [], isLoading: userPermsLoading } = useQuery({
    queryKey: ['user-permissions', userId],
    queryFn: () => usersApi.getPermissions(userId),
    enabled: isOwner && !!userId,
  })

  const assignMutation = useMutation({
    mutationFn: (permission_name: string) =>
      permissionsApi.assignPermission({ user_id: Number(userId), permission_name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-permissions', userId] })
    },
  })

  const removeMutation = useMutation({
    mutationFn: (permission_name: string) =>
      permissionsApi.removePermission({ user_id: Number(userId), permission_name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-permissions', userId] })
    },
  })

  const userPermNames = new Set(userPermissions.map((p: Permission) => p.name))
  const groupedAll = groupByModule(allPermissions)

  if (userLoading || !user) {
    return (
      <div className="space-y-6">
        <BackButton href="/dashboard/settings/users" label="Back to users" />
        <div className="h-8 w-48 bg-slate-200 rounded animate-pulse" />
        <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-10 bg-slate-200 rounded animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3">
        <BackButton href="/dashboard/settings/users" label="Back to users" />
        <div>
          <h1 className="text-3xl font-bold text-slate-900">User details</h1>
          <p className="text-slate-600 mt-1">View user and manage permissions (owner only)</p>
        </div>
      </div>

      {/* User info - no password */}
      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        <div className="p-6 space-y-4">
          <div className="flex items-start gap-3">
            <Mail className="w-5 h-5 text-slate-600 mt-0.5" />
            <div>
              <p className="text-sm text-slate-600">Email</p>
              <p className="font-medium text-slate-900">{user.email}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <Shield className="w-5 h-5 text-slate-600 mt-0.5" />
            <div>
              <p className="text-sm text-slate-600">Role</p>
              <p className="font-medium text-slate-900 capitalize">{user.role}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <Calendar className="w-5 h-5 text-slate-600 mt-0.5" />
            <div>
              <p className="text-sm text-slate-600">Status</p>
              <p className="font-medium text-slate-900">{user.is_active ? 'Active' : 'Inactive'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Permissions: two columns - only for owner */}
      {isOwner && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: All permissions by module with assign */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
              <h2 className="text-lg font-semibold text-slate-900">All permissions</h2>
              <p className="text-sm text-slate-600">Click + to grant this permission to the user</p>
            </div>
            <div className="p-6 overflow-y-auto max-h-[420px]">
              {allPermsLoading ? (
                <div className="text-slate-600 text-sm">Loading...</div>
              ) : (
                <div className="space-y-6">
                  {Object.entries(groupedAll).map(([module, perms]) => (
                    <div key={module}>
                      <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide mb-2 capitalize">
                        {module}
                      </h3>
                      <ul className="space-y-1">
                        {perms.map((p) => {
                          const has = userPermNames.has(p.name)
                          return (
                            <li
                              key={p.id}
                              className="flex items-center justify-between gap-2 py-1.5 px-2 rounded hover:bg-slate-50"
                            >
                              <span className="text-sm text-slate-900">
                                {p.name}
                                {p.description && (
                                  <span className="text-slate-500 font-normal ml-1">
                                    — {p.description}
                                  </span>
                                )}
                              </span>
                              {!has && (
                                <button
                                  type="button"
                                  onClick={() => assignMutation.mutate(p.name)}
                                  disabled={assignMutation.isPending}
                                  className="p-1.5 text-green-600 hover:bg-green-50 rounded disabled:opacity-50"
                                  title="Grant permission"
                                >
                                  <Plus className="w-4 h-4" />
                                </button>
                              )}
                            </li>
                          )
                        })}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right: User's current permissions with remove */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
              <h2 className="text-lg font-semibold text-slate-900">User&apos;s permissions</h2>
              <p className="text-sm text-slate-600">Permissions this user has. Click × to revoke.</p>
            </div>
            <div className="p-6 overflow-y-auto max-h-[420px]">
              {userPermsLoading ? (
                <div className="text-slate-600 text-sm">Loading...</div>
              ) : userPermissions.length === 0 ? (
                <p className="text-slate-500 text-sm">No permissions assigned yet.</p>
              ) : (
                <div className="space-y-6">
                  {Object.entries(groupByModule(userPermissions)).map(([module, perms]) => (
                    <div key={module}>
                      <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide mb-2 capitalize">
                        {module}
                      </h3>
                      <ul className="space-y-1">
                        {perms.map((p: Permission) => (
                          <li
                            key={p.id}
                            className="flex items-center justify-between gap-2 py-1.5 px-2 rounded hover:bg-slate-50"
                          >
                            <span className="text-sm text-slate-900">
                              {p.name}
                              {p.description && (
                                <span className="text-slate-500 font-normal ml-1">
                                  — {p.description}
                                </span>
                              )}
                            </span>
                            <button
                              type="button"
                              onClick={() => removeMutation.mutate(p.name)}
                              disabled={removeMutation.isPending}
                              className="p-1.5 text-red-600 hover:bg-red-50 rounded disabled:opacity-50"
                              title="Revoke permission"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {!isOwner && (
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-slate-600 text-sm">
          Permission management is only available to workspace owners.
        </div>
      )}
    </div>
  )
}
