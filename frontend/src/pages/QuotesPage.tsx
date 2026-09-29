import { useNavigate } from 'react-router-dom'
import { Box, Button, Typography } from '@mui/material'
import { QuotesDataGrid } from '../components/QuotesDataGrid'

export function QuotesPage() {
  const navigate = useNavigate()

  return (
    <>
      <Box
        sx={{
          mb: 3,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Typography
          variant="h1"
          sx={{ fontSize: '1.5rem', fontWeight: 600, letterSpacing: '-0.025em' }}
        >
          Quotes
        </Typography>
        <Button variant="contained" onClick={() => navigate('/quotes/new')}>
          New Quote
        </Button>
      </Box>
      <QuotesDataGrid />
    </>
  )
}
