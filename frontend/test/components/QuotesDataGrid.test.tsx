import { render, screen, waitFor } from '@testing-library/react'
import { QuotesDataGrid } from '../../src/components/QuotesDataGrid'
import { getQuotes } from '../../src/api/quotes'
import type { QuoteDto } from '../../src/types/quote_model'

jest.mock('../../src/api/quotes', () => ({
  getQuotes: jest.fn(),
}))

const mockedGetQuotes = jest.mocked(getQuotes)

const sampleQuote: QuoteDto = {
  id: 'Q001',
  status: 'New',
  product_id: 1,
  applicant: {
    applicant_id: 1001,
    first_name: 'Jane',
    last_name: 'Doe',
    email: 'jane.doe@example.com',
    phone: '7700900123',
    date_of_birth: '1990-01-01',
  },
  question_set: [],
  created_at: '2026-01-01T10:00:00Z',
  updated_at: '2026-01-01T10:00:00Z',
}

describe('QuotesDataGrid', () => {
  afterEach(() => {
    mockedGetQuotes.mockReset()
  })

  it('renders quote rows once loaded', async () => {
    mockedGetQuotes.mockResolvedValue([sampleQuote])

    render(<QuotesDataGrid />)

    expect(await screen.findByText('Q001')).toBeInTheDocument()
    expect(screen.getByText('Jane Doe')).toBeInTheDocument()
    expect(screen.getByText('jane.doe@example.com')).toBeInTheDocument()
    expect(screen.getByText('7700900123')).toBeInTheDocument()
  })

  it('renders an empty grid with no rows when there are no quotes', async () => {
    mockedGetQuotes.mockResolvedValue([])

    render(<QuotesDataGrid />)

    await waitFor(() => expect(mockedGetQuotes).toHaveBeenCalledTimes(1))
    expect(await screen.findByText('No rows')).toBeInTheDocument()
  })

  it('shows an error message when the request fails', async () => {
    mockedGetQuotes.mockRejectedValue(new Error('Network down'))

    render(<QuotesDataGrid />)

    expect(
      await screen.findByText(/Couldn't load quotes: Network down/),
    ).toBeInTheDocument()
  })
})
