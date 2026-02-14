import { ProductForm } from '@/features/inventory/components/ProductForm'

export default function NewProductPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">New Product</h1>
        <p className="text-slate-600 mt-1">Add a new product to inventory</p>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <ProductForm />
      </div>
    </div>
  )
}
