import { render, screen } from '@testing-library/react'
import { QuestionsPage } from '../../src/pages/QuestionsPage'

jest.mock('../../src/components/QuestionsDataGrid', () => ({
  QuestionsDataGrid: () => <div data-testid="questions-data-grid-stub" />,
}))

describe('QuestionsPage', () => {
  it('renders the Questions heading and grid', () => {
    render(<QuestionsPage />)

    expect(screen.getByRole('heading', { name: 'Questions' })).toBeInTheDocument()
    expect(screen.getByTestId('questions-data-grid-stub')).toBeInTheDocument()
  })
})
