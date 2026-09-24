import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QuotesDataGrid } from '../../src/components/QuotesDataGrid'
import { deleteQuote, getQuotes } from '../../src/api/quotes'
import type { QuoteDto } from '../../src/types/quote_model'

jest.mock('../../src/api/quotes', () => ({
  getQuotes: jest.fn(),
  deleteQuote: jest.fn(),
}))

const mockedGetQuotes = jest.mocked(getQuotes)
const mockedDeleteQuote = jest.mocked(deleteQuote)

function renderGrid() {
  return render(
    <MemoryRouter initialEntries={['/quotes']}>
      <Routes>
        <Route path="/quotes" element={<QuotesDataGrid />} />
        <Route path="/quotes/:quoteId/edit" element={<div>Edit page stub</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

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
  question_set: [
    {
      question_id: 1,
      question_label: 'Are you 18 years old?',
      default_answer: 'Yes',
      answer: 'No',
    },
  ],
  created_at: '2026-01-01T10:00:00Z',
  updated_at: '2026-01-01T10:00:00Z',
}

const otherQuote: QuoteDto = {
  ...sampleQuote,
  id: 'Q002',
  applicant: { ...sampleQuote.applicant, first_name: 'Mark', last_name: 'Evans' },
}

describe('QuotesDataGrid', () => {
  afterEach(() => {
    mockedGetQuotes.mockReset()
    mockedDeleteQuote.mockReset()
  })

  it('renders quote rows once loaded', async () => {
    mockedGetQuotes.mockResolvedValue([sampleQuote])

    renderGrid()

    expect(await screen.findByText('Q001')).toBeInTheDocument()
    expect(screen.getByText('Jane Doe')).toBeInTheDocument()
    expect(screen.getByText('jane.doe@example.com')).toBeInTheDocument()
    expect(screen.getByText('7700900123')).toBeInTheDocument()
  })

  it('lists quotes newest first, sorted by id descending', async () => {
    mockedGetQuotes.mockResolvedValue([
      { ...sampleQuote, id: 'Q009' },
      { ...sampleQuote, id: 'Q1000' },
      { ...sampleQuote, id: 'Q010' },
    ])

    renderGrid()

    await screen.findByText('Q1000')
    const ids = screen
      .getAllByRole('row')
      .filter((row) => row.getAttribute('data-id'))
      .map((row) => row.getAttribute('data-id'))
    expect(ids).toEqual(['Q1000', 'Q010', 'Q009'])
  })

  it('renders an empty grid with no rows when there are no quotes', async () => {
    mockedGetQuotes.mockResolvedValue([])

    renderGrid()

    await waitFor(() => expect(mockedGetQuotes).toHaveBeenCalledTimes(1))
    expect(await screen.findByText('No rows')).toBeInTheDocument()
  })

  it('shows an error message when the request fails', async () => {
    mockedGetQuotes.mockRejectedValue(new Error('Network down'))

    renderGrid()

    expect(
      await screen.findByText(/Couldn't load quotes: Network down/),
    ).toBeInTheDocument()
  })

  it('provides a quick-filter search box for filtering records', async () => {
    mockedGetQuotes.mockResolvedValue([sampleQuote, otherQuote])

    renderGrid()

    await screen.findByText('Jane Doe')

    // The filtering behavior itself is MUI's own (well-tested) DataGrid
    // logic; this confirms the toolbar + quick filter are actually wired
    // up and rendered, i.e. that a user genuinely has a way to filter.
    expect(screen.getByRole('searchbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /show filters/i })).toBeInTheDocument()
  })

  it('shows each question with its default answer and answer in a dialog', async () => {
    mockedGetQuotes.mockResolvedValue([sampleQuote])

    renderGrid()

    await screen.findByText('Q001')
    fireEvent.click(screen.getByRole('button', { name: 'View (1)' }))

    const dialog = await screen.findByRole('dialog')
    const row = within(dialog).getByRole('row', { name: /Are you 18 years old\?/ })
    expect(within(row).getAllByRole('cell').map((cell) => cell.textContent)).toEqual([
      'Are you 18 years old?',
      'Yes',
      'No',
    ])

    fireEvent.click(within(dialog).getByRole('button', { name: 'Close' }))
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('navigates to the edit page when Edit is clicked', async () => {
    mockedGetQuotes.mockResolvedValue([sampleQuote])

    renderGrid()

    await screen.findByText('Q001')
    fireEvent.click(screen.getByRole('button', { name: 'Edit' }))

    expect(await screen.findByText('Edit page stub')).toBeInTheDocument()
  })

  it('closes the confirm dialog without deleting on Cancel', async () => {
    mockedGetQuotes.mockResolvedValue([sampleQuote])

    renderGrid()

    await screen.findByText('Q001')
    fireEvent.click(screen.getByRole('button', { name: 'Delete' }))

    const dialog = await screen.findByRole('dialog')
    fireEvent.click(within(dialog).getByRole('button', { name: 'Cancel' }))

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(mockedDeleteQuote).not.toHaveBeenCalled()
    expect(screen.getByText('Q001')).toBeInTheDocument()
  })

  it('deletes the quote and removes the row on OK', async () => {
    mockedGetQuotes.mockResolvedValue([sampleQuote, otherQuote])
    mockedDeleteQuote.mockResolvedValue(undefined)

    renderGrid()

    await screen.findByText('Q001')
    const q001Row = screen.getByText('Q001').closest('[role="row"]') as HTMLElement
    fireEvent.click(within(q001Row).getByRole('button', { name: 'Delete' }))

    const dialog = await screen.findByRole('dialog')
    fireEvent.click(within(dialog).getByRole('button', { name: 'OK' }))

    await waitFor(() => expect(mockedDeleteQuote).toHaveBeenCalledWith('Q001'))
    await waitFor(() => expect(screen.queryByText('Q001')).not.toBeInTheDocument())
    expect(screen.getByText('Q002')).toBeInTheDocument()
  })
})
