import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  FormControl,
  FormControlLabel,
  FormLabel,
  MenuItem,
  Paper,
  Radio,
  RadioGroup,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { getProductQuestions, getProducts } from '../api/products'
import { createQuote, getQuote, updateQuote } from '../api/quotes'
import type { ProductDto } from '../types/product_model'
import type { QuestionDto } from '../types/question_model'
import type { QuestionAnswerDto, QuoteCreateDto } from '../types/quote_model'

interface FormValues {
  product_id: string
  applicant_id: string
  first_name: string
  last_name: string
  email: string
  phone: string
  date_of_birth: string
}

// New quotes use this applicant. Applicant ID, phone and date of birth aren't
// shown on the form, but the API requires them, so they're sent from here (or,
// when editing, from the quote as loaded).
const defaultValues: FormValues = {
  product_id: '',
  applicant_id: '1001',
  first_name: 'Quote',
  last_name: 'Admin',
  email: 'quote.admin@gmail.com',
  phone: '123-456-7890',
  date_of_birth: '1980-01-01',
}

interface QuestionsResult {
  productId: string
  questions: QuestionDto[]
  // Current answer per question_id.
  answers: Record<number, string>
  error: string | null
}

// Answers already saved on the quote being edited, for its own product.
interface SavedAnswers {
  productId: string
  answers: Record<number, string>
}

const baseAnswerOptions = ['Yes', 'No']

function answerOptions(question: QuestionDto, current: string): string[] {
  return [...new Set([...baseAnswerOptions, question.default_answer, current])]
}

function toAnswers(result: QuestionsResult | null): QuestionAnswerDto[] | undefined {
  if (!result || result.error) return undefined
  return result.questions.map((question) => ({
    question_id: question.question_id,
    answer: result.answers[question.question_id] ?? question.default_answer,
  }))
}

function toPayload(values: FormValues, answers?: QuestionAnswerDto[]): QuoteCreateDto {
  return {
    answers,
    product_id: Number(values.product_id),
    applicant: {
      applicant_id: Number(values.applicant_id),
      first_name: values.first_name.trim(),
      last_name: values.last_name.trim(),
      email: values.email.trim(),
      phone: values.phone.trim(),
      date_of_birth: values.date_of_birth,
    },
  }
}

export function QuoteFormPage() {
  const { quoteId } = useParams<{ quoteId: string }>()
  const navigate = useNavigate()
  const isEdit = quoteId !== undefined

  const [values, setValues] = useState<FormValues>(defaultValues)
  const [products, setProducts] = useState<ProductDto[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [questionsResult, setQuestionsResult] = useState<QuestionsResult | null>(null)
  const [savedAnswers, setSavedAnswers] = useState<SavedAnswers | null>(null)

  useEffect(() => {
    let cancelled = false

    Promise.all([getProducts(), quoteId ? getQuote(quoteId) : Promise.resolve(null)])
      .then(([productList, quote]) => {
        if (cancelled) return
        setProducts(productList)
        if (quote) {
          setValues({
            product_id: String(quote.product_id),
            applicant_id: String(quote.applicant.applicant_id),
            first_name: quote.applicant.first_name,
            last_name: quote.applicant.last_name,
            email: quote.applicant.email,
            phone: quote.applicant.phone,
            date_of_birth: quote.applicant.date_of_birth,
          })
          setSavedAnswers({
            productId: String(quote.product_id),
            answers: Object.fromEntries(
              quote.question_set.map((item) => [item.question_id, item.answer]),
            ),
          })
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load the form')
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [quoteId])

  // Load the selected product's questions (question_set -> question_array ->
  // question_catalog, resolved by the API) whenever the product changes.
  useEffect(() => {
    if (!values.product_id) return

    let cancelled = false
    const productId = values.product_id

    getProductQuestions(Number(productId))
      .then((questions) => {
        if (cancelled) return
        // Start from each question's default answer, then apply the answers
        // already saved on this quote (only while its product is unchanged).
        const saved = savedAnswers?.productId === productId ? savedAnswers.answers : {}
        const answers = Object.fromEntries(
          questions.map((question) => [
            question.question_id,
            saved[question.question_id] ?? question.default_answer,
          ]),
        )
        setQuestionsResult({ productId, questions, answers, error: null })
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setQuestionsResult({
            productId,
            questions: [],
            answers: {},
            error: err instanceof Error ? err.message : 'Failed to load questions',
          })
        }
      })

    return () => {
      cancelled = true
    }
  }, [values.product_id, savedAnswers])

  const questionsLoading =
    values.product_id !== '' && questionsResult?.productId !== values.product_id
  const questions =
    questionsResult?.productId === values.product_id ? questionsResult : null

  const handleChange =
    (field: keyof FormValues) => (event: React.ChangeEvent<HTMLInputElement>) => {
      setValues((prev) => ({ ...prev, [field]: event.target.value }))
    }

  const handleAnswerChange = (questionId: number, answer: string) => {
    setQuestionsResult((prev) =>
      prev ? { ...prev, answers: { ...prev.answers, [questionId]: answer } } : prev,
    )
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setSaving(true)
    setError(null)

    try {
      const payload = toPayload(values, toAnswers(questions))
      if (quoteId) {
        await updateQuote(quoteId, payload)
      } else {
        await createQuote(payload)
      }
      navigate('/quotes')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save the quote')
      setSaving(false)
    }
  }

  return (
    <>
      <Typography
        variant="h1"
        sx={{ mb: 3, fontSize: '1.5rem', fontWeight: 600, letterSpacing: '-0.025em' }}
      >
        {isEdit ? `Edit Quote ${quoteId}` : 'New Quote'}
      </Typography>

      <Paper variant="outlined" sx={{ p: 3 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress aria-label="Loading" />
          </Box>
        ) : (
          <Box component="form" onSubmit={handleSubmit}>
            <Stack spacing={2.5}>
              {error && <Alert severity="error">{error}</Alert>}

              <TextField
                select
                required
                label="Product"
                value={values.product_id}
                onChange={handleChange('product_id')}
              >
                {products.map((product) => (
                  <MenuItem key={product.product_id} value={String(product.product_id)}>
                    {product.product_label}
                  </MenuItem>
                ))}
              </TextField>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2.5}>
                <TextField
                  required
                  fullWidth
                  label="First name"
                  value={values.first_name}
                  onChange={handleChange('first_name')}
                />
                <TextField
                  required
                  fullWidth
                  label="Last name"
                  value={values.last_name}
                  onChange={handleChange('last_name')}
                />
              </Stack>

              <TextField
                required
                label="Email"
                type="email"
                value={values.email}
                onChange={handleChange('email')}
              />

              {values.product_id && (
                <Box>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="h2" sx={{ fontSize: '1.1rem', fontWeight: 600 }}>
                    Questions
                  </Typography>
                  {questionsLoading && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                      <CircularProgress size={24} aria-label="Loading questions" />
                    </Box>
                  )}
                  {questions?.error && (
                    <Alert severity="error" sx={{ mt: 1 }}>
                      Couldn't load questions: {questions.error}
                    </Alert>
                  )}
                  {questions && !questions.error && questions.questions.length === 0 && (
                    <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
                      This product has no questions.
                    </Typography>
                  )}
                  {questions && questions.questions.length > 0 && (
                    <Stack spacing={2} sx={{ mt: 1 }}>
                      {questions.questions.map((question) => {
                        const answer =
                          questions.answers[question.question_id] ?? question.default_answer
                        return (
                          <FormControl key={question.question_id}>
                            <FormLabel id={`question-${question.question_id}-label`}>
                              {question.question_label}
                            </FormLabel>
                            <RadioGroup
                              row
                              aria-labelledby={`question-${question.question_id}-label`}
                              value={answer}
                              onChange={(event) =>
                                handleAnswerChange(question.question_id, event.target.value)
                              }
                            >
                              {answerOptions(question, answer).map((option) => (
                                <FormControlLabel
                                  key={option}
                                  value={option}
                                  control={<Radio />}
                                  label={option}
                                />
                              ))}
                            </RadioGroup>
                          </FormControl>
                        )
                      })}
                    </Stack>
                  )}
                </Box>
              )}

              <Stack direction="row" spacing={2} sx={{ justifyContent: 'flex-end' }}>
                <Button variant="outlined" onClick={() => navigate('/quotes')}>
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={saving || questionsLoading}
                >
                  {saving ? 'Saving…' : 'Save'}
                </Button>
              </Stack>
            </Stack>
          </Box>
        )}
      </Paper>
    </>
  )
}
