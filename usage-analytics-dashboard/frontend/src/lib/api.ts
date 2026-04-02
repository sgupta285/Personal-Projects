import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
})

export async function fetchMetricCatalog() {
  const { data } = await api.get('/metric-catalog')
  return data
}

export async function fetchSummary(params: Record<string, string>) {
  const { data } = await api.get('/usage/summary', { params })
  return data
}

export async function fetchBreakdown(params: Record<string, string>) {
  const { data } = await api.get('/usage/breakdown', { params })
  return data
}
