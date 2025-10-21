import PropTypes from 'prop-types'

/**
 * SimulationSelector provides a dropdown to select between simulations
 *
 * @param {Object} props
 * @param {Array} props.simulations - Array of simulation objects
 * @param {number} props.selectedId - Currently selected simulation ID
 * @param {Function} props.onSelect - Callback when simulation is selected
 * @returns {JSX.Element}
 */
export default function SimulationSelector({ simulations, selectedId, onSelect }) {
  if (!simulations || simulations.length === 0) {
    return null
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString()
  }

  return (
    <div className="mb-6">
      <label htmlFor="simulation-select" className="block text-sm font-medium text-gray-700 mb-2">
        Select Simulation
      </label>
      <select
        id="simulation-select"
        className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        value={selectedId || ''}
        onChange={(e) => onSelect(parseInt(e.target.value, 10))}
      >
        {simulations.map((simulation) => (
          <option key={simulation.id} value={simulation.id}>
            Simulation #{simulation.id} - {formatDate(simulation.start_date)} ({simulation.num_teams} teams, {simulation.total_sections} sections)
          </option>
        ))}
      </select>
    </div>
  )
}

SimulationSelector.propTypes = {
  simulations: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      start_date: PropTypes.string.isRequired,
      num_teams: PropTypes.number.isRequired,
      total_sections: PropTypes.number.isRequired,
    })
  ).isRequired,
  selectedId: PropTypes.number,
  onSelect: PropTypes.func.isRequired,
}
