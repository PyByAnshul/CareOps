'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { Save, Trash2, Package, Hash, FileText } from 'lucide-react'
import { inventoryApi } from '@/features/inventory/api/inventoryApi'
import { usePermissions } from '@/features/permissions/hooks/usePermissions'
import { BackButton } from '@/shared/components/BackButton'

export default function EditProductPage() {
  const router = useRouter()
  const params = useParams()
  const productId = params.id as string
  
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    description: '',
    quantity_on_hand: 0,
    min_quantity: 0,
    unit_of_measure: 'unit'
  })
  const [isSaving, setIsSaving] = useState(false)

  const { canRead, canWrite, canDelete } = usePermissions()
  const { data: product, isLoading } = useQuery({
    queryKey: ['product', productId],
    queryFn: () => inventoryApi.getProduct(productId),
    enabled: canRead('inventory'),
  })

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name || '',
        sku: product.sku || '',
        description: product.description || '',
        quantity_on_hand: product.quantity_on_hand || 0,
        min_quantity: product.min_quantity || 0,
        unit_of_measure: product.unit_of_measure || 'unit'
      })
    }
  }, [product])

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await inventoryApi.updateProduct(productId, formData)
      router.push('/dashboard/inventory')
    } catch (error) {
      console.error('Failed to update product:', error)
      alert('Failed to update product')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this product?')) {
      try {
        await inventoryApi.deleteProduct(productId)
        router.push('/dashboard/inventory')
      } catch (error) {
        console.error('Failed to delete product:', error)
        alert('Failed to delete product')
      }
    }
  }

  if (isLoading) {
    return (
      <div className="h-full bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!canRead('inventory')) {
    return (
      <div className="h-full bg-slate-50 p-6">
        <BackButton href="/dashboard/inventory" label="Back to inventory" />
        <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-6 text-amber-800">
          You don&apos;t have access to view or edit inventory.
        </div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="h-full bg-slate-50 flex items-center justify-center">
        <p className="text-slate-600">Product not found</p>
      </div>
    )
  }

  return (
    <div className="h-full bg-slate-50">
      <div className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <BackButton href="/dashboard/inventory" label="Back to inventory" />
            <div>
              <h1 className="text-xl font-semibold text-slate-900">Edit Product</h1>
              <p className="text-sm text-slate-600">Modify product information and stock levels</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {canDelete('inventory') && (
              <button onClick={handleDelete} className="flex items-center px-3 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50">
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </button>
            )}
            {canWrite('inventory') && (
            <button onClick={handleSave} disabled={isSaving} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
            )}
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <Package className="w-4 h-4 inline mr-2" />
                  Product Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <Hash className="w-4 h-4 inline mr-2" />
                  SKU
                </label>
                <input
                  type="text"
                  value={formData.sku}
                  onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Quantity on Hand</label>
                <input
                  type="number"
                  value={formData.quantity_on_hand}
                  onChange={(e) => setFormData({ ...formData, quantity_on_hand: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Minimum Quantity</label>
                <input
                  type="number"
                  value={formData.min_quantity}
                  onChange={(e) => setFormData({ ...formData, min_quantity: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Unit of Measure</label>
                <select
                  value={formData.unit_of_measure}
                  onChange={(e) => setFormData({ ...formData, unit_of_measure: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="unit">Unit</option>
                  <option value="box">Box</option>
                  <option value="pack">Pack</option>
                  <option value="bottle">Bottle</option>
                  <option value="kg">Kilogram</option>
                  <option value="liter">Liter</option>
                </select>
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <FileText className="w-4 h-4 inline mr-2" />
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            {/* Stock Status */}
            <div className="mt-6 p-4 bg-slate-50 rounded-lg">
              <h3 className="font-medium text-slate-900 mb-2">Stock Status</h3>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Current Stock Level:</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  formData.quantity_on_hand <= formData.min_quantity 
                    ? 'bg-red-100 text-red-700' 
                    : 'bg-green-100 text-green-700'
                }`}>
                  {formData.quantity_on_hand <= formData.min_quantity ? 'Low Stock' : 'In Stock'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}