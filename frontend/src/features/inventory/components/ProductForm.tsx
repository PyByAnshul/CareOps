'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { inventoryApi } from '../api/inventoryApi'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

const productSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  sku: z.string().optional(),
  description: z.string().optional(),
  quantity_on_hand: z.number().min(0),
  min_quantity: z.number().min(0),
  unit_of_measure: z.string().min(1),
})

type ProductFormData = z.infer<typeof productSchema>

export function ProductForm({ initialData }: { initialData?: any }) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)

  const { register, handleSubmit, formState: { errors } } = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
    defaultValues: initialData || { quantity_on_hand: 0, min_quantity: 0, unit_of_measure: 'unit' },
  })

  const mutation = useMutation({
    mutationFn: (data: ProductFormData) =>
      initialData ? inventoryApi.updateProduct(initialData.id, data) : inventoryApi.createProduct(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      router.push('/dashboard/inventory')
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to save product')
    },
  })

  return (
    <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Product Name *</label>
          <input
            {...register('name')}
            type="text"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          {errors.name && <p className="text-red-600 text-sm mt-1">{errors.name.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">SKU</label>
          <input
            {...register('sku')}
            type="text"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Initial Quantity *</label>
          <input
            {...register('quantity_on_hand', { valueAsNumber: true })}
            type="number"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          {errors.quantity_on_hand && <p className="text-red-600 text-sm mt-1">{errors.quantity_on_hand.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Min Quantity *</label>
          <input
            {...register('min_quantity', { valueAsNumber: true })}
            type="number"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          {errors.min_quantity && <p className="text-red-600 text-sm mt-1">{errors.min_quantity.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Unit of Measure *</label>
          <input
            {...register('unit_of_measure')}
            type="text"
            placeholder="e.g., unit, kg, liter"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          {errors.unit_of_measure && <p className="text-red-600 text-sm mt-1">{errors.unit_of_measure.message}</p>}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
        <textarea
          {...register('description')}
          rows={4}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        />
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={mutation.isPending}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white px-6 py-2 rounded-lg transition-colors"
        >
          {mutation.isPending ? 'Saving...' : initialData ? 'Update Product' : 'Create Product'}
        </button>
        <button
          type="button"
          onClick={() => router.back()}
          className="bg-slate-200 hover:bg-slate-300 text-slate-900 px-6 py-2 rounded-lg transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
