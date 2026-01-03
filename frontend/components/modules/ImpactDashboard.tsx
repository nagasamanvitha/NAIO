'use client'

import { useState, useEffect } from 'react'
import { TrendingUp, Target, Zap, BarChart3 } from 'lucide-react'

interface ImpactDashboardProps {
  initialData?: {
    overview?: any
    recommendations?: any[]
  }
}

export default function ImpactDashboard({ initialData }: ImpactDashboardProps = {}) {
  // Get themes from initialData - no API calls
  const initialThemes = initialData?.overview?.themes?.top_themes || []
  const [themes, setThemes] = useState<any[]>(initialThemes)
  const [weights, setWeights] = useState({
    customerValue: 0.25,
    requestFrequency: 0.20,
    strategicWeight: 0.15,
    competitivePressure: 0.15,
    recency: 0.15,
    trendVelocity: 0.10
  })
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list')

  // No API calls - data comes from initialData

  const sortedThemes = [...themes].sort((a, b) => 
    (b.impact_score || 0) - (a.impact_score || 0)
  )

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Impact Scoring Dashboard
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Transparent scoring model for every theme and feature
        </p>
      </div>

      {/* Formula Breakdown & Weights */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
          Scoring Formula Weights
        </h2>
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-700 dark:text-gray-300">Customer Value</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {(weights.customerValue * 100).toFixed(0)}%
              </span>
            </div>
            <Slider
              value={[weights.customerValue * 100]}
              onValueChange={([value]) => setWeights({ ...weights, customerValue: value / 100 })}
              max={100}
              step={1}
              className="w-full"
            />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-700 dark:text-gray-300">Request Frequency</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {(weights.requestFrequency * 100).toFixed(0)}%
              </span>
            </div>
            <Slider
              value={[weights.requestFrequency * 100]}
              onValueChange={([value]) => setWeights({ ...weights, requestFrequency: value / 100 })}
              max={100}
              step={1}
              className="w-full"
            />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-700 dark:text-gray-300">Strategic Segment Weight</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {(weights.strategicWeight * 100).toFixed(0)}%
              </span>
            </div>
            <Slider
              value={[weights.strategicWeight * 100]}
              onValueChange={([value]) => setWeights({ ...weights, strategicWeight: value / 100 })}
              max={100}
              step={1}
              className="w-full"
            />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-700 dark:text-gray-300">Competitive Pressure</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {(weights.competitivePressure * 100).toFixed(0)}%
              </span>
            </div>
            <Slider
              value={[weights.competitivePressure * 100]}
              onValueChange={([value]) => setWeights({ ...weights, competitivePressure: value / 100 })}
              max={100}
              step={1}
              className="w-full"
            />
          </div>
        </div>
      </div>

      {/* Impact vs Effort Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
              Impact vs Effort Matrix
            </h2>
            <div className="relative h-96 border-2 border-gray-300 dark:border-gray-700 rounded-lg">
              {/* Grid Lines */}
              <div className="absolute inset-0">
                <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-300 dark:bg-gray-700" />
                <div className="absolute top-1/2 left-0 right-0 h-px bg-gray-300 dark:bg-gray-700" />
              </div>
              {/* Labels */}
              <div className="absolute top-2 left-2 text-xs font-medium text-gray-500 dark:text-gray-400">
                High Impact
              </div>
              <div className="absolute top-2 right-2 text-xs font-medium text-gray-500 dark:text-gray-400">
                High Effort
              </div>
              <div className="absolute bottom-2 left-2 text-xs font-medium text-gray-500 dark:text-gray-400">
                Low Effort
              </div>
              <div className="absolute bottom-2 right-2 text-xs font-medium text-gray-500 dark:text-gray-400">
                Low Impact
              </div>
              {/* Theme Bubbles */}
              <div className="absolute inset-0 p-4">
                {sortedThemes.slice(0, 10).map((theme, idx) => {
                  const impact = (theme.impact_score || 0) / 10
                  const effort = 0.5 // Placeholder - would come from PM input
                  return (
                    <div
                      key={theme.id}
                      className="absolute cursor-move"
                      style={{
                        left: `${effort * 100}%`,
                        top: `${(1 - impact) * 100}%`,
                        transform: 'translate(-50%, -50%)'
                      }}
                    >
                      <div className="w-4 h-4 bg-blue-500 rounded-full hover:scale-150 transition-transform" />
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Quick Stats
          </h2>
          <div className="space-y-4">
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Total Themes</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {themes.length}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">High Impact (8+)</div>
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {themes.filter(t => (t.impact_score || 0) >= 8).length}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Avg Impact Score</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {themes.length > 0
                  ? (themes.reduce((sum, t) => sum + (t.impact_score || 0), 0) / themes.length).toFixed(1)
                  : '0.0'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Feature List View */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800">
        <div className="p-6 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Features & Themes
          </h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-100 dark:bg-blue-900/20' : ''}`}
            >
              <BarChart3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-100 dark:bg-blue-900/20' : ''}`}
            >
              <Target className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Feature / Theme
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  ARR Impact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Requests
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Segment Weight
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Competitive
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Pain Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Impact Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Effort
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
              {sortedThemes.map((theme) => (
                <tr key={theme.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {theme.name}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {theme.description?.substring(0, 50)}...
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    High
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {theme.request_frequency}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {(theme.strategic_segment_weight || 0.5).toFixed(1)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {(theme.competitive_pressure || 0.5).toFixed(1)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                        <div
                          className="bg-red-500 h-2 rounded-full"
                          style={{ width: `${((theme.customer_value || 0) / 10) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-900 dark:text-white">
                        {(theme.customer_value || 0).toFixed(1)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-lg font-bold text-blue-600 dark:text-blue-400">
                      {(theme.impact_score || 0).toFixed(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="number"
                      min="1"
                      max="10"
                      defaultValue="5"
                      className="w-16 px-2 py-1 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

// Simple Slider component
function Slider({ value, onValueChange, max, step, className }: any) {
  return (
    <input
      type="range"
      min="0"
      max={max}
      step={step}
      value={value[0]}
      onChange={(e) => onValueChange([parseInt(e.target.value)])}
      className={className}
    />
  )
}

