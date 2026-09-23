import { render, screen } from '@testing-library/react'
import { ProductsPage } from '../../src/pages/ProductsPage'

jest.mock('../../src/components/ProductsDataGrid', () => ({
  ProductsDataGrid: () => <div data-testid="products-data-grid-stub" />,
}))

describe('ProductsPage', () => {
  it('renders the Products heading and grid', () => {
    render(<ProductsPage />)

    expect(screen.getByRole('heading', { name: 'Products' })).toBeInTheDocument()
    expect(screen.getByTestId('products-data-grid-stub')).toBeInTheDocument()
  })
})
