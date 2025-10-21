import { useState, useEffect } from 'react'
import Card from '../components/Card'
import Spinner from '../components/Spinner'
import { api } from '../utils/api'
import { formatNumber } from '../utils/format'

export default function SimulationResults({ navigate }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [data, setData] = useState(null)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        const result = await api.getOverviewTotal()
        setData(result)
      } catch (err) {
        setError(err.message || 'Failed to load results')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) return <Spinner />

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <div className="text-center py-12">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              No Simulation Data
            </h2>
            <p className="text-gray-600 mb-6">
              {error}
            </p>
            <button
              onClick={() => navigate('simulation')}
              className="text-blue-600 hover:underline"
            >
              Run a simulation first
            </button>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Simulation Results</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold mb-2">Total Cost</h3>
          <p className="text-4xl font-bold text-[var(--color-gold)]">
            {formatNumber(data.cost)} GD
          </p>
          <p className="text-sm text-gray-500 mt-2">Gold Dragons</p>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-2">Completion Time</h3>
          <p className="text-4xl font-bold text-blue-600">
            {data.day || 'N/A'} {data.day === 1 ? 'day' : 'days'}
          </p>
          <p className="text-sm text-gray-500 mt-2">Total construction time</p>
        </Card>
      </div>

      <Card>
        <h3 className="text-lg font-semibold mb-4">Construction Overview</h3>
        <p className="text-gray-600">
          The simulation has been completed successfully. Total cost for the entire
          construction project is <strong>{formatNumber(data.cost)} Gold Dragons</strong>.
        </p>
      </Card>
    </div>
  )
}
