import { QuestionsDataGrid } from '../components/QuestionsDataGrid'

export function QuestionsPage() {
  return (
    <>
      <h1 className="mb-6 text-2xl font-semibold tracking-tight text-slate-900">
        Questions
      </h1>
      <QuestionsDataGrid />
    </>
  )
}
