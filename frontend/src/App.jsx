import { useState, useEffect } from 'react'
import Dashboard from './pages/Dashboard'
import SimulationForm from './pages/SimulationForm'
import SimulationResults from './pages/SimulationResults'

function App() {
  const [route, setRoute] = useState(window.location.hash.slice(1) || 'dashboard')
  const [params, setParams] = useState({})

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1)
      const [path, query] = hash.split('?')
      setRoute(path || 'dashboard')

      // Parse query params
      const searchParams = new URLSearchParams(query)
      const paramsObj = {}
      searchParams.forEach((value, key) => {
        paramsObj[key] = value
      })
      setParams(paramsObj)
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  const navigate = (path, queryParams = {}) => {
    const query = new URLSearchParams(queryParams).toString()
    window.location.hash = query ? `${path}?${query}` : path
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm mb-8">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-gray-900">
              Wall Construction Tracker
            </h1>
            <div className="flex gap-4">
              <button
                onClick={() => navigate('dashboard')}
                className={`px-3 py-2 rounded-md ${
                  route === 'dashboard'
                    ? 'bg-blue-100 text-blue-700 font-semibold'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => navigate('simulation')}
                className={`px-3 py-2 rounded-md ${
                  route === 'simulation'
                    ? 'bg-blue-100 text-blue-700 font-semibold'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Run Simulation
              </button>
              <button
                onClick={() => navigate('results')}
                className={`px-3 py-2 rounded-md ${
                  route === 'results'
                    ? 'bg-blue-100 text-blue-700 font-semibold'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                View Results
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 pb-12">
        {route === 'dashboard' && <Dashboard navigate={navigate} params={params} />}
        {route === 'simulation' && <SimulationForm navigate={navigate} params={params} />}
        {route === 'results' && <SimulationResults navigate={navigate} params={params} />}
      </main>
    </div>
  )
}

export default App
