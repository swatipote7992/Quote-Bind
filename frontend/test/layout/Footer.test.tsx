import { render, screen } from '@testing-library/react'
import { Footer } from '../../src/layout/Footer'

describe('Footer', () => {
  it('renders the copyright notice with the current year', () => {
    render(<Footer />)

    const year = new Date().getFullYear()
    expect(
      screen.getByText(`© ${year} Swati Pote. All rights reserved.`),
    ).toBeInTheDocument()
  })

  it('renders as a footer landmark', () => {
    render(<Footer />)

    expect(screen.getByRole('contentinfo')).toBeInTheDocument()
  })
})
