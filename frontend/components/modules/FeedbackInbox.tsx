'use client'

import { useState, useEffect } from 'react'
import {
  Search,
  Filter,
  ChevronDown,
  MessageSquare,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  XCircle,
  Zap
} from 'lucide-react'
import { feedbackApi } from '@/lib/api'

interface FeedbackInboxProps {
  initialFeedback?: any[]
}

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

export default function FeedbackInbox({ initialFeedback = [] }: FeedbackInboxProps) {
  // Use initial feedback immediately - no API calls
  const [feedback, setFeedback] = useState<any[]>(initialFeedback)
  const [filteredFeedback, setFilteredFeedback] = useState<any[]>(initialFeedback)
  const [selectedFeedback, setSelectedFeedback] = useState<any>(null)
  const [filters, setFilters] = useState({
    source: '',
    type: '',
    sentiment: '',
    segment: '',
    arrBucket: '',
    churnRisk: '',
    quarter: '',
    year: '2025',
    startDate: '',
    endDate: ''
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [useDateRange, setUseDateRange] = useState(false)
  // NO loading state - data is always available
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadFeedbackWithFilters()
  }, [filters.quarter, filters.year, filters.startDate, filters.endDate, useDateRange])

  useEffect(() => {
    applyFilters()
  }, [feedback, filters, searchQuery])

  const loadFeedbackWithFilters = async () => {
    try {
      setLoading(true)
      const params: any = { limit: 500 }
      
      if (useDateRange && filters.startDate && filters.endDate) {
        params.start_date = filters.startDate
        params.end_date = filters.endDate
      } else if (filters.quarter && filters.year) {
        params.quarter = filters.quarter
        params.year = parseInt(filters.year)
      }
      
      if (filters.source) params.source = filters.source
      if (filters.type) params.classification = filters.type
      
      const { data } = await feedbackApi.list(params)
      setFeedback(data.feedback || [])
      setFilteredFeedback(data.feedback || [])
    } catch (error) {
      console.error('Error loading feedback:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadFeedback = async () => {
    try {
      const { data } = await feedbackApi.list({ limit: 100 })
      setFeedback(data.feedback || [])
      setFilteredFeedback(data.feedback || [])
    } catch (error) {
      console.error('Error loading feedback:', error)
    } finally {
      setLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...feedback]

    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.content?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (filters.source) {
      filtered = filtered.filter(item => item.source === filters.source)
    }

    if (filters.type) {
      filtered = filtered.filter(item => item.classification === filters.type)
    }

    if (filters.segment) {
      filtered = filtered.filter(item => item.user_segment === filters.segment)
    }

    // Client-side date filtering (backup if API filtering doesn't work)
    if (filters.quarter && filters.year && !useDateRange) {
      const quarterMap: { [key: string]: number[] } = {
        'Q1': [1, 2, 3],
        'Q2': [4, 5, 6],
        'Q3': [7, 8, 9],
        'Q4': [10, 11, 12]
      }
      const months = quarterMap[filters.quarter] || []
      const year = parseInt(filters.year)
      filtered = filtered.filter(item => {
        if (!item.created_at) return false
        const date = new Date(item.created_at)
        return date.getFullYear() === year && months.includes(date.getMonth() + 1)
      })
    }

    if (useDateRange && filters.startDate && filters.endDate) {
      filtered = filtered.filter(item => {
        if (!item.created_at) return false
        const itemDate = new Date(item.created_at)
        const startDate = new Date(filters.startDate)
        const endDate = new Date(filters.endDate)
        endDate.setHours(23, 59, 59, 999) // Include entire end date
        return itemDate >= startDate && itemDate <= endDate
      })
    }

    // Sentiment filtering
    if (filters.sentiment) {
      filtered = filtered.filter(item => {
        const score = item.sentiment_score || 0
        if (filters.sentiment === 'positive') return score > 0.3
        if (filters.sentiment === 'negative') return score < -0.3
        if (filters.sentiment === 'neutral') return score >= -0.3 && score <= 0.3
        return true
      })
    }

    setFilteredFeedback(filtered)
  }

  const getSentimentColor = (score: number) => {
    if (score > 0.3) return 'text-green-600 bg-green-50'
    if (score < -0.3) return 'text-red-600 bg-red-50'
    return 'text-yellow-600 bg-yellow-50'
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'bug':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'feature_request':
        return <Zap className="w-4 h-4 text-blue-500" />
      case 'usability_issue':
        return <AlertCircle className="w-4 h-4 text-orange-500" />
      default:
        return <MessageSquare className="w-4 h-4 text-gray-500" />
    }
  }

  const sources = Array.from(new Set(feedback.map(f => f.source))).filter(Boolean)

  return (
    <div className="flex h-full">
      {/* Left Sidebar - Filters */}
      <div className="w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 p-6 overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
          Filters
        </h2>

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search feedback..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Source Filter */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Source
          </label>
          <select
            value={filters.source}
            onChange={(e) => setFilters({ ...filters, source: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="">All Sources</option>
            {sources.map(source => (
              <option key={source} value={source}>{source}</option>
            ))}
          </select>
        </div>

        {/* Type Filter */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Feedback Type
          </label>
          <select
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="">All Types</option>
            <option value="bug">Bug</option>
            <option value="feature_request">Feature Request</option>
            <option value="usability_issue">Usability Issue</option>
            <option value="integration_request">Integration Request</option>
          </select>
        </div>

        {/* Sentiment Slider */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Sentiment
          </label>
          <select
            value={filters.sentiment}
            onChange={(e) => setFilters({ ...filters, sentiment: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="">All Sentiments</option>
            <option value="positive">Positive</option>
            <option value="neutral">Neutral</option>
            <option value="negative">Negative</option>
          </select>
        </div>

        {/* Segment Filter */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Segment
          </label>
          <select
            value={filters.segment}
            onChange={(e) => setFilters({ ...filters, segment: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="">All Segments</option>
            <option value="enterprise">Enterprise</option>
            <option value="smb">SMB</option>
            <option value="individual">Individual</option>
          </select>
        </div>

        {/* Date Range Filter Section */}
        <div className="mb-4 border-t border-gray-200 dark:border-gray-700 pt-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Filter by Date
          </label>
          
          {/* Toggle between Quarter and Date Range */}
          <div className="mb-3 flex gap-2">
            <button
              onClick={() => setUseDateRange(false)}
              className={`flex-1 px-3 py-1.5 text-xs rounded ${
                !useDateRange
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              Quarter
            </button>
            <button
              onClick={() => setUseDateRange(true)}
              className={`flex-1 px-3 py-1.5 text-xs rounded ${
                useDateRange
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              Date Range
            </button>
          </div>

          {!useDateRange ? (
            <>
              {/* Quarter Filter */}
              <div className="mb-3">
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Quarter
                </label>
                <select
                  value={filters.quarter}
                  onChange={(e) => setFilters({ ...filters, quarter: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                >
                  <option value="">All Quarters</option>
                  <option value="Q1">Q1 (Jan-Mar)</option>
                  <option value="Q2">Q2 (Apr-Jun)</option>
                  <option value="Q3">Q3 (Jul-Sep)</option>
                  <option value="Q4">Q4 (Oct-Dec)</option>
                </select>
              </div>
              
              {/* Year Filter */}
              <div className="mb-3">
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Year
                </label>
                <select
                  value={filters.year}
                  onChange={(e) => setFilters({ ...filters, year: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                >
                  <option value="2025">2025</option>
                  <option value="2024">2024</option>
                  <option value="2023">2023</option>
                </select>
              </div>
            </>
          ) : (
            <>
              {/* Start Date */}
              <div className="mb-3">
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={filters.startDate}
                  onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                />
              </div>
              
              {/* End Date */}
              <div className="mb-3">
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={filters.endDate}
                  onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                />
              </div>
            </>
          )}
        </div>

        {/* Results Count */}
        <div className="mt-6 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Showing {filteredFeedback.length} of {feedback.length} feedback items
          </div>
        </div>
      </div>

      {/* Main List View */}
      <div className="flex-1 flex">
        <div className="flex-1 overflow-y-auto">
          <div className="p-6">
            <div className="mb-6 flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Feedback Inbox
              </h1>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Export
              </button>
            </div>

            {loading ? (
              <div className="text-center py-12 text-gray-500">Loading feedback...</div>
            ) : filteredFeedback.length === 0 ? (
              <div className="text-center py-12 text-gray-500">No feedback found</div>
            ) : (
              <div className="space-y-3">
                {filteredFeedback.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setSelectedFeedback(item)}
                    className={`p-4 bg-white dark:bg-gray-900 rounded-lg border cursor-pointer transition-all ${
                      selectedFeedback?.id === item.id
                        ? 'border-blue-500 shadow-md'
                        : 'border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          {getTypeIcon(item.classification)}
                          <span className="text-sm font-medium text-gray-900 dark:text-white">
                            {item.source}
                          </span>
                          <span className="px-2 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                            {item.classification?.replace('_', ' ') || 'Unknown'}
                          </span>
                          {item.arr && (
                            <span className="px-2 py-1 text-xs rounded-full bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400">
                              ${(item.arr / 1000).toFixed(0)}k ARR
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2 mb-2">
                          {item.content}
                        </p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                          <span>{formatDate(item.created_at)}</span>
                          {item.user_segment && (
                            <span className="capitalize">{item.user_segment}</span>
                          )}
                          {item.sentiment_score !== null && (
                            <span className={`px-2 py-1 rounded ${getSentimentColor(item.sentiment_score)}`}>
                              {item.sentiment_score > 0 ? 'Positive' : item.sentiment_score < 0 ? 'Negative' : 'Neutral'}
                            </span>
                          )}
                          {item.pain_level && (
                            <span>Pain: {item.pain_level.toFixed(1)}/10</span>
                          )}
                        </div>
                      </div>
                      <div className="ml-4">
                        {item.sentiment_score !== null && (
                          <div className={`w-12 h-12 rounded-full flex items-center justify-center ${getSentimentColor(item.sentiment_score)}`}>
                            {item.sentiment_score > 0 ? (
                              <TrendingUp className="w-6 h-6" />
                            ) : item.sentiment_score < 0 ? (
                              <TrendingDown className="w-6 h-6" />
                            ) : (
                              <div className="w-2 h-2 bg-current rounded-full" />
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Detail Panel */}
        {selectedFeedback && (
          <div className="w-96 bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 p-6 overflow-y-auto">
            <div className="mb-6">
              <button
                onClick={() => setSelectedFeedback(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                ← Back
              </button>
            </div>

            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
              Feedback Details
            </h2>

            <div className="space-y-6">
              {/* Full Content */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Full Feedback
                </h3>
                <p className="text-sm text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                  {selectedFeedback.content}
                </p>
              </div>

              {/* Extracted Info */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Extracted Information
                </h3>
                <div className="space-y-3">
                  {selectedFeedback.feature && (
                    <div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">Feature</span>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {selectedFeedback.feature}
                      </p>
                    </div>
                  )}
                  {selectedFeedback.reason && (
                    <div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">Why Needed</span>
                      <p className="text-sm text-gray-900 dark:text-white">
                        {selectedFeedback.reason}
                      </p>
                    </div>
                  )}

                {/* Product Genome - UNIQUE FEATURE */}
                {selectedFeedback.genome && (
                  <div className="mt-4 p-3 bg-purple-50 dark:bg-purple-900/20 rounded border border-purple-200 dark:border-purple-800">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                      🧬 Product Genome (Unique Feature)
                    </h4>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="font-medium">Category:</span> {selectedFeedback.genome.category}
                      </div>
                      <div>
                        <span className="font-medium">Persona:</span> {selectedFeedback.genome.persona}
                      </div>
                      <div>
                        <span className="font-medium">Pain Level:</span> {selectedFeedback.genome.pain_level}/10
                      </div>
                      <div>
                        <span className="font-medium">Urgency:</span> {selectedFeedback.genome.urgency}
                      </div>
                      {selectedFeedback.genome.customer_arr && (
                        <div>
                          <span className="font-medium">Customer ARR:</span> ${(selectedFeedback.genome.customer_arr / 1000).toFixed(0)}K
                        </div>
                      )}
                      {selectedFeedback.genome.lost_deal && (
                        <div className="text-red-600 dark:text-red-400 font-medium">
                          ⚠️ Lost Deal Flag
                        </div>
                      )}
                      {selectedFeedback.genome.competitor && (
                        <div>
                          <span className="font-medium">Competitor:</span> {selectedFeedback.genome.competitor}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Lost Deal & Competitor Info - UNIQUE FEATURES */}
                {(selectedFeedback.lost_deal_flag || selectedFeedback.competitor_mentioned) && (
                  <div className="mt-4 space-y-2">
                    {selectedFeedback.lost_deal_flag && (
                      <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
                        <div className="flex items-center text-sm">
                          <span className="font-semibold text-red-600 dark:text-red-400 mr-2">⚠️ Lost Deal Alert</span>
                          <span className="text-gray-600 dark:text-gray-400 text-xs">
                            This feedback is linked to a lost deal
                          </span>
                        </div>
                      </div>
                    )}
                    {selectedFeedback.competitor_mentioned && (
                      <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded border border-orange-200 dark:border-orange-800">
                        <div className="text-sm">
                          <span className="font-semibold text-orange-600 dark:text-orange-400">🎯 Competitor Mentioned:</span>
                          <span className="ml-2 text-gray-700 dark:text-gray-300">{selectedFeedback.competitor_mentioned}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
                  {selectedFeedback.user_segment && (
                    <div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">User Segment</span>
                      <p className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                        {selectedFeedback.user_segment}
                      </p>
                    </div>
                  )}
                  {selectedFeedback.urgency && (
                    <div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">Urgency</span>
                      <p className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                        {selectedFeedback.urgency}
                      </p>
                    </div>
                  )}
                  {selectedFeedback.pain_level && (
                    <div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">Pain Score</span>
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-red-500 h-2 rounded-full"
                            style={{ width: `${(selectedFeedback.pain_level / 10) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {selectedFeedback.pain_level.toFixed(1)}/10
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="space-y-2 pt-4 border-t border-gray-200 dark:border-gray-800">
                <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Add to Theme
                </button>
                <button className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                  Mark as Addressed
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

