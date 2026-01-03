'use client'

import { useState, useEffect } from 'react'
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts'
import { 
  TrendingUp, Users, Target, AlertCircle, 
  MessageSquare, FileText, Zap, Globe 
} from 'lucide-react'
import { dashboardApi, feedbackApi, competitorApi } from '@/lib/api'

// Helper function to format dates consistently (avoiding hydration mismatch)
const formatDate = (dateString: string | Date): string => {
  if (!dateString) return 'N/A'
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString
  if (isNaN(date.getTime())) return 'Invalid Date'
  
  // Use consistent format: YYYY-MM-DD
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

interface DashboardProps {
  initialData?: any
}

export default function Dashboard({ initialData }: DashboardProps) {
  const [overview, setOverview] = useState(initialData)
  const [insights, setInsights] = useState<any>(null)
  const [themes, setThemes] = useState<any[]>([])
  const [competitors, setCompetitors] = useState<any[]>([])

  useEffect(() => {
    if (!overview) {
      loadOverview()
    }
    loadInsights()
    loadThemes()
    loadCompetitors()
  }, [])

  const loadOverview = async () => {
    try {
      const { data } = await dashboardApi.getOverview()
      setOverview(data)
    } catch (error) {
      console.error('Error loading overview:', error)
    }
  }

  const loadInsights = async () => {
    try {
      const { data } = await dashboardApi.getInsights()
      setInsights(data)
    } catch (error) {
      console.error('Error loading insights:', error)
    }
  }

  const loadThemes = async () => {
    try {
      const { data } = await feedbackApi.getThemes()
      setThemes(data.themes || [])
    } catch (error) {
      console.error('Error loading themes:', error)
    }
  }

  const loadCompetitors = async () => {
    try {
      const { data } = await competitorApi.list()
      setCompetitors(data.competitors || [])
    } catch (error) {
      console.error('Error loading competitors:', error)
    }
  }

  if (!overview) {
    return <div className="p-8">Loading...</div>
  }

  const classificationData = Object.entries(overview.feedback.by_classification || {}).map(
    ([name, value]) => ({ name, value })
  )

  const statusData = Object.entries(overview.recommendations.by_status || {}).map(
    ([name, value]) => ({ name, value })
  )

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8']

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Multi-Agent Intelligence System
          </h1>
          <p className="text-gray-600 mt-1">
            Real-time insights from Competitor, Market, and Social agents
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Feedback"
            value={overview.feedback.total}
            icon={<MessageSquare className="w-6 h-6" />}
            color="blue"
          />
          <StatCard
            title="Themes Identified"
            value={overview.themes.total}
            icon={<Target className="w-6 h-6" />}
            color="green"
          />
          <StatCard
            title="Recommendations"
            value={overview.recommendations.total}
            icon={<TrendingUp className="w-6 h-6" />}
            color="purple"
          />
          <StatCard
            title="Competitors"
            value={overview.competitors.total}
            icon={<Globe className="w-6 h-6" />}
            color="orange"
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ChartCard title="Feedback Classification">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={classificationData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {classificationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Recommendation Status">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={statusData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* Top Themes */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Top Impact Themes</h2>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Theme
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Impact Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Requests
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer Value
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {themes.slice(0, 10).map((theme) => (
                  <tr key={theme.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{theme.name}</div>
                      <div className="text-sm text-gray-500">{theme.description}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-semibold text-blue-600">
                        {theme.impact_score?.toFixed(2) || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {theme.request_frequency}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {theme.customer_value?.toFixed(1) || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Competitors */}
        {competitors.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Discovered Competitors</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {competitors.slice(0, 6).map((competitor) => (
                <div key={competitor.id} className="bg-white rounded-lg shadow p-4">
                  <h3 className="font-semibold text-lg mb-2">{competitor.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">{competitor.description}</p>
                  <div className="flex items-center justify-between mt-4">
                    <span className="text-xs text-gray-500">
                      Sentiment: {competitor.sentiment_score?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Insights */}
        {insights && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h2 className="text-2xl font-bold mb-4">High Impact Recommendations</h2>
              <div className="space-y-4">
                {insights.pending_recommendations?.slice(0, 5).map((rec: any) => (
                  <div key={rec.id} className="bg-white rounded-lg shadow p-4">
                    <h3 className="font-semibold mb-2">{rec.title}</h3>
                    <div className="flex items-center gap-4 text-sm">
                      <span>Impact: {rec.impact_score?.toFixed(1)}</span>
                      <span>Feasibility: {rec.feasibility_score?.toFixed(1)}</span>
                      <span>Risk: {rec.risk_score?.toFixed(1)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-bold mb-4">Recent Activity</h2>
              <div className="bg-white rounded-lg shadow p-4">
                <div className="space-y-3">
                  {overview.recent_activity?.slice(0, 5).map((activity: any, idx: number) => (
                    <div key={idx} className="border-b pb-2 last:border-0">
                      <p className="text-sm text-gray-700">{activity.content}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {activity.source} • {formatDate(activity.created_at)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

function StatCard({ title, value, icon, color }: any) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div className={`${colorClasses[color as keyof typeof colorClasses]} text-white p-3 rounded-lg`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

function ChartCard({ title, children }: any) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      {children}
    </div>
  )
}

