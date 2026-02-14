'use client'

import { useQuery } from '@tanstack/react-query'
import { inventoryApi } from '@/features/inventory/api/inventoryApi'
import { usePermissions } from '@/features/permissions/hooks/usePermissions'
import { Plus, Package, AlertTriangle } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'

export default function InventoryPage() {
  const [search, setSearch] = useState('')
  const [lowStockOnly, setLowStockOnly] = useState(false)
  const { canRead, canWrite, isLoading: permLoading } = usePermissions()

  const { data: products = [], isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: inventoryApi.listProducts,
    enabled: canRead('inventory'),
  })

  const filtered = products.filter((p: any) => {
    const matchSearch = !search || 
      p.name?.toLowerCase().includes(search.toLowerCase()) ||
      p.sku?.toLowerCase().includes(search.toLowerCase())
    const matchLowStock = !lowStockOnly || p.quantity_on_hand <= p.min_quantity
    return matchSearch && matchLowStock
  })

  if (permLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-slate-200 rounded animate-pulse" />
        <div className="bg-white rounded-lg border border-slate-200 p-6 h-64 animate-pulse" />
      </div>
    )
  }

  if (!canRead('inventory')) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Inventory</h1>
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-amber-800">
          You don&apos;t have access to view inventory.
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Inventory</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-48 bg-slate-200 rounded-lg animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Inventory</h1>
          <p className="text-slate-600 mt-1">Manage products and stock</p>
        </div>
        {canWrite('inventory') && (
          <Link
            href="/dashboard/inventory/products/new"
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Product
          </Link>
        )}
      </div>

      <div className="flex gap-4 items-center">
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        />
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={lowStockOnly}
            onChange={(e) => setLowStockOnly(e.target.checked)}
            className="rounded border-slate-300"
          />
          Low Stock Only
        </label>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.length === 0 ? (
          <div className="col-span-full bg-white rounded-lg border border-slate-200 p-12 text-center">
            <Package className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-600">No products found</p>
          </div>
        ) : (
          filtered.map((product: any) => {
            const isLowStock = product.quantity_on_hand <= product.min_quantity
            return (
              <div
                key={product.id}
                onClick={() => window.location.href = `/dashboard/inventory/products/${product.id}/edit`}
                className="bg-white rounded-lg border border-slate-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-semibold text-slate-900">{product.name}</h3>
                    <p className="text-sm text-slate-600">{product.sku || 'No SKU'}</p>
                  </div>
                  {isLowStock && (
                    <span className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs font-medium flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" />
                      Low
                    </span>
                  )}
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">On Hand:</span>
                    <span className="text-2xl font-bold text-slate-900">{product.quantity_on_hand}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Min Quantity:</span>
                    <span className="text-slate-900">{product.min_quantity}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Unit:</span>
                    <span className="text-slate-900">{product.unit_of_measure}</span>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
