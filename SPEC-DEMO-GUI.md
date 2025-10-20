# Wall Construction API - GUI Technical Specification

## Philosophy: Minimal Dependencies, Maximum Standards

This specification defines a **production-ready React GUI** with an absolute minimal dependency footprint while adhering to 2025 industry best practices.

**Core Principle**: Every dependency must justify its existence. No bloat, no convenience libraries that add marginal value.

---

## Technology Stack

### Framework & Build Tools
- **React 19.2.0** (October 2025 release)
  - Latest stable with React Compiler
  - Actions API for async operations
  - Enhanced form handling
  - Improved hydration and error reporting

- **Vite 7.0** (2025 release)
  - Requires Node.js 20.19+ or 22.12+
  - ESM-only distribution
  - Native `require(esm)` support
  - 5x faster builds than Vite 6
  - Instant HMR (Hot Module Replacement)

### Styling & UI
- **Tailwind CSS v4.0** (January 2025)
  - Zero configuration setup
  - Single CSS import: `@import "tailwindcss"`
  - Built-in Vite plugin
  - 5x faster full builds, 100x faster incremental builds
  - Modern CSS features (cascade layers, @property, color-mix)
  - P3 color palette for vibrant displays
  - Container queries support

### Data Visualization
- **Recharts 2.x** (latest)
  - 24.8k GitHub stars
  - React-native component API
  - SVG-based rendering
  - Responsive by default
  - Composable chart primitives
  - Built on D3.js submodules

### HTTP & State
- **Native Fetch API** (no axios, no external HTTP libs)
- **React useState/useReducer** (no Redux, no Zustand, no external state libs)

---

## Dependencies

### Production Dependencies (3 total)
```json
{
  "react": "^19.2.0",
  "react-dom": "^19.2.0",
  "recharts": "^2.15.0"
}
```

### Development Dependencies (2 total)
```json
{
  "vite": "^7.0.0",
  "@tailwindcss/vite": "^4.0.0"
}
```

**Total: 5 dependencies**

---

## Project Structure

```
wall-construction-gui/
├── public/
│   └── favicon.ico
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Button.jsx
│   │   ├── Card.jsx
│   │   ├── Input.jsx
│   │   ├── Select.jsx
│   │   ├── DatePicker.jsx
│   │   ├── Spinner.jsx
│   │   ├── ErrorBoundary.jsx
│   │   └── charts/
│   │       ├── LineChart.jsx
│   │       ├── BarChart.jsx
│   │       └── AreaChart.jsx
│   ├── pages/               # Page-level components
│   │   ├── Dashboard.jsx
│   │   ├── ProfileDetail.jsx
│   │   ├── ProgressForm.jsx
│   │   ├── DailyIceUsage.jsx
│   │   └── CostAnalytics.jsx
│   ├── hooks/               # Custom React hooks
│   │   ├── useApi.js
│   │   ├── useFetch.js
│   │   └── useDebounce.js
│   ├── utils/               # Helper functions
│   │   ├── api.js           # Fetch wrapper
│   │   ├── formatters.js    # Number/date formatting
│   │   └── constants.js     # App constants
│   ├── App.jsx              # Root component
│   ├── main.jsx             # Entry point
│   └── index.css            # Global styles
├── index.html
├── vite.config.js
└── package.json
```

---

## Setup Instructions

### 1. Initialize Project

```bash
# Create Vite project
npm create vite@latest wall-construction-gui -- --template react

cd wall-construction-gui
```

### 2. Install Dependencies

```bash
# Install production dependencies
npm install react@19.2.0 react-dom@19.2.0 recharts

# Install dev dependencies
npm install -D vite@7 @tailwindcss/vite@4
```

### 3. Configure Vite

**vite.config.js**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 4. Setup Tailwind CSS

**src/index.css**
```css
@import "tailwindcss";

/* CSS Custom Properties for Theme */
:root {
  --color-primary: #3b82f6;
  --color-secondary: #64748b;
  --color-success: #10b981;
  --color-danger: #ef4444;
  --color-warning: #f59e0b;
  --color-ice: #93c5fd;
  --color-gold: #fbbf24;
}

/* Global Styles */
body {
  @apply bg-gray-50 text-gray-900;
}
```

### 5. Run Development Server

```bash
npm run dev
```

Server starts at `http://localhost:5173`

---

## Component Architecture

### Base Components

#### Button Component
```jsx
// src/components/Button.jsx
export default function Button({
  children,
  variant = 'primary',
  onClick,
  disabled = false,
  type = 'button'
}) {
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900',
    danger: 'bg-red-600 hover:bg-red-700 text-white'
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        px-4 py-2 rounded-lg font-medium
        transition-colors duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]}
      `}
    >
      {children}
    </button>
  )
}
```

#### Card Component
```jsx
// src/components/Card.jsx
export default function Card({ children, className = '' }) {
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      {children}
    </div>
  )
}
```

#### Input Component
```jsx
// src/components/Input.jsx
export default function Input({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  error
}) {
  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className={`
          w-full px-4 py-2 border rounded-lg
          focus:outline-none focus:ring-2 focus:ring-blue-500
          ${error ? 'border-red-500' : 'border-gray-300'}
        `}
      />
      {error && (
        <p className="text-red-500 text-sm mt-1">{error}</p>
      )}
    </div>
  )
}
```

### Chart Components

#### LineChart Wrapper
```jsx
// src/components/charts/LineChart.jsx
import {
  LineChart as RechartsLine,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

export default function LineChart({ data, dataKey, xKey, color = '#3b82f6' }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsLine data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} />
        <YAxis />
        <Tooltip />
        <Line
          type="monotone"
          dataKey={dataKey}
          stroke={color}
          strokeWidth={2}
        />
      </RechartsLine>
    </ResponsiveContainer>
  )
}
```

#### BarChart Wrapper
```jsx
// src/components/charts/BarChart.jsx
import {
  BarChart as RechartsBar,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

export default function BarChart({ data, dataKey, xKey, color = '#10b981' }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsBar data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} />
        <YAxis />
        <Tooltip />
        <Bar dataKey={dataKey} fill={color} />
      </RechartsBar>
    </ResponsiveContainer>
  )
}
```

---

## Pages

### 1. Dashboard
**File**: `src/pages/Dashboard.jsx`

**Purpose**: Display all construction profiles as cards with summary statistics

**Data Source**: `GET /api/profiles/` + parallel `GET /api/profiles/{id}/cost-overview/`

**Components**:
- Grid of profile cards
- Summary statistics (total ice, total cost, total feet)
- "View Details" button per profile
- "+ New Profile" button

**Key Features**:
- Responsive grid (1 col mobile, 2 col tablet, 3 col desktop)
- Loading states with skeleton cards
- Empty state when no profiles exist
- Filter by active/inactive status

### 2. ProfileDetail
**File**: `src/pages/ProfileDetail.jsx`

**Purpose**: Detailed view of a single profile with cost analytics and daily breakdown

**Data Source**: `GET /api/profiles/{id}/cost-overview/?start_date=X&end_date=Y`

**Components**:
- Profile header (name, team lead)
- Summary cards (total cost, total ice, avg/day)
- Line chart: Daily cost trend
- Line chart: Daily feet built
- Area chart: Cumulative cost
- Data table: Daily breakdown

**Key Features**:
- Date range picker (default: last 30 days)
- Responsive charts
- Download CSV button (client-side generation)
- Print-friendly layout

### 3. ProgressForm
**File**: `src/pages/ProgressForm.jsx`

**Purpose**: Record daily construction progress for a wall section

**Data Source**: `POST /api/profiles/{id}/progress/`

**Components**:
- Profile selector dropdown
- Wall section selector
- Date picker (default: today)
- Feet built input (number)
- Notes textarea (optional)
- Real-time calculation display (ice usage, cost)
- Submit button

**Key Features**:
- Form validation (required fields, number validation)
- Real-time calculations using constants (195 yd³/ft, 1,900 GD/yd³)
- Success toast notification
- Error handling with user-friendly messages
- Clear form after submission

### 4. DailyIceUsage
**File**: `src/pages/DailyIceUsage.jsx`

**Purpose**: Breakdown of ice usage by wall section for a specific date

**Data Source**: `GET /api/profiles/{id}/daily-ice-usage/?date=YYYY-MM-DD`

**Components**:
- Profile selector
- Date picker
- Summary card (total feet, total ice)
- Horizontal bar chart (ice by section)
- Data table (section breakdown with percentages)

**Key Features**:
- Client-side percentage calculations
- Color-coded bars
- Sortable table columns
- Export to CSV

### 5. CostAnalytics
**File**: `src/pages/CostAnalytics.jsx`

**Purpose**: Multi-chart cost analytics dashboard

**Data Source**: `GET /api/profiles/{id}/cost-overview/?start_date=X&end_date=Y`

**Components**:
- Date range selector
- 4 summary cards (total cost, total feet, avg/day, days)
- Line chart: Daily cost
- Line chart: Daily feet built
- Area chart: Cumulative cost
- Compare profiles (optional enhancement)

**Key Features**:
- Multiple chart views in grid layout
- Responsive breakpoints
- Print view
- Share URL with date filters in query params

---

## API Integration

### API Client

**src/utils/api.js**
```javascript
const API_BASE = import.meta.env.DEV ? '/api' : 'https://api.example.com/api'

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
      throw new ApiError(
        data.message || 'Request failed',
        response.status,
        data
      )
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
  createProfile: (data) => request('/profiles/', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Progress
  recordProgress: (profileId, data) => request(`/profiles/${profileId}/progress/`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Analytics
  getDailyIceUsage: (profileId, date) =>
    request(`/profiles/${profileId}/daily-ice-usage/?date=${date}`),

  getCostOverview: (profileId, startDate, endDate) =>
    request(`/profiles/${profileId}/cost-overview/?start_date=${startDate}&end_date=${endDate}`)
}
```

### Custom Hooks

**src/hooks/useFetch.js**
```javascript
import { useState, useEffect } from 'react'

export function useFetch(fetchFn, dependencies = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false

    async function fetchData() {
      try {
        setLoading(true)
        setError(null)
        const result = await fetchFn()
        if (!cancelled) {
          setData(result)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchData()

    return () => {
      cancelled = true
    }
  }, dependencies)

  return { data, loading, error }
}
```

**Usage Example**:
```javascript
import { useFetch } from '../hooks/useFetch'
import { api } from '../utils/api'

function Dashboard() {
  const { data: profiles, loading, error } = useFetch(() => api.getProfiles())

  if (loading) return <Spinner />
  if (error) return <ErrorMessage error={error} />

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {profiles.results.map(profile => (
        <ProfileCard key={profile.id} profile={profile} />
      ))}
    </div>
  )
}
```

---

## State Management Strategy

### Component-Level State
Use `useState` for:
- Form inputs
- UI toggles (modals, dropdowns)
- Local loading/error states

### Lifted State
Use props drilling for:
- Shared data between sibling components
- Parent-child communication

**Example**:
```javascript
function App() {
  const [currentView, setCurrentView] = useState('dashboard')
  const [selectedProfile, setSelectedProfile] = useState(null)

  return (
    <div>
      <Navigation view={currentView} onNavigate={setCurrentView} />
      {currentView === 'dashboard' && (
        <Dashboard onSelectProfile={setSelectedProfile} />
      )}
      {currentView === 'profile' && (
        <ProfileDetail profile={selectedProfile} />
      )}
    </div>
  )
}
```

### When to Add Context
Only add React Context if:
- Props drilling exceeds 3 levels
- Data is truly global (theme, auth, language)
- Performance profiling shows re-render issues

**Not needed for this app initially**.

---

## Routing Strategy

### Hash-Based Routing (Minimal Approach)

**src/App.jsx**
```javascript
import { useState, useEffect } from 'react'
import Dashboard from './pages/Dashboard'
import ProfileDetail from './pages/ProfileDetail'
import ProgressForm from './pages/ProgressForm'

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
      <nav className="bg-white shadow-sm mb-6">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex gap-4">
            <button onClick={() => navigate('dashboard')}
              className={route === 'dashboard' ? 'font-bold' : ''}>
              Dashboard
            </button>
            <button onClick={() => navigate('progress')}
              className={route === 'progress' ? 'font-bold' : ''}>
              Record Progress
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4">
        {route === 'dashboard' && <Dashboard navigate={navigate} />}
        {route === 'profile' && <ProfileDetail profileId={params.id} navigate={navigate} />}
        {route === 'progress' && <ProgressForm navigate={navigate} />}
      </main>
    </div>
  )
}

export default App
```

### URL Structure
```
/#dashboard
/#profile?id=1
/#profile?id=1&start=2025-10-01&end=2025-10-20
/#progress
/#ice-usage?id=1&date=2025-10-15
```

---

## Styling Guidelines

### Tailwind Utility Classes
- Use composition for common patterns
- Avoid inline style objects
- Keep classes readable (multi-line for complex components)

**Good**:
```jsx
<div className="
  flex items-center justify-between
  bg-white rounded-lg shadow-md
  p-6 mb-4
  hover:shadow-lg transition-shadow
">
```

**Bad**:
```jsx
<div style={{ display: 'flex', padding: '24px', background: 'white' }}>
```

### Responsive Design
Use Tailwind breakpoints:
- `sm:` - 640px
- `md:` - 768px
- `lg:` - 1024px
- `xl:` - 1280px

**Example**:
```jsx
<div className="
  grid
  grid-cols-1
  md:grid-cols-2
  lg:grid-cols-3
  gap-6
">
```

### Color Palette
Use Tailwind's default colors + custom properties:
```css
:root {
  --color-ice: #93c5fd;    /* Light blue for ice theme */
  --color-gold: #fbbf24;   /* Gold for currency */
}
```

Apply in Tailwind:
```jsx
<div className="bg-[var(--color-ice)]">
```

---

## Error Handling

### Error Boundary Component

**src/components/ErrorBoundary.jsx**
```javascript
import { Component } from 'react'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="bg-white p-8 rounded-lg shadow-lg max-w-md">
            <h2 className="text-2xl font-bold text-red-600 mb-4">
              Something went wrong
            </h2>
            <p className="text-gray-600 mb-4">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Reload Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
```

### API Error Handling

Display user-friendly error messages:
```javascript
function ErrorMessage({ error }) {
  const getMessage = () => {
    if (error.status === 404) return 'Resource not found'
    if (error.status === 500) return 'Server error. Please try again later.'
    if (error.status === 0) return 'Network error. Check your connection.'
    return error.message || 'An error occurred'
  }

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <p className="text-red-800">{getMessage()}</p>
    </div>
  )
}
```

---

## Performance Optimization

### Code Splitting (Future Enhancement)
When bundle size grows, use React.lazy:
```javascript
import { lazy, Suspense } from 'react'

const ProfileDetail = lazy(() => import('./pages/ProfileDetail'))

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <ProfileDetail />
    </Suspense>
  )
}
```

### Memoization
Use React.memo for expensive list items:
```javascript
import { memo } from 'react'

const ProfileCard = memo(function ProfileCard({ profile }) {
  return (
    <Card>
      <h3>{profile.name}</h3>
      <p>{profile.team_lead}</p>
    </Card>
  )
})
```

### Debouncing
For search/filter inputs:
```javascript
// src/hooks/useDebounce.js
import { useState, useEffect } from 'react'

export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}
```

---

## Build & Deployment

### Development Build
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

Output: `dist/` directory with optimized static files

### Preview Production Build
```bash
npm run preview
```

### Build Optimizations (Vite 7)
- Automatic code splitting
- CSS minification
- Tree shaking
- Asset optimization (images, fonts)
- Source maps (optional)

**vite.config.js** (production settings):
```javascript
export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    sourcemap: false,
    minify: 'esbuild',
    target: 'es2020',
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'charts': ['recharts']
        }
      }
    }
  }
})
```

---

## HuggingFace Space Deployment

### Static Site Setup

**Dockerfile**
```dockerfile
FROM nginx:alpine

# Copy built files
COPY dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 7860

CMD ["nginx", "-g", "daemon off;"]
```

**nginx.conf**
```nginx
events {
  worker_connections 1024;
}

http {
  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  server {
    listen 7860;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # SPA fallback
    location / {
      try_files $uri $uri/ /index.html;
    }

    # API proxy (if Django backend in same Space)
    location /api {
      proxy_pass http://localhost:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }
}
```

### Space Configuration

**README.md** (HuggingFace header):
```yaml
---
title: Wall Construction Tracker
emoji: 🏰
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
---
```

### Environment Variables

**src/utils/api.js**:
```javascript
const API_BASE = import.meta.env.VITE_API_BASE || '/api'
```

**.env.production**:
```
VITE_API_BASE=https://your-api-domain.com/api
```

---

## Testing Strategy (Future Enhancement)

When tests become necessary:

### Unit Tests
- Vitest (Vite-native test runner)
- React Testing Library
- Test utilities, formatters, API client

### Integration Tests
- Test page-level components
- Mock API responses
- Test user workflows

### E2E Tests
- Playwright or Cypress
- Test critical paths (record progress, view analytics)

**Not included in minimal spec** - add when project matures.

---

## Accessibility (a11y)

### Semantic HTML
Use proper elements:
```jsx
<button> instead of <div onClick>
<nav> for navigation
<main> for main content
<header>, <footer> for sections
```

### ARIA Labels
```jsx
<button aria-label="Close modal">×</button>
<input aria-describedby="error-message" />
```

### Keyboard Navigation
- All interactive elements focusable
- Visible focus states
- Logical tab order

### Color Contrast
- WCAG AA minimum (4.5:1 for text)
- Use Tailwind's accessible color combinations

---

## Development Workflow

### 1. Start Backend (Django)
```bash
cd /path/to/django/backend
python manage.py runserver
```

### 2. Start Frontend (Vite)
```bash
cd /path/to/react/frontend
npm run dev
```

### 3. Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Vite proxies `/api` requests to backend

### 4. Make Changes
- Edit React components
- Save file
- Vite HMR updates browser instantly (no refresh needed)

---

## Code Quality Standards

### Formatting
- Consistent indentation (2 spaces)
- Trailing commas in multiline arrays/objects
- Single quotes for strings
- Semicolons optional (be consistent)

### Naming Conventions
- Components: PascalCase (`ProfileCard.jsx`)
- Hooks: camelCase with `use` prefix (`useFetch.js`)
- Utilities: camelCase (`formatNumber.js`)
- Constants: UPPER_SNAKE_CASE (`API_BASE`)

### File Organization
- One component per file
- Group related components in folders
- Keep files under 200 lines
- Extract complex logic to hooks/utils

### Comments
- Use JSDoc for functions
- Explain "why", not "what"
- Remove commented-out code

**Example**:
```javascript
/**
 * Formats a number as currency (Gold Dragons)
 * @param {number} value - The value to format
 * @returns {string} Formatted string like "1,234,567 GD"
 */
function formatCurrency(value) {
  return `${value.toLocaleString()} GD`
}
```

---

## Browser Support

### Target Browsers (Vite 7 defaults)
- Chrome 107+
- Edge 107+
- Firefox 104+
- Safari 16.0+

These align with Vite 7's "baseline-widely-available" target.

### Polyfills
None needed - modern browsers support:
- ES2020 syntax
- Fetch API
- Async/await
- CSS Grid/Flexbox
- CSS custom properties

---

## Future Enhancements (Not in Minimal Spec)

### When to Add
1. **React Router** - When hash-based routing becomes limiting
2. **React Context** - When props drilling exceeds 3 levels
3. **React Query** - When caching/invalidation becomes complex
4. **TypeScript** - When team grows or errors increase
5. **Testing** - When regression bugs appear frequently
6. **Storybook** - When design system emerges
7. **i18n** - When internationalization is required
8. **PWA** - When offline support is needed

### Don't Add Unless Needed
- Redux (useState is sufficient)
- CSS-in-JS (Tailwind is enough)
- Component libraries (build your own)
- Lodash (native JS is powerful enough)

---

## Summary

This specification defines a **minimal, production-ready React GUI** with:

✅ **5 total dependencies** (React, ReactDOM, Recharts, Vite, Tailwind)
✅ **Modern 2025 stack** (React 19.2, Vite 7, Tailwind v4)
✅ **Zero configuration** (Tailwind v4, Vite auto-discovery)
✅ **Fast builds** (5x faster with Vite 7 + Tailwind v4)
✅ **Component-based architecture** (reusable, composable)
✅ **Hash-based routing** (no external router)
✅ **Native fetch** (no HTTP libraries)
✅ **Simple state management** (useState/props)
✅ **Recharts integration** (SVG-based, responsive charts)
✅ **Tailwind styling** (utility-first, no CSS frameworks)
✅ **HuggingFace Space ready** (Docker, nginx, static build)

**Philosophy**: Start minimal, add dependencies only when complexity demands it.
