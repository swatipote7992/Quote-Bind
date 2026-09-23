import { ProductsDataGrid } from '../components/ProductsDataGrid'

export function ProductsPage() {
  return (
    <>
      <h1 className="mb-6 text-2xl font-semibold tracking-tight text-slate-900">
        Products
      </h1>
      <ProductsDataGrid />
    </>
  )
}
