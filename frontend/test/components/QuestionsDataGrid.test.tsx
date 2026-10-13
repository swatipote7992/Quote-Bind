import { render, screen, waitFor } from '@testing-library/react'
import { QuestionsDataGrid } from '../../src/components/QuestionsDataGrid'
import { getQuestionsPage } from '../../src/api/questions'
import type {
  QuestionDto,
  QuestionPageDto,
} from '../../src/types/question_model'

jest.mock('../../src/api/questions', () => ({
  getQuestionsPage: jest.fn(),
}))

const mockedGetQuestionsPage = jest.mocked(getQuestionsPage)

const sampleQuestion: QuestionDto = {
  question_id: 1,
  question_label: 'Are you 18 years old?',
  default_answer: 'Yes',
}

function pageOf(data: QuestionDto[], total = data.length): QuestionPageDto {
  return { data, page: 1, page_size: 10, total, total_pages: 1 }
}

describe('QuestionsDataGrid', () => {
  afterEach(() => {
    mockedGetQuestionsPage.mockReset()
  })

  it('renders question rows once loaded', async () => {
    mockedGetQuestionsPage.mockResolvedValue(pageOf([sampleQuestion]))

    render(<QuestionsDataGrid />)

    expect(await screen.findByText('Are you 18 years old?')).toBeInTheDocument()
    expect(screen.getByText('Yes')).toBeInTheDocument()
  })

  it('requests the first page with the default page size', async () => {
    mockedGetQuestionsPage.mockResolvedValue(pageOf([sampleQuestion]))

    render(<QuestionsDataGrid />)

    await waitFor(() =>
      expect(mockedGetQuestionsPage).toHaveBeenCalledWith(1, 10),
    )
  })

  it('renders an empty grid with no rows when there are no questions', async () => {
    mockedGetQuestionsPage.mockResolvedValue(pageOf([]))

    render(<QuestionsDataGrid />)

    await waitFor(() => expect(mockedGetQuestionsPage).toHaveBeenCalledTimes(1))
    expect(await screen.findByText('No rows')).toBeInTheDocument()
  })

  it('shows an error message when the request fails', async () => {
    mockedGetQuestionsPage.mockRejectedValue(new Error('Network down'))

    render(<QuestionsDataGrid />)

    expect(
      await screen.findByText(/Couldn't load questions: Network down/),
    ).toBeInTheDocument()
  })

  it('provides a quick-filter search box for filtering records', async () => {
    mockedGetQuestionsPage.mockResolvedValue(pageOf([sampleQuestion]))

    render(<QuestionsDataGrid />)

    await screen.findByText('Are you 18 years old?')

    expect(screen.getByRole('searchbox')).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /show filters/i }),
    ).toBeInTheDocument()
  })
})
