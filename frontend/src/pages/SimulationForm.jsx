import { useState } from 'react'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import Spinner from '../components/Spinner'
import { api } from '../utils/api'

export default function SimulationForm({ navigate }) {
  const [config, setConfig] = useState('21 25 28\n17\n17 22 17 19 17')
  const [numTeams, setNumTeams] = useState('10')
  const [startDate, setStartDate] = useState('2025-10-20')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await api.runSimulation(config, parseInt(numTeams), startDate)
      setResult(data)
    } catch (err) {
      setError(err.message || 'Simulation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Run Simulation</h1>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Wall Configuration
              <span className="text-red-500 ml-1">*</span>
            </label>
            <textarea
              value={config}
              onChange={(e) => setConfig(e.target.value)}
              required
              rows="6"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter wall section heights (space or newline separated)"
            />
            <p className="text-sm text-gray-500 mt-1">
              Example: "21 25 28" creates 3 sections with heights 21, 25, and 28 feet
            </p>
          </div>

          <Input
            label="Number of Teams"
            type="number"
            value={numTeams}
            onChange={setNumTeams}
            required
            placeholder="10"
          />

          <Input
            label="Start Date"
            type="date"
            value={startDate}
            onChange={setStartDate}
            required
          />

          <Button type="submit" disabled={loading}>
            {loading ? 'Running Simulation...' : 'Run Simulation'}
          </Button>
        </form>

        {loading && <Spinner />}

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {result && (
          <div className="mt-6 space-y-4">
            <h2 className="text-xl font-semibold text-green-600">Simulation Complete!</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Total Sections</p>
                <p className="text-2xl font-bold text-blue-600">{result.total_sections}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Total Days</p>
                <p className="text-2xl font-bold text-green-600">{result.total_days}</p>
              </div>
            </div>
            <Button onClick={() => navigate('results')}>
              View Detailed Results
            </Button>
          </div>
        )}
      </Card>
    </div>
  )
}
