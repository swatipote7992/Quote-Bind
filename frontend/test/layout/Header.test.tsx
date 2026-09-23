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

  it('links Quotes, Products, and Questions to their routes, in that order', () => {
    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>,
    )

    const links = screen.getAllByRole('link')
    expect(links.map((link) => link.textContent)).toEqual([
      'Quotes',
      'Products',
      'Questions',
    ])

    expect(screen.getByRole('link', { name: 'Quotes' })).toHaveAttribute(
      'href',
      '/quotes',
    )
    expect(screen.getByRole('link', { name: 'Products' })).toHaveAttribute(
      'href',
      '/products',
    )
    expect(screen.getByRole('link', { name: 'Questions' })).toHaveAttribute(
      'href',
      '/questions',
    )
  })
})
