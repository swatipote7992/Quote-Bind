import { render, screen, waitFor } from '@testing-library/react'
import { QuestionsDataGrid } from '../../src/components/QuestionsDataGrid'
import { getQuestions } from '../../src/api/questions'
import type { QuestionDto } from '../../src/types/question_model'

jest.mock('../../src/api/questions', () => ({
  getQuestions: jest.fn(),
}))

const mockedGetQuestions = jest.mocked(getQuestions)

const sampleQuestion: QuestionDto = {
  question_id: 1,
  question_label: 'Are you 18 years old?',
  default_answer: 'Yes',
}

describe('QuestionsDataGrid', () => {
  afterEach(() => {
    mockedGetQuestions.mockReset()
  })

  it('renders question rows once loaded', async () => {
    mockedGetQuestions.mockResolvedValue([sampleQuestion])

    render(<QuestionsDataGrid />)

    expect(await screen.findByText('Are you 18 years old?')).toBeInTheDocument()
    expect(screen.getByText('Yes')).toBeInTheDocument()
  })

  it('renders an empty grid with no rows when there are no questions', async () => {
    mockedGetQuestions.mockResolvedValue([])

    render(<QuestionsDataGrid />)

    await waitFor(() => expect(mockedGetQuestions).toHaveBeenCalledTimes(1))
    expect(await screen.findByText('No rows')).toBeInTheDocument()
  })

  it('shows an error message when the request fails', async () => {
    mockedGetQuestions.mockRejectedValue(new Error('Network down'))

    render(<QuestionsDataGrid />)

    expect(
      await screen.findByText(/Couldn't load questions: Network down/),
    ).toBeInTheDocument()
  })
})
