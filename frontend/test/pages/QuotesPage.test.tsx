import { render, screen } from '@testing-library/react'
import { QuotesPage } from '../../src/pages/QuotesPage'

jest.mock('../../src/components/QuotesDataGrid', () => ({
  QuotesDataGrid: () => <div data-testid="quotes-data-grid-stub" />,
}))

describe('QuotesPage', () => {
  it('renders the Quotes heading and grid', () => {
    render(<QuotesPage />)

    expect(screen.getByRole('heading', { name: 'Quotes' })).toBeInTheDocument()
    expect(screen.getByTestId('quotes-data-grid-stub')).toBeInTheDocument()
  })
})
