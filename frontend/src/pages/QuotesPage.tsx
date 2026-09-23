import { QuotesDataGrid } from '../components/QuotesDataGrid'

export function QuotesPage() {
  return (
    <>
      <h1 className="mb-6 text-2xl font-semibold tracking-tight text-slate-900">
        Quotes
      </h1>
      <QuotesDataGrid />
    </>
  )
}
