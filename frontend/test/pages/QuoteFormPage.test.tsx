import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QuoteFormPage } from '../../src/pages/QuoteFormPage'
import { createQuote, getQuote, updateQuote } from '../../src/api/quotes'
import { getProductQuestions, getProducts } from '../../src/api/products'
import type { QuoteDto } from '../../src/types/quote_model'

jest.mock('../../src/api/quotes', () => ({
  createQuote: jest.fn(),
  getQuote: jest.fn(),
  updateQuote: jest.fn(),
}))
jest.mock('../../src/api/products', () => ({
  getProducts: jest.fn(),
  getProductQuestions: jest.fn(),
}))

const mockedCreateQuote = jest.mocked(createQuote)
const mockedGetQuote = jest.mocked(getQuote)
const mockedUpdateQuote = jest.mocked(updateQuote)
const mockedGetProducts = jest.mocked(getProducts)
const mockedGetProductQuestions = jest.mocked(getProductQuestions)

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
  question_set: [
    {
      question_id: 1,
      question_label: 'Are you 18 years old?',
      default_answer: 'Yes',
      answer: 'No',
    },
    {
      question_id: 4,
      question_label: 'Do you hold a valid UK driving license?',
      default_answer: 'Yes',
      answer: 'Yes',
    },
  ],
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
    mockedGetProductQuestions.mockResolvedValue([
      { question_id: 1, question_label: 'Are you 18 years old?', default_answer: 'Yes' },
      { question_id: 4, question_label: 'Do you hold a valid UK driving license?', default_answer: 'Yes' },
    ])
  })

  afterEach(() => {
    jest.resetAllMocks()
  })

  it('does not show applicant id, phone or date of birth', async () => {
    renderAt('/quotes/new')

    await screen.findByDisplayValue('Quote')
    expect(screen.queryByLabelText(/applicant id/i)).not.toBeInTheDocument()
    expect(screen.queryByLabelText(/phone/i)).not.toBeInTheDocument()
    expect(screen.queryByLabelText(/date of birth/i)).not.toBeInTheDocument()
  })

  it('pre-fills the applicant as Quote Admin on a new quote', async () => {
    renderAt('/quotes/new')

    expect(await screen.findByDisplayValue('Quote')).toBeInTheDocument()
    expect(screen.getByLabelText(/last name/i)).toHaveValue('Admin')
    expect(screen.getByLabelText(/email/i)).toHaveValue('quote.admin@gmail.com')
    expect(screen.queryByText('Questions')).not.toBeInTheDocument()
  })

  it("lists the selected product's questions", async () => {
    renderAt('/quotes/new')

    fireEvent.mouseDown(await screen.findByRole('combobox', { name: /product/i }))
    fireEvent.click(await screen.findByRole('option', { name: 'Home' }))

    expect(await screen.findByText('Are you 18 years old?')).toBeInTheDocument()
    expect(screen.getByText('Do you hold a valid UK driving license?')).toBeInTheDocument()
    expect(mockedGetProductQuestions).toHaveBeenCalledWith(1)
  })

  it('renders each question as radio buttons with the default answer selected', async () => {
    renderAt('/quotes/new')

    fireEvent.mouseDown(await screen.findByRole('combobox', { name: /product/i }))
    fireEvent.click(await screen.findByRole('option', { name: 'Home' }))

    const group = await screen.findByRole('radiogroup', { name: 'Are you 18 years old?' })
    expect(within(group).getByRole('radio', { name: 'Yes' })).toBeChecked()
    expect(within(group).getByRole('radio', { name: 'No' })).not.toBeChecked()

    fireEvent.click(within(group).getByRole('radio', { name: 'No' }))

    expect(within(group).getByRole('radio', { name: 'No' })).toBeChecked()
    expect(within(group).getByRole('radio', { name: 'Yes' })).not.toBeChecked()
  })

  it('shows an error when the questions fail to load', async () => {
    mockedGetProductQuestions.mockRejectedValue(new Error('boom'))
    renderAt('/quotes/new')

    fireEvent.mouseDown(await screen.findByRole('combobox', { name: /product/i }))
    fireEvent.click(await screen.findByRole('option', { name: 'Home' }))

    expect(await screen.findByText(/Couldn't load questions: boom/)).toBeInTheDocument()
  })

  it('creates a new quote and returns to the list', async () => {
    mockedCreateQuote.mockResolvedValue(existingQuote)

    renderAt('/quotes/new')

    expect(screen.getByRole('heading', { name: 'New Quote' })).toBeInTheDocument()

    fireEvent.mouseDown(await screen.findByRole('combobox', { name: /product/i }))
    fireEvent.click(await screen.findByRole('option', { name: 'Home' }))
    const driving = await screen.findByRole('radiogroup', {
      name: 'Do you hold a valid UK driving license?',
    })
    fireEvent.click(within(driving).getByRole('radio', { name: 'No' }))
    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Jane' } })
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } })
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'jane.doe@example.com' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Save' }))

    await waitFor(() =>
      expect(mockedCreateQuote).toHaveBeenCalledWith({
        product_id: 1,
        answers: [
          { question_id: 1, answer: 'Yes' },
          { question_id: 4, answer: 'No' },
        ],
        applicant: {
          applicant_id: 1001,
          first_name: 'Jane',
          last_name: 'Doe',
          email: 'jane.doe@example.com',
          phone: '123-456-7890',
          date_of_birth: '1980-01-01',
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

    // Saved answers win over the catalog defaults.
    const group = await screen.findByRole('radiogroup', { name: 'Are you 18 years old?' })
    expect(within(group).getByRole('radio', { name: 'No' })).toBeChecked()

    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'Janet' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save' }))

    await waitFor(() =>
      expect(mockedUpdateQuote).toHaveBeenCalledWith(
        'Q001',
        expect.objectContaining({
          product_id: 1,
          // Hidden fields are sent back exactly as loaded.
          applicant: expect.objectContaining({
            first_name: 'Janet',
            applicant_id: 1001,
            phone: '7700900123',
            date_of_birth: '1990-01-01',
          }),
          answers: [
            { question_id: 1, answer: 'No' },
            { question_id: 4, answer: 'Yes' },
          ],
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
    await screen.findByRole('radiogroup', { name: 'Are you 18 years old?' })
    fireEvent.click(screen.getByRole('button', { name: 'Save' }))

    expect(await screen.findByText('PUT failed')).toBeInTheDocument()
    expect(screen.queryByText('Quotes list stub')).not.toBeInTheDocument()
  })
})
