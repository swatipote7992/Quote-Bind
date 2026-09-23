import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Header } from '../../src/layout/Header'

describe('Header', () => {
  it('renders the QuoteBind brand', () => {
    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>,
    )

    expect(screen.getByText('QuoteBind')).toBeInTheDocument()
  })

  it('links Products, Question Set, and Quotes to their routes', () => {
    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>,
    )

    expect(screen.getByRole('link', { name: 'Products' })).toHaveAttribute(
      'href',
      '/products',
    )
    expect(screen.getByRole('link', { name: 'Question Set' })).toHaveAttribute(
      'href',
      '/question-set',
    )
    expect(screen.getByRole('link', { name: 'Quotes' })).toHaveAttribute(
      'href',
      '/quotes',
    )
  })
})
