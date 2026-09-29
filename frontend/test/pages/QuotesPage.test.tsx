import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QuotesPage } from '../../src/pages/QuotesPage'

jest.mock('../../src/components/QuotesDataGrid', () => ({
  QuotesDataGrid: () => <div data-testid="quotes-data-grid-stub" />,
}))

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/quotes']}>
      <Routes>
        <Route path="/quotes" element={<QuotesPage />} />
        <Route path="/quotes/new" element={<div>New quote page stub</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('QuotesPage', () => {
  it('renders the Quotes heading and grid', () => {
    renderPage()

    expect(screen.getByRole('heading', { name: 'Quotes' })).toBeInTheDocument()
    expect(screen.getByTestId('quotes-data-grid-stub')).toBeInTheDocument()
  })

  it('navigates to the new quote page when New Quote is clicked', () => {
    renderPage()

    fireEvent.click(screen.getByRole('button', { name: 'New Quote' }))

    expect(screen.getByText('New quote page stub')).toBeInTheDocument()
  })
})
