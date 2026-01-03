'use client'

import { useState } from 'react'
import { Target, TrendingUp, AlertTriangle, DollarSign, Users, Globe, Calendar, TrendingDown, CheckCircle, XCircle, Zap } from 'lucide-react'
import { mockCompetitors } from '@/lib/mockData'

export default function CompetitorRadar() {
  const [selectedCompetitor, setSelectedCompetitor] = useState<any>(null)
  const [viewMode, setViewMode] = useState<'overview' | 'detailed'>('overview')

  const getPressureColor = (pressure: string) => {
    switch (pressure) {
      case 'high': return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border-red-300 dark:border-red-700'
      case 'medium': return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 border-yellow-300 dark:border-yellow-700'
      case 'low': return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border-green-300 dark:border-green-700'
      default: return 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
    }
  }

  const getGapColor = (gap: string) => {
    switch (gap) {
      case 'critical': return 'text-red-600 dark:text-red-400'
      case 'advantage': return 'text-green-600 dark:text-green-400'
      default: return 'text-gray-600 dark:text-gray-400'
    }
  }

  const totalArrLost = mockCompetitors.reduce((sum, c) => sum + c.total_arr_lost, 0)
  const totalLostDeals = mockCompetitors.reduce((sum, c) => sum + c.lost_deals_attributed, 0)

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          🎯 Competitor Radar Intelligence
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Real-time competitive intelligence extracted from customer feedback and market analysis
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Total Competitors</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{mockCompetitors.length}</div>
            </div>
            <Target className="w-8 h-8 text-blue-500 opacity-50" />
          </div>
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Lost Deals</div>
              <div className="text-2xl font-bold text-red-600 dark:text-red-400">{totalLostDeals}</div>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500 opacity-50" />
          </div>
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400">ARR at Risk</div>
              <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                ${(totalArrLost / 1000).toFixed(0)}K
              </div>
            </div>
            <DollarSign className="w-8 h-8 text-orange-500 opacity-50" />
          </div>
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Avg Win Rate</div>
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {(mockCompetitors.reduce((sum, c) => sum + c.win_rate_against, 0) / mockCompetitors.length * 100).toFixed(0)}%
              </div>
            </div>
            <TrendingUp className="w-8 h-8 text-green-500 opacity-50" />
          </div>
        </div>
      </div>

      {/* Competitor Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {mockCompetitors.map((competitor) => (
          <div
            key={competitor.id}
            onClick={() => setSelectedCompetitor(competitor)}
            className={`p-5 bg-white dark:bg-gray-900 rounded-lg border-2 cursor-pointer transition-all hover:shadow-lg ${
              selectedCompetitor?.id === competitor.id
                ? 'border-blue-500 shadow-lg'
                : 'border-gray-200 dark:border-gray-800 hover:border-blue-300'
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h3 className="font-bold text-lg text-gray-900 dark:text-white mb-1">
                  {competitor.name}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                  {competitor.company_type}
                </p>
              </div>
              <span className={`text-xs px-2 py-1 rounded border ${getPressureColor(competitor.competitive_pressure)}`}>
                {competitor.competitive_pressure} pressure
              </span>
            </div>

            <div className="space-y-2 mb-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Lost Deals:</span>
                <span className="font-semibold text-red-600 dark:text-red-400">
                  {competitor.lost_deals_attributed}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">ARR Lost:</span>
                <span className="font-semibold text-orange-600 dark:text-orange-400">
                  ${(competitor.total_arr_lost / 1000).toFixed(0)}K
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Win Rate:</span>
                <span className={`font-semibold ${competitor.win_rate_against > 0.5 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {(competitor.win_rate_against * 100).toFixed(0)}%
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Mentioned:</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {competitor.mentioned_in_feedback}x
                </span>
              </div>
            </div>

            <div className="pt-3 border-t border-gray-200 dark:border-gray-800">
              <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                <Globe className="w-3 h-3 mr-1" />
                <span>{competitor.website}</span>
              </div>
              <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mt-1">
                <Users className="w-3 h-3 mr-1" />
                <span>{competitor.employees} employees</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Detailed Competitor View */}
      {selectedCompetitor && (
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                {selectedCompetitor.name}
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {selectedCompetitor.company_type} • Founded {selectedCompetitor.founded} • {selectedCompetitor.funding}
              </p>
            </div>
            <button
              onClick={() => setSelectedCompetitor(null)}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              ✕
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Key Metrics */}
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Lost Deals</div>
                  <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {selectedCompetitor.lost_deals_attributed}
                  </div>
                </div>
                <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">ARR Lost</div>
                  <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                    ${(selectedCompetitor.total_arr_lost / 1000).toFixed(0)}K
                  </div>
                </div>
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Win Rate</div>
                  <div className={`text-2xl font-bold ${selectedCompetitor.win_rate_against > 0.5 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                    {(selectedCompetitor.win_rate_against * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Mentions</div>
                  <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                    {selectedCompetitor.mentioned_in_feedback}
                  </div>
                </div>
              </div>
            </div>

            {/* Company Info */}
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Company Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Website:</span>
                    <span className="text-gray-900 dark:text-white">{selectedCompetitor.website}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Employees:</span>
                    <span className="text-gray-900 dark:text-white">{selectedCompetitor.employees}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Funding:</span>
                    <span className="text-gray-900 dark:text-white">{selectedCompetitor.funding}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Market Position:</span>
                    <span className="text-gray-900 dark:text-white">{selectedCompetitor.market_position}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                <TrendingUp className="w-4 h-4 mr-2 text-green-500" />
                Strengths
              </h3>
              <ul className="space-y-2">
                {selectedCompetitor.strengths.map((strength: string, i: number) => (
                  <li key={i} className="flex items-start text-sm text-gray-600 dark:text-gray-400">
                    <CheckCircle className="w-4 h-4 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
                    <span>{strength}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                <AlertTriangle className="w-4 h-4 mr-2 text-red-500" />
                Weaknesses
              </h3>
              <ul className="space-y-2">
                {selectedCompetitor.weaknesses.map((weakness: string, i: number) => (
                  <li key={i} className="flex items-start text-sm text-gray-600 dark:text-gray-400">
                    <XCircle className="w-4 h-4 mr-2 text-red-500 flex-shrink-0 mt-0.5" />
                    <span>{weakness}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Feature Comparison */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Feature Comparison</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-4 py-2 text-left text-gray-700 dark:text-gray-300">Feature</th>
                    <th className="px-4 py-2 text-center text-gray-700 dark:text-gray-300">Them</th>
                    <th className="px-4 py-2 text-center text-gray-700 dark:text-gray-300">Us</th>
                    <th className="px-4 py-2 text-center text-gray-700 dark:text-gray-300">Gap</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
                  {Object.entries(selectedCompetitor.feature_comparison).map(([feature, data]: [string, any]) => (
                    <tr key={feature} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                      <td className="px-4 py-3 font-medium text-gray-900 dark:text-white capitalize">
                        {feature.replace('_', ' ')}
                      </td>
                      <td className="px-4 py-3 text-center">
                        {data.them ? (
                          <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                        ) : (
                          <XCircle className="w-5 h-5 text-gray-400 mx-auto" />
                        )}
                      </td>
                      <td className="px-4 py-3 text-center">
                        {data.us ? (
                          <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                        ) : (
                          <XCircle className="w-5 h-5 text-gray-400 mx-auto" />
                        )}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`font-medium ${getGapColor(data.gap)}`}>
                          {data.gap === 'critical' && '⚠️ Critical Gap'}
                          {data.gap === 'advantage' && '✅ Our Advantage'}
                          {data.gap === 'neutral' && '➖ Neutral'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Opportunities & Threats */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center">
                <Target className="w-4 h-4 mr-2 text-blue-500" />
                Opportunities
              </h3>
              <p className="text-sm text-gray-700 dark:text-gray-300">{selectedCompetitor.opportunities}</p>
            </div>
            <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center">
                <AlertTriangle className="w-4 h-4 mr-2 text-orange-500" />
                Threats
              </h3>
              <p className="text-sm text-gray-700 dark:text-gray-300">{selectedCompetitor.threats}</p>
            </div>
          </div>

          {/* Market Gaps */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Market Gaps</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
              {selectedCompetitor.market_gaps}
            </p>
          </div>

          {/* Customer Quotes */}
          {selectedCompetitor.customer_quotes && selectedCompetitor.customer_quotes.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Customer Quotes</h3>
              <div className="space-y-2">
                {selectedCompetitor.customer_quotes.map((quote: string, i: number) => (
                  <div key={i} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border-l-4 border-blue-500">
                    <p className="text-sm text-gray-700 dark:text-gray-300 italic">"{quote}"</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Pricing */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Pricing</h3>
            <div className="grid grid-cols-3 gap-4">
              {Object.entries(selectedCompetitor.pricing).map(([tier, price]: [string, any]) => (
                <div key={tier} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg text-center">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 capitalize">{tier}</div>
                  <div className="font-semibold text-gray-900 dark:text-white">{price}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent News */}
          {selectedCompetitor.recent_news && (
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Recent News</h3>
              <ul className="space-y-2">
                {selectedCompetitor.recent_news.map((news: string, i: number) => (
                  <li key={i} className="flex items-start text-sm text-gray-600 dark:text-gray-400">
                    <Zap className="w-4 h-4 mr-2 text-blue-500 flex-shrink-0 mt-0.5" />
                    <span>{news}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
