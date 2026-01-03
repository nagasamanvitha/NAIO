'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import FeaturesList from '@/components/modules/FeaturesList'
import { dashboardApi } from '@/lib/api'

// Load ONLY real recommendations from backend API (from n8n processed data) - NO MOCK DATA
// Data is cached in localStorage to persist even when backend is stopped
const RECOMMENDATIONS_CACHE_KEY = 'naio_recommendations_cache'

export default function FeaturesPage() {
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCached, setIsCached] = useState(false)
  const [quarter, setQuarter] = useState<string>('')
  const [year, setYear] = useState<string>('2025')

  useEffect(() => {
    // First, load from cache (instant display)
    loadFromCache()
    // Then try to fetch from API (silent update in background)
    loadRecommendations(true)
    // Only refresh when backend is available (no auto-refresh if backend is down)
  }, [quarter, year])

  const loadFromCache = () => {
    try {
      const cached = localStorage.getItem(RECOMMENDATIONS_CACHE_KEY)
      if (cached) {
        const cachedData = JSON.parse(cached)
        setRecommendations(cachedData.recommendations || [])
        setIsCached(true)
        setLoading(false)
        console.log('✅ Loaded recommendations from cache:', cachedData.recommendations?.length || 0, 'recommendations')
      }
    } catch (error) {
      console.error('Error loading from cache:', error)
    }
  }

  const saveToCache = (recs: any[]) => {
    try {
      localStorage.setItem(RECOMMENDATIONS_CACHE_KEY, JSON.stringify({
        recommendations: recs,
        timestamp: new Date().toISOString()
      }))
      console.log('💾 Saved recommendations to cache:', recs.length, 'recommendations')
    } catch (error) {
      console.error('Error saving to cache:', error)
    }
  }

  const loadRecommendations = async (silent: boolean = false) => {
    try {
      if (!silent) setError(null)
      const params: any = {}
      if (quarter && year) {
        params.quarter = quarter
        params.year = parseInt(year)
      }
      const response = await dashboardApi.getRecommendations(undefined, params.quarter, params.year)
      console.log('✅ API Response:', response)
      console.log('✅ Response data:', response.data)
      console.log('✅ Recommendations array:', response.data?.recommendations)
      console.log('✅ Recommendations count:', response.data?.recommendations?.length || 0)
      
      const recs = response.data?.recommendations || []
      console.log('✅ Setting recommendations:', recs.length, 'items')
      setRecommendations(recs)
      setIsCached(false)
      saveToCache(recs) // Save to cache for offline viewing
      
      if (recs.length > 0) {
        console.log('✅ First recommendation:', recs[0])
      }
    } catch (error) {
      console.error('❌ Error loading recommendations:', error)
      if (!silent) {
        // Only show error if we don't have cached data
        if (recommendations.length === 0) {
          setError('Cannot connect to backend. Showing cached data if available.')
        } else {
          // We have cached data, just show a subtle notice
          setError(null)
        }
      }
      // Keep showing cached data if available
    } finally {
      setLoading(false)
    }
  }

  if (error && recommendations.length === 0) {
    return (
      <MainLayout>
        <div className="p-8">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-yellow-800 mb-2">⚠️ Connection Error</h3>
            <p className="text-yellow-700">{error}</p>
            <p className="text-sm text-yellow-600 mt-2">Data will appear here once you run the n8n workflow and backend is available.</p>
          </div>
        </div>
      </MainLayout>
    )
  }

  // Recommendations are generated automatically when themes are created via n8n workflow
  // No manual generation needed - the flow is: Feedback → Themes → Recommendations (all automatic)

  if (recommendations.length === 0 && !loading) {
    return (
      <MainLayout>
        <div className="p-8">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                    <h3 className="text-xl font-semibold text-blue-800 mb-2">🚀 No Recommendations Yet</h3>
                    <p className="text-blue-700 mb-4">Recommendations are generated automatically when you run the n8n workflow.</p>
                    <p className="text-sm text-blue-600 mb-2">The flow is: <strong>Feedback → Themes → Recommendations</strong></p>
                    <p className="text-sm text-blue-600">When themes are created, recommendations are automatically generated with:</p>
                    <ul className="text-sm text-blue-600 text-left max-w-md mx-auto mt-2 space-y-1">
                      <li>• ARR values, lost deals, competitor info</li>
                      <li>• Detailed persona agent debates</li>
                      <li>• Team consensus and prioritization</li>
                      <li>• Customer quotes</li>
                    </ul>
                    <p className="text-sm text-blue-500 mt-4">Please run your n8n workflow to process feedback and generate recommendations automatically.</p>
                  </div>
        </div>
      </MainLayout>
    )
  }

          return (
            <MainLayout>
              <div className="flex items-center justify-between p-4 bg-white border-b border-gray-200">
                <h1 className="text-xl font-semibold text-gray-900">Feature Recommendations</h1>
                <div className="flex items-center gap-3">
                  {/* Quarter Filter */}
                  <select
                    value={quarter}
                    onChange={(e) => setQuarter(e.target.value)}
                    className="px-3 py-2 text-sm border border-gray-300 rounded-lg bg-white text-gray-900"
                  >
                    <option value="">All Quarters</option>
                    <option value="Q1">Q1 (Jan-Mar)</option>
                    <option value="Q2">Q2 (Apr-Jun)</option>
                    <option value="Q3">Q3 (Jul-Sep)</option>
                    <option value="Q4">Q4 (Oct-Dec)</option>
                  </select>
                  {/* Year Filter */}
                  <select
                    value={year}
                    onChange={(e) => setYear(e.target.value)}
                    className="px-3 py-2 text-sm border border-gray-300 rounded-lg bg-white text-gray-900"
                  >
                    <option value="2025">2025</option>
                    <option value="2024">2024</option>
                    <option value="2023">2023</option>
                  </select>
                </div>
              </div>
              <div className="p-6">
                <FeaturesList initialRecommendations={recommendations} />
              </div>
            </MainLayout>
          )
        }
