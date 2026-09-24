import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '../src/App'

jest.mock('../src/components/QuotesDataGrid', () => ({
  QuotesDataGrid: () => <div data-testid="quotes-data-grid-stub" />,
}))
jest.mock('../src/pages/QuoteFormPage', () => ({
  QuoteFormPage: () => <div data-testid="quote-form-page-stub" />,
}))
jest.mock('../src/components/ProductsDataGrid', () => ({
  ProductsDataGrid: () => <div data-testid="products-data-grid-stub" />,
}))
jest.mock('../src/components/QuestionsDataGrid', () => ({
  QuestionsDataGrid: () => <div data-testid="questions-data-grid-stub" />,
}))

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  )
}

describe('App', () => {
  it('renders the QuoteBind header with nav links', () => {
    renderAt('/quotes')

    expect(screen.getByText('QuoteBind')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Quotes' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Products' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Questions' })).toBeInTheDocument()
  })

  it('redirects / to /quotes', () => {
    renderAt('/')

    expect(screen.getByRole('heading', { name: 'Quotes' })).toBeInTheDocument()
    expect(screen.getByTestId('quotes-data-grid-stub')).toBeInTheDocument()
  })

  it('renders the Products page at /products', () => {
    renderAt('/products')

    expect(screen.getByRole('heading', { name: 'Products' })).toBeInTheDocument()
    expect(screen.getByTestId('products-data-grid-stub')).toBeInTheDocument()
  })

  it('renders the Questions page at /questions', () => {
    renderAt('/questions')

    expect(screen.getByRole('heading', { name: 'Questions' })).toBeInTheDocument()
    expect(screen.getByTestId('questions-data-grid-stub')).toBeInTheDocument()
  })

  it('renders the Quotes page at /quotes', () => {
    renderAt('/quotes')

    expect(screen.getByRole('heading', { name: 'Quotes' })).toBeInTheDocument()
    expect(screen.getByTestId('quotes-data-grid-stub')).toBeInTheDocument()
  })

  it('renders the quote form at /quotes/new and /quotes/:id/edit', () => {
    const { unmount } = renderAt('/quotes/new')
    expect(screen.getByTestId('quote-form-page-stub')).toBeInTheDocument()
    unmount()

    renderAt('/quotes/Q001/edit')
    expect(screen.getByTestId('quote-form-page-stub')).toBeInTheDocument()
  })

  it('renders the footer with the copyright notice', () => {
    renderAt('/quotes')

    expect(screen.getByText(/All rights reserved\./)).toBeInTheDocument()
  })
})
