const API_BASE = '/api'

class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.status = status
    this.data = data
  }
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  }

  try {
    const response = await fetch(url, config)

    const data = await response.json()

    if (!response.ok) {
      // Parse Django REST Framework field-specific validation errors
      let message = 'Request failed'
      if (typeof data === 'object' && data !== null) {
        const errors = []
        for (const [field, value] of Object.entries(data)) {
          if (Array.isArray(value)) {
            errors.push(...value)
          } else if (typeof value === 'string') {
            errors.push(value)
          }
        }
        if (errors.length > 0) {
          message = errors.join('. ')
        } else if (data.message) {
          message = data.message
        }
      }

      throw new ApiError(message, response.status, data)
    }

    return data
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    throw new ApiError('Network error', 0, { originalError: error })
  }
}

export const api = {
  // Profiles
  getProfiles: () => request('/profiles/'),
  getProfile: (id) => request(`/profiles/${id}/`),

  // Simulation
  runSimulation: (config, numTeams = 10, startDate) => request('/profiles/simulate/', {
    method: 'POST',
    body: JSON.stringify({ config, num_teams: numTeams, start_date: startDate })
  }),

  // Simulations (history)
  getSimulations: () => request('/simulations/'),
  getSimulation: (id) => request(`/simulations/${id}/`),
  getSimulationOverview: (id) => request(`/simulations/${id}/overview/`),

  // Analytics
  getProfileDays: (id, day) => request(`/profiles/${id}/days/${day}/`),
  getProfileOverview: (id, day) => request(`/profiles/${id}/overview/${day}/`),
  getOverviewByDay: (day) => request(`/profiles/overview/${day}/`),
  getOverviewTotal: () => request('/profiles/overview/')
}
