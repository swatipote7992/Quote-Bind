import { render, screen, waitFor } from '@testing-library/react'
import { ProductsDataGrid } from '../../src/components/ProductsDataGrid'
import { getProducts } from '../../src/api/products'
import type { ProductDto } from '../../src/types/product_model'

jest.mock('../../src/api/products', () => ({
  getProducts: jest.fn(),
}))

const mockedGetProducts = jest.mocked(getProducts)

const sampleProduct: ProductDto = {
  product_id: 1,
  product_label: 'Audi',
  isActive: true,
}

describe('ProductsDataGrid', () => {
  afterEach(() => {
    mockedGetProducts.mockReset()
  })

  it('renders product rows once loaded', async () => {
    mockedGetProducts.mockResolvedValue([sampleProduct])

    render(<ProductsDataGrid />)

    expect(await screen.findByText('Audi')).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument()
  })

  it('renders an empty grid with no rows when there are no products', async () => {
    mockedGetProducts.mockResolvedValue([])

    render(<ProductsDataGrid />)

    await waitFor(() => expect(mockedGetProducts).toHaveBeenCalledTimes(1))
    expect(await screen.findByText('No rows')).toBeInTheDocument()
  })

  it('shows an error message when the request fails', async () => {
    mockedGetProducts.mockRejectedValue(new Error('Network down'))

    render(<ProductsDataGrid />)

    expect(
      await screen.findByText(/Couldn't load products: Network down/),
    ).toBeInTheDocument()
  })

  it('provides a quick-filter search box for filtering records', async () => {
    mockedGetProducts.mockResolvedValue([sampleProduct])

    render(<ProductsDataGrid />)

    await screen.findByText('Audi')

    expect(screen.getByRole('searchbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /show filters/i })).toBeInTheDocument()
  })
})
