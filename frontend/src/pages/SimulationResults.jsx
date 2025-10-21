import { useState, useEffect } from 'react'
import Card from '../components/Card'
import Spinner from '../components/Spinner'
import SimulationSelector from '../components/SimulationSelector'
import WallSegmentGrid from '../components/WallSegmentGrid'
import { api } from '../utils/api'
import { formatNumber } from '../utils/format'

export default function SimulationResults({ navigate }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [simulations, setSimulations] = useState([])
  const [selectedSimId, setSelectedSimId] = useState(null)
  const [simulationData, setSimulationData] = useState(null)
  const [overviewData, setOverviewData] = useState(null)

  // Fetch list of simulations on mount
  useEffect(() => {
    async function fetchSimulations() {
      try {
        setLoading(true)
        const sims = await api.getSimulations()
        setSimulations(sims)

        // Auto-select most recent simulation
        if (sims.length > 0) {
          setSelectedSimId(sims[0].id)
        } else {
          setError('No simulations found')
        }
      } catch (err) {
        setError(err.message || 'Failed to load simulations')
      } finally {
        setLoading(false)
      }
    }
    fetchSimulations()
  }, [])

  // Fetch selected simulation details
  useEffect(() => {
    if (!selectedSimId) return

    async function fetchSimulationDetails() {
      try {
        setLoading(true)
        const [simDetails, overview] = await Promise.all([
          api.getSimulation(selectedSimId),
          api.getSimulationOverview(selectedSimId)
        ])
        setSimulationData(simDetails)
        setOverviewData(overview)
      } catch (err) {
        setError(err.message || 'Failed to load simulation details')
      } finally {
        setLoading(false)
      }
    }
    fetchSimulationDetails()
  }, [selectedSimId])

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

  if (!simulationData || !overviewData) {
    return <Spinner />
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString()
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Simulation Results</h1>

      {/* Simulation Selector */}
      <SimulationSelector
        simulations={simulations}
        selectedId={selectedSimId}
        onSelect={setSelectedSimId}
      />

      {/* Total Cost and Completion Time */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold mb-2">Total Cost</h3>
          <p className="text-4xl font-bold text-[var(--color-gold)]">
            {formatNumber(overviewData.cost)} GD
          </p>
          <p className="text-sm text-gray-500 mt-2">Gold Dragons</p>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-2">Completion Time</h3>
          <p className="text-4xl font-bold text-blue-600">
            {overviewData.day || 'N/A'} {overviewData.day === 1 ? 'day' : 'days'}
          </p>
          <p className="text-sm text-gray-500 mt-2">Total construction time</p>
        </Card>
      </div>

      {/* Input Summary */}
      <Card>
        <h3 className="text-lg font-semibold mb-4">Input Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-gray-700">
          <div>
            <span className="font-medium">Teams:</span> {simulationData.num_teams}
          </div>
          <div>
            <span className="font-medium">Start Date:</span> {formatDate(simulationData.start_date)}
          </div>
          <div>
            <span className="font-medium">Total Sections:</span> {simulationData.total_sections}
          </div>
        </div>
      </Card>

      {/* Wall Segments Grid */}
      <Card>
        <WallSegmentGrid profiles={simulationData.profiles} />
      </Card>
    </div>
  )
}
