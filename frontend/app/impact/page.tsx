'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import ImpactDashboard from '@/components/modules/ImpactDashboard'
import { dashboardApi, feedbackApi } from '@/lib/api'

// Load ONLY real data from backend API (from n8n processed data) - NO MOCK DATA
// Data is cached in localStorage to persist even when backend is stopped
const IMPACT_CACHE_KEY = 'naio_impact_cache'

export default function ImpactPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCached, setIsCached] = useState(false)

  useEffect(() => {
    // First, load from cache (instant display)
    loadFromCache()
    // Then try to fetch from API (silent update in background)
    loadData(true)
    // Only refresh when backend is available (no auto-refresh if backend is down)
  }, [])

  const loadFromCache = () => {
    try {
      const cached = localStorage.getItem(IMPACT_CACHE_KEY)
      if (cached) {
        const cachedData = JSON.parse(cached)
        setData(cachedData)
        setIsCached(true)
        setLoading(false)
        console.log('✅ Loaded impact data from cache')
      }
    } catch (error) {
      console.error('Error loading from cache:', error)
    }
  }

  const saveToCache = (dataToCache: any) => {
    try {
      localStorage.setItem(IMPACT_CACHE_KEY, JSON.stringify({
        ...dataToCache,
        timestamp: new Date().toISOString()
      }))
      console.log('💾 Saved impact data to cache')
    } catch (error) {
      console.error('Error saving to cache:', error)
    }
  }

  const loadData = async (silent: boolean = false) => {
    try {
      if (!silent) setError(null)
      const [overviewRes, themesRes, recommendationsRes] = await Promise.all([
        dashboardApi.getOverview().catch(() => ({ data: null })),
        feedbackApi.getThemes(100).catch(() => ({ data: { themes: [] } })),
        dashboardApi.getRecommendations().catch(() => ({ data: { recommendations: [] } }))
      ])
      
      const overview = overviewRes.data
      const themes = themesRes.data?.themes || []
      const recommendations = recommendationsRes.data?.recommendations || []
      
      // If backend returns empty, don't overwrite cached data - keep existing data
      if ((!overview || themes.length === 0) && data) {
        console.log('⚠️ Backend returned empty - keeping cached data. Run n8n workflow to generate new data.')
        setIsCached(true) // Mark as cached since we're using old data
        return // Don't update - keep existing cached data
      }
      
      const newData = {
        overview: overview || (data?.overview || {}),
        themes: themes.length > 0 ? themes : (data?.themes || []),
        recommendations: recommendations.length > 0 ? recommendations : (data?.recommendations || [])
      }
      
      // Only update if we have new data OR if data count changed (new n8n workflow ran)
      const currentRecCount = data?.recommendations?.length || 0
      const newRecCount = recommendations.length
      
      if (newRecCount > 0 || themes.length > 0 || overview) {
        setData(newData)
        setIsCached(false)
        saveToCache(newData) // Save to cache - persists even when backend stops
        console.log('💾 Saved impact data to cache - will persist even if backend stops')
        
        if (newRecCount > currentRecCount && currentRecCount > 0) {
          console.log(`✨ Detected ${newRecCount - currentRecCount} new recommendation(s) from n8n workflow`)
        }
      }
    } catch (error) {
      console.error('❌ Error loading impact data:', error)
      // Don't clear cached data - keep showing it
      if (!silent) {
        // Only show error if we don't have cached data
        if (!data) {
          setError('Cannot connect to backend. Showing cached data if available.')
        } else {
          // We have cached data, just show a subtle notice
          setError(null)
          setIsCached(true) // Mark as using cached data
          console.log('💾 Using cached impact data - backend offline but data persists')
        }
      }
      // Keep showing cached data if available - DON'T CLEAR IT
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <MainLayout>
        <div className="p-8">Loading impact data from n8n workflows...</div>
      </MainLayout>
    )
  }

  if (error && !data) {
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

  if (!data) {
    return (
      <MainLayout>
        <div className="p-8">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">📊 No Impact Data Yet</h3>
            <p className="text-blue-700">Impact data will appear here after processing feedback from n8n workflow.</p>
            <p className="text-sm text-blue-600 mt-2">Execute your n8n workflow to see impact metrics.</p>
          </div>
        </div>
      </MainLayout>
    )
  }

  return (
    <MainLayout>
      <ImpactDashboard initialData={data} />
    </MainLayout>
  )
}
