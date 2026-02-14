'use client'

import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { dashboardApi } from '../api/dashboardApi'

const STOCK_COLORS = {
  'In Stock': '#22c55e',
  'Low Stock': '#eab308',
  'Out of Stock': '#ef4444',
}

export function InventoryCharts() {
  const { data, isLoading } = useQuery({
    queryKey: ['inventory-stats'],
    queryFn: dashboardApi.getInventoryStats,
  })

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="h-80 bg-slate-200 rounded-lg animate-pulse"></div>
        <div className="h-80 bg-slate-200 rounded-lg animate-pulse"></div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Stock Status - Pie Chart */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Stock Status</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data?.stockStatus || []}
              dataKey="count"
              nameKey="status"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label={(entry) => `${entry.status}: ${entry.count}`}
            >
              {(data?.stockStatus || []).map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={STOCK_COLORS[entry.status as keyof typeof STOCK_COLORS] || '#94a3b8'} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Top Products by Stock - Bar Chart */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Top Products by Stock</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data?.topProducts || []} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" width={100} />
            <Tooltip />
            <Legend />
            <Bar dataKey="quantity" fill="#8b5cf6" name="Quantity" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
