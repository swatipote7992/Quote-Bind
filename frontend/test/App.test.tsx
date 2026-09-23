import { render, screen } from '@testing-library/react'
import App from '../src/App'

jest.mock('../src/components/QuotesDataGrid', () => ({
  QuotesDataGrid: () => <div data-testid="quotes-data-grid-stub" />,
}))

describe('App', () => {
  it('renders the QuoteBind header with nav links', () => {
    render(<App />)

    expect(screen.getByText('QuoteBind')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Products' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Quotes' })).toBeInTheDocument()
  })

  it('renders the Quotes page heading', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: 'Quotes' })).toBeInTheDocument()
  })

  it('renders the QuotesDataGrid', () => {
    render(<App />)

    expect(screen.getByTestId('quotes-data-grid-stub')).toBeInTheDocument()
  })

  it('renders the footer with the copyright notice', () => {
    render(<App />)

    expect(screen.getByText(/All rights reserved\./)).toBeInTheDocument()
  })
})
