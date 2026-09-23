import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './layout/Layout'
import { ProductsPage } from './pages/ProductsPage'
import { QuestionSetPage } from './pages/QuestionSetPage'
import { QuotesPage } from './pages/QuotesPage'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/quotes" replace />} />
        <Route path="products" element={<ProductsPage />} />
        <Route path="question-set" element={<QuestionSetPage />} />
        <Route path="quotes" element={<QuotesPage />} />
      </Route>
    </Routes>
  )
}

export default App
