import Card from '../components/Card'
import Button from '../components/Button'

export default function Dashboard({ navigate }) {
  return (
    <div className="space-y-6">
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Wall Construction Tracker
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Track ice usage and construction costs for the Great Wall of the North
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <h3 className="text-lg font-semibold mb-2">Run Simulation</h3>
          <p className="text-gray-600 mb-4">
            Configure wall sections and simulate construction progress
          </p>
          <Button onClick={() => navigate('simulation')}>
            Start Simulation
          </Button>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-2">View Results</h3>
          <p className="text-gray-600 mb-4">
            Analyze ice usage and construction costs by day
          </p>
          <Button variant="secondary" onClick={() => navigate('results')}>
            View Results
          </Button>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-2">API Documentation</h3>
          <p className="text-gray-600 mb-4">
            Explore the REST API endpoints
          </p>
          <Button variant="secondary" onClick={() => window.location.href = '/api/'}>
            Browse API
          </Button>
        </Card>
      </div>
    </div>
  )
}
