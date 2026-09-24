import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QuoteFormPage } from '../../src/pages/QuoteFormPage'
import { createQuote, getQuote, updateQuote } from '../../src/api/quotes'
import { getProducts } from '../../src/api/products'
import type { QuoteDto } from '../../src/types/quote_model'

jest.mock('../../src/api/quotes', () => ({
  createQuote: jest.fn(),
  getQuote: jest.fn(),
  updateQuote: jest.fn(),
}))
jest.mock('../../src/api/products', () => ({
  getProducts: jest.fn(),
}))

const mockedCreateQuote = jest.mocked(createQuote)
const mockedGetQuote = jest.mocked(getQuote)
const mockedUpdateQuote = jest.mocked(updateQuote)
const mockedGetProducts = jest.mocked(getProducts)

const existingQuote: QuoteDto = {
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

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/quotes" element={<div>Quotes list stub</div>} />
        <Route path="/quotes/new" element={<QuoteFormPage />} />
        <Route path="/quotes/:quoteId/edit" element={<QuoteFormPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('QuoteFormPage', () => {
  beforeEach(() => {
    mockedGetProducts.mockResolvedValue([
      { product_id: 1, product_label: 'Home', isActive: true },
    ])
  })

  afterEach(() => {
    jest.resetAllMocks()
  })

  it('creates a new quote and returns to the list', async () => {
    mockedCreateQuote.mockResolvedValue(existingQuote)

    renderAt('/quotes/new')

    expect(screen.getByRole('heading', { name: 'New Quote' })).toBeInTheDocument()

    fireEvent.mouseDown(await screen.findByRole('combobox', { name: /product/i }))
    fireEvent.click(await screen.findByRole('option', { name: 'Home' }))
    fireEvent.change(screen.getByLabelText(/applicant id/i), { target: { value: '1001' } })
    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Jane' } })
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } })
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'jane.doe@example.com' },
    })
    fireEvent.change(screen.getByLabelText(/phone/i), { target: { value: '7700900123' } })
    fireEvent.change(screen.getByLabelText(/date of birth/i), {
      target: { value: '1990-01-01' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Save' }))

    await waitFor(() =>
      expect(mockedCreateQuote).toHaveBeenCalledWith({
        product_id: 1,
        applicant: {
          applicant_id: 1001,
          first_name: 'Jane',
          last_name: 'Doe',
          email: 'jane.doe@example.com',
          phone: '7700900123',
          date_of_birth: '1990-01-01',
        },
      }),
    )
    expect(await screen.findByText('Quotes list stub')).toBeInTheDocument()
  })

  it('loads an existing quote and saves edits', async () => {
    mockedGetQuote.mockResolvedValue(existingQuote)
    mockedUpdateQuote.mockResolvedValue(existingQuote)

    renderAt('/quotes/Q001/edit')

    expect(await screen.findByDisplayValue('Jane')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Edit Quote Q001' })).toBeInTheDocument()

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Janet' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save' }))

    await waitFor(() =>
      expect(mockedUpdateQuote).toHaveBeenCalledWith(
        'Q001',
        expect.objectContaining({
          product_id: 1,
          applicant: expect.objectContaining({ first_name: 'Janet' }),
        }),
      ),
    )
    expect(await screen.findByText('Quotes list stub')).toBeInTheDocument()
  })

  it('shows an error and stays on the page when saving fails', async () => {
    mockedGetQuote.mockResolvedValue(existingQuote)
    mockedUpdateQuote.mockRejectedValue(new Error('PUT failed'))

    renderAt('/quotes/Q001/edit')

    await screen.findByDisplayValue('Jane')
    fireEvent.click(screen.getByRole('button', { name: 'Save' }))

    expect(await screen.findByText('PUT failed')).toBeInTheDocument()
    expect(screen.queryByText('Quotes list stub')).not.toBeInTheDocument()
  })
})
