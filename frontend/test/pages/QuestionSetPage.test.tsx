import { render, screen } from '@testing-library/react'
import { QuestionSetPage } from '../../src/pages/QuestionSetPage'

jest.mock('../../src/components/QuestionsDataGrid', () => ({
  QuestionsDataGrid: () => <div data-testid="questions-data-grid-stub" />,
}))

describe('QuestionSetPage', () => {
  it('renders the Question Set heading and grid', () => {
    render(<QuestionSetPage />)

    expect(screen.getByRole('heading', { name: 'Question Set' })).toBeInTheDocument()
    expect(screen.getByTestId('questions-data-grid-stub')).toBeInTheDocument()
  })
})
