import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './layout/Layout'
import { ProductsPage } from './pages/ProductsPage'
import { QuestionsPage } from './pages/QuestionsPage'
import { QuotesPage } from './pages/QuotesPage'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/quotes" replace />} />
        <Route path="quotes" element={<QuotesPage />} />
        <Route path="products" element={<ProductsPage />} />
        <Route path="questions" element={<QuestionsPage />} />
      </Route>
    </Routes>
  )
}

export default App
