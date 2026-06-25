import { useQuery } from '@tanstack/react-query'

interface HealthResponse {
  status: string
  version: string
  environment: string
}

async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch('/api/health/')
  if (!res.ok) throw new Error('API unreachable')
  return res.json()
}

export default function App() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
  })

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-sm border border-gray-100 p-8 space-y-6">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold text-gray-900">
            AI Opportunity Tracker
          </h1>
          <p className="text-sm text-gray-500">
            Internships · Research · Fellowships · Scholarships
          </p>
        </div>

        <div className="border-t pt-4">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
            API Status
          </p>
          {isLoading && (
            <span className="inline-flex items-center gap-2 text-sm text-gray-500">
              <span className="h-2 w-2 rounded-full bg-yellow-400 animate-pulse" />
              Connecting…
            </span>
          )}
          {isError && (
            <span className="inline-flex items-center gap-2 text-sm text-red-600">
              <span className="h-2 w-2 rounded-full bg-red-500" />
              API unreachable — is the backend running?
            </span>
          )}
          {data && (
            <span className="inline-flex items-center gap-2 text-sm text-green-700">
              <span className="h-2 w-2 rounded-full bg-green-500" />
              {data.status} · v{data.version} · {data.environment}
            </span>
          )}
        </div>

        <p className="text-xs text-gray-400">
          Step 3 complete — dashboard coming in a later step.
        </p>
      </div>
    </div>
  )
}
