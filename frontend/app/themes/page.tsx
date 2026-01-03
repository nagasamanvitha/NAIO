'use client'

import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import ThemesExplorer from '@/components/modules/ThemesExplorer'
import { feedbackApi } from '@/lib/api'

// Load ONLY real themes from backend API (from n8n processed data) - NO MOCK DATA
// Data is cached in localStorage to persist even when backend is stopped
const THEMES_CACHE_KEY = 'naio_themes_cache'

export default function ThemesPage() {
  const [themes, setThemes] = useState<{themes: any[], clusters: any[], clustered: boolean}>({themes: [], clusters: [], clustered: false})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCached, setIsCached] = useState(false)
  const [newThemesCount, setNewThemesCount] = useState(0)
  const [lastThemeCount, setLastThemeCount] = useState(0)
  const [quarter, setQuarter] = useState<string>('')
  const [year, setYear] = useState<string>('2025')

  useEffect(() => {
    // First, load from cache (instant display) - data persists even when backend stops
    loadFromCache()
    // Then try to fetch from API ONCE on mount (only if backend is available)
    // Don't auto-refresh - data persists until new n8n workflow runs
    loadThemes(true)
    
    // Optional: Check for updates every 60 seconds (only if backend is available)
    // This allows new data from n8n to appear without manual refresh
    const refreshInterval = setInterval(() => {
      // Only try to refresh if we have cached data (backend was available before)
      // Use a function to get current state
      loadThemes(true) // Silent refresh - only updates if new data available
    }, 60000) // Check every 60 seconds (less frequent to preserve data)
    
    // Cleanup interval on unmount
    return () => clearInterval(refreshInterval)
  }, [quarter, year])

  const loadFromCache = () => {
    try {
      const cached = localStorage.getItem(THEMES_CACHE_KEY)
      if (cached) {
        const cachedData = JSON.parse(cached)
        // Handle both old format (array) and new format (object with themes/clusters)
        if (Array.isArray(cachedData.themes)) {
          setThemes({
            themes: cachedData.themes || [],
            clusters: cachedData.clusters || [],
            clustered: cachedData.clustered || false
          })
        } else if (Array.isArray(cachedData)) {
          // Old format - just array of themes
          setThemes({ themes: cachedData, clusters: [], clustered: false })
        } else {
          setThemes({ themes: [], clusters: [], clustered: false })
        }
        setIsCached(true)
        setLoading(false)
        console.log('✅ Loaded themes from cache:', cachedData.themes?.length || cachedData.length || 0, 'themes')
      }
    } catch (error) {
      console.error('Error loading from cache:', error)
    }
  }

  const saveToCache = (data: {themes: any[], clusters: any[], clustered: boolean}) => {
    try {
      localStorage.setItem(THEMES_CACHE_KEY, JSON.stringify({
        themes: data.themes,
        clusters: data.clusters,
        clustered: data.clustered,
        timestamp: new Date().toISOString()
      }))
      console.log('💾 Saved themes to cache:', data.themes.length, 'themes', data.clusters.length, 'clusters')
    } catch (error) {
      console.error('Error saving to cache:', error)
    }
  }

  const loadThemes = async (silent: boolean = false) => {
    try {
      if (!silent) setError(null)
      const yearNum = year ? parseInt(year) : undefined
      const { data } = await feedbackApi.getThemes(100, quarter || undefined, yearNum) // Request up to 100 themes
      let themesList = data.themes || []
      let clustersList = data.clusters || []
      
      // If backend returns empty, don't overwrite cached data - keep existing themes
      if (themesList.length === 0 && themes.themes.length > 0) {
        console.log('⚠️ Backend returned empty - keeping cached themes. Run n8n workflow to generate new themes.')
        setIsCached(true) // Mark as cached since we're using old data
        return // Don't update - keep existing cached data
      }
      
      // Deduplicate themes by ID (prevent duplicates from backend)
      const seenThemeIds = new Set<number>()
      themesList = themesList.filter((theme: any) => {
        if (!theme.id) return false
        if (seenThemeIds.has(theme.id)) {
          console.warn('⚠️ Duplicate theme detected and removed:', theme.id, theme.name)
          return false
        }
        seenThemeIds.add(theme.id)
        return true
      })
      
      // Deduplicate themes in clusters
      clustersList = clustersList.map((cluster: any) => {
        if (!cluster.themes) return cluster
        const seenIds = new Set<number>()
        cluster.themes = cluster.themes.filter((theme: any) => {
          if (!theme.id) return false
          if (seenIds.has(theme.id)) {
            console.warn('⚠️ Duplicate theme in cluster detected and removed:', theme.id, theme.name)
            return false
          }
          seenIds.add(theme.id)
          return true
        })
        return cluster
      })
      
      // Only update if we have new data OR if theme count changed (new n8n workflow ran)
      const currentThemeCount = themes.themes.length
      const newThemeCount = themesList.length
      
      // Log to verify data source and check for ARR/lost deals
      if (themesList.length > 0) {
        console.log('✅ Using REAL themes from n8n/backend:', themesList.length, 'themes (deduplicated)')
        if (clustersList.length > 0) {
          console.log('📦 Themes grouped into', clustersList.length, 'clusters')
        }
        
        // Only show sample if this is new data
        if (newThemeCount !== currentThemeCount || currentThemeCount === 0) {
          const sampleTheme = themesList[0]
          console.log('Sample theme:', sampleTheme)
          console.log('Sample theme ARR:', {
            avg_arr: sampleTheme.avg_arr,
            total_arr: sampleTheme.total_arr,
            lost_deal_count: sampleTheme.lost_deal_count,
            lost_deal_arr: sampleTheme.lost_deal_arr,
            competitor_mentions: sampleTheme.competitor_mentions,
            has_lost_deals: sampleTheme.has_lost_deals
          })
        }
      } else {
        console.log('⚠️ Backend returned empty array - keeping cached themes. Execute n8n workflow to see new themes.')
        // Don't overwrite - keep cached data
        return
      }
      
      // Check if new themes were added (new n8n workflow ran)
      if (currentThemeCount > 0 && newThemeCount > currentThemeCount) {
        const newCount = newThemeCount - currentThemeCount
        setNewThemesCount(newCount)
        console.log(`✨ Detected ${newCount} new theme(s) from n8n workflow - updating display`)
        // Auto-hide notification after 10 seconds
        setTimeout(() => setNewThemesCount(0), 10000)
      }
      
      setLastThemeCount(newThemeCount)
      
      // Store both themes and clusters - PERSISTENT: saved to localStorage
      setThemes({ themes: themesList, clusters: clustersList, clustered: data.clustered || false })
      setIsCached(false)
      saveToCache({ themes: themesList, clusters: clustersList, clustered: data.clustered || false }) // Save to cache - persists even when backend stops
      console.log('💾 Themes saved to cache - will persist even if backend stops')
    } catch (error) {
      console.error('❌ API Error - Backend unavailable:', error)
      // Don't clear cached data - keep showing it
      if (!silent) {
        // Only show error if we don't have cached data
        if (themes.themes.length === 0) {
          setError('Cannot connect to backend. Showing cached data if available.')
        } else {
          // We have cached data, just show a subtle notice
          setError(null)
          setIsCached(true) // Mark as using cached data
          console.log('💾 Using cached themes - backend offline but data persists')
        }
      }
      // Keep showing cached data if available - DON'T CLEAR IT
    } finally {
      setLoading(false)
    }
  }

  if (error && themes.themes.length === 0) {
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

  if (themes.themes.length === 0 && !loading) {
    return (
      <MainLayout>
        <div className="p-8">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">📊 No Themes Yet</h3>
            <p className="text-blue-700">Themes will appear here after processing feedback from n8n workflow.</p>
            <p className="text-sm text-blue-600 mt-2">Execute your n8n workflow to generate themes.</p>
          </div>
        </div>
      </MainLayout>
    )
  }

  return (
    <MainLayout>
      <div className="flex items-center justify-between p-4 bg-white border-b border-gray-200">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-semibold text-gray-900">Themes</h1>
          {themes.themes.length > 0 && (
            <span className="text-sm text-gray-500">
              {themes.themes.length} theme{themes.themes.length !== 1 ? 's' : ''} 
              {themes.clusters.length > 0 && ` • ${themes.clusters.length} cluster${themes.clusters.length !== 1 ? 's' : ''}`}
            </span>
          )}
        </div>
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
          <button
            onClick={() => loadThemes(false)}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>
      {newThemesCount > 0 && (
        <div className="p-4 bg-green-50 border-b border-green-200 animate-pulse">
          <p className="text-sm text-green-700 font-medium">
            ✨ {newThemesCount} new theme{newThemesCount > 1 ? 's' : ''} detected! Themes updated automatically.
          </p>
        </div>
      )}
      <ThemesExplorer initialThemes={themes.themes} initialClusters={themes.clusters} loading={loading && !isCached} />
    </MainLayout>
  )
}
