'use client'

import { useState, useEffect } from 'react'
import { Layers, TrendingUp, TrendingDown, Minus, Users, DollarSign, Target, ArrowRight } from 'lucide-react'

interface ThemesExplorerProps {
  themes?: any[]
  initialThemes?: any[]
  initialClusters?: any[]
  loading?: boolean
}

export default function ThemesExplorer({ themes: propThemes, initialThemes, initialClusters, loading: initialLoading }: ThemesExplorerProps = {}) {
  // Use themes from props (either 'themes' or 'initialThemes')
  const themesFromProps = initialThemes || propThemes || []
  const [themes, setThemes] = useState<any[]>(themesFromProps)
  const [clusters, setClusters] = useState<any[]>(initialClusters || [])
  
  // Update themes when props change
  useEffect(() => {
    const newThemes = initialThemes || propThemes || []
    if (newThemes.length > 0 || themes.length === 0) {
      setThemes(newThemes)
    }
    if (initialClusters) {
      setClusters(initialClusters)
    }
  }, [initialThemes, propThemes, initialClusters])
  // NO loading state - data is always available
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState<'bubble' | 'table' | 'trend'>('table')
  const [selectedTheme, setSelectedTheme] = useState<any>(null)

  const getTrendIcon = (velocity: number) => {
    if (velocity > 0.5) return <TrendingUp className="w-4 h-4 text-green-500" />
    if (velocity < -0.5) return <TrendingDown className="w-4 h-4 text-red-500" />
    return <Minus className="w-4 h-4 text-gray-500" />
  }

  // Theme Card Component
  const ThemeCard = ({ theme, onSelect }: { theme: any, onSelect: (theme: any) => void }) => (
    <div
      onClick={() => onSelect(theme)}
      className="p-6 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 hover:border-blue-500 cursor-pointer transition-all"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
            {typeof theme.name === 'string' ? theme.name : (theme.name?.toString() || 'Unnamed Theme')}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
            {typeof theme.description === 'string' ? theme.description : (theme.description?.toString() || '')}
          </p>
          {/* Unique Features: ARR Impact, Lost Deals, Competitors */}
          <div className="mt-2 flex flex-wrap gap-2">
            {theme.avg_arr > 0 ? (
              <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded">
                💰 ${(theme.avg_arr / 1000).toFixed(0)}K avg ARR
              </span>
            ) : (
              <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded">
                💰 Calculating ARR...
              </span>
            )}
            {theme.lost_deal_arr > 0 && (
              <span className="text-xs px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded">
                ⚠️ ${(theme.lost_deal_arr / 1000).toFixed(0)}K lost ARR
              </span>
            )}
            {theme.lost_deal_count > 0 && (
              <span className="text-xs px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 rounded">
                📉 {theme.lost_deal_count} lost deal{theme.lost_deal_count > 1 ? 's' : ''}
              </span>
            )}
            {theme.competitor_mentions && theme.competitor_mentions.length > 0 && (
              <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded">
                🎯 {theme.competitor_mentions.slice(0, 2).map((c: any) => {
                  if (typeof c === 'string') return c
                  if (c && typeof c === 'object') return c.name || c.toString() || String(c)
                  return String(c)
                }).join(', ')}
                {theme.competitor_mentions.length > 2 ? '...' : ''}
              </span>
            )}
          </div>
        </div>
        <Layers className="w-5 h-5 text-blue-500 flex-shrink-0 ml-2" />
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Volume</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {theme.request_frequency || theme.feedback_count || 0} similar request{theme.request_frequency !== 1 ? 's' : ''} grouped
          </span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400 flex items-center gap-1">
            <DollarSign className="w-3 h-3" /> Total ARR
          </span>
          <span className={`font-medium ${theme.total_arr > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-400'}`}>
            {theme.total_arr > 0 ? `$${(theme.total_arr / 1000).toFixed(0)}K` : theme.avg_arr > 0 ? `$${(theme.avg_arr / 1000).toFixed(0)}K avg` : 'N/A'}
          </span>
        </div>
        {theme.avg_arr > 0 && theme.total_arr > 0 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <DollarSign className="w-3 h-3" /> Avg ARR
            </span>
            <span className="font-medium text-green-600 dark:text-green-400">
              ${(theme.avg_arr / 1000).toFixed(0)}K
            </span>
          </div>
        )}

        {(theme.lost_deal_count > 0 || theme.competitor_mentions?.length > 0) && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500 dark:text-gray-400">Lost Deals</span>
            <span className="font-medium text-red-600 dark:text-red-400">
              {theme.lost_deal_count > 0 ? `${theme.lost_deal_count} (${theme.lost_deal_arr > 0 ? `$${(theme.lost_deal_arr / 1000).toFixed(0)}K ARR` : 'No ARR data'})` : 'Competitor pressure'}
            </span>
          </div>
        )}

        {theme.competitor_mentions && theme.competitor_mentions.length > 0 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500 dark:text-gray-400">Competitors</span>
            <span className="font-medium text-blue-600 dark:text-blue-400 text-xs">
              {theme.competitor_mentions.slice(0, 2).map((c: any) => {
                if (typeof c === 'string') return c
                if (c && typeof c === 'object') return c.name || String(c)
                return String(c)
              }).join(', ')}
              {theme.competitor_mentions.length > 2 ? '...' : ''}
            </span>
          </div>
        )}

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Pain Score</span>
          <div className="flex items-center space-x-2">
            <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-red-500 h-2 rounded-full"
                style={{ width: `${((theme.pain_score || theme.customer_value || 0) / 10) * 100}%` }}
              />
            </div>
            <span className="font-medium text-gray-900 dark:text-white">
              {(theme.pain_score || theme.customer_value || 0).toFixed(1)}/10
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Impact Score</span>
          <span className="font-bold text-blue-600 dark:text-blue-400">
            {(theme.impact_score || 0).toFixed(1)}
          </span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Trend</span>
          <div className="flex items-center space-x-1">
            {getTrendIcon(theme.trend_velocity || 0)}
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {theme.trend || (theme.trend_velocity > 0 ? 'Growing' : theme.trend_velocity < 0 ? 'Declining' : 'Stable')}
            </span>
          </div>
        </div>
      </div>

      <button className="mt-4 w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
        <span className="text-sm font-medium">Open Theme</span>
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  )

  // Ensure themes is always an array and deduplicate by ID
  const safeThemes = (themes || []).filter((theme: any, index: number, self: any[]) => {
    if (!theme || !theme.id) return false
    return index === self.findIndex((t: any) => t.id === theme.id)
  })
  
  // Debug log - check for ARR and lost deals data
  console.log('ThemesExplorer - themes count:', safeThemes.length)
  if (safeThemes.length > 0) {
    const firstTheme = safeThemes[0]
    console.log('ThemesExplorer - First theme:', firstTheme)
    console.log('ThemesExplorer - First theme ARR data:', {
      avg_arr: firstTheme.avg_arr,
      total_arr: firstTheme.total_arr,
      lost_deal_count: firstTheme.lost_deal_count,
      lost_deal_arr: firstTheme.lost_deal_arr,
      competitor_mentions: firstTheme.competitor_mentions,
      has_lost_deals: firstTheme.has_lost_deals
    })
  }

  // Only show loading if we truly have no data
  if (loading && safeThemes.length === 0) {
    return (
      <div className="p-6">
        <div className="text-center py-12 text-gray-500">Loading themes...</div>
      </div>
    )
  }
  
  // Show message if no themes
  if (!loading && safeThemes.length === 0) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400 mb-2">No themes found</p>
          <p className="text-sm text-gray-400 dark:text-gray-500">
            Themes will appear here after processing feedback from n8n
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full">
      <div className="overflow-y-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Themes & Clusters
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {safeThemes.length} themes identified from feedback clusters
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('bubble')}
              className={`px-3 py-2 rounded-lg text-sm ${
                viewMode === 'bubble'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
              }`}
            >
              Bubble Map
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-2 rounded-lg text-sm ${
                viewMode === 'table'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
              }`}
            >
              Table
            </button>
            <button
              onClick={() => setViewMode('trend')}
              className={`px-3 py-2 rounded-lg text-sm ${
                viewMode === 'trend'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
              }`}
            >
              Trends
            </button>
          </div>
        </div>

        {viewMode === 'table' && (() => {
          // Track all rendered theme IDs to prevent duplicates
          const renderedThemeIds = new Set<number>()
          
          return (
            <div className="space-y-6">
              {/* Display clusters with grouped themes */}
              {clusters.length > 0 && clusters.map((cluster, clusterIdx) => {
                // Filter out themes that have already been rendered
                const uniqueClusterThemes = (cluster.themes || []).filter((theme: any) => {
                  if (!theme || !theme.id) return false
                  if (renderedThemeIds.has(theme.id)) {
                    console.warn('⚠️ Duplicate theme in cluster, skipping:', theme.id, theme.name)
                    return false
                  }
                  renderedThemeIds.add(theme.id)
                  return true
                })
                
                if (uniqueClusterThemes.length === 0) return null
                
                return (
                  <div key={`cluster-${clusterIdx}`} className="space-y-4">
                    {/* Cluster Header */}
                    <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded font-medium">
                              Major Cluster
                            </span>
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {uniqueClusterThemes.length} themes
                            </span>
                          </div>
                          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-1">
                            {cluster.cluster_name}
                          </h2>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {cluster.cluster_description}
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    {/* Individual Themes in Cluster */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 ml-4">
                      {uniqueClusterThemes.map((theme: any) => (
                        <ThemeCard key={theme.id} theme={theme} onSelect={setSelectedTheme} />
                      ))}
                    </div>
                  </div>
                )
              })}
              
              {/* Display themes not in clusters (single themes) */}
              {(() => {
                // Get all theme IDs from clusters (already rendered)
                const clusteredThemeIds = new Set(
                  clusters.flatMap((c: any) => (c.themes || []).map((t: any) => t.id).filter((id: any) => id))
                )
                
                // Filter themes that are not in clusters AND not already rendered
                const unclusteredThemes = safeThemes.filter((t: any) => {
                  if (!t || !t.id) return false
                  if (clusteredThemeIds.has(t.id) || renderedThemeIds.has(t.id)) {
                    return false
                  }
                  renderedThemeIds.add(t.id)
                  return true
                })
                
                return unclusteredThemes.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {unclusteredThemes.map((theme) => (
                      <ThemeCard key={theme.id} theme={theme} onSelect={setSelectedTheme} />
                    ))}
                  </div>
                ) : null
              })()}
              
              {/* Fallback: if no clusters, show all themes normally */}
              {clusters.length === 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {safeThemes.map((theme) => {
                    if (!theme || !theme.id) return null
                    if (renderedThemeIds.has(theme.id)) {
                      console.warn('⚠️ Duplicate theme in fallback, skipping:', theme.id, theme.name)
                      return null
                    }
                    renderedThemeIds.add(theme.id)
                    return (
                      <ThemeCard key={theme.id} theme={theme} onSelect={setSelectedTheme} />
                    )
                  })}
                </div>
              )}
            </div>
          )
        })()}
        
        {/* Old theme display - removed */}
        {false && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {safeThemes.map((theme) => (
              <div
                key={theme.id}
                onClick={() => setSelectedTheme(theme)}
                className="p-6 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 hover:border-blue-500 cursor-pointer transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    {theme.is_cluster && (
                      <div className="mb-2">
                        <span className="text-xs px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded font-medium">
                          Major Cluster
                        </span>
                      </div>
                    )}
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                      {theme.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                      {theme.description}
                    </p>
                    {/* Show merged themes if this is a cluster */}
                    {theme.is_cluster && theme.themes_merged_names && theme.themes_merged_names.length > 0 && (
                      <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Themes merged ({theme.themes_merged_names.length}):
                        </div>
                        <div className="space-y-1">
                          {theme.themes_merged_names.map((mergedName: string, idx: number) => (
                            <div key={idx} className="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-1">
                              <span className="w-1 h-1 bg-blue-500 rounded-full"></span>
                              {mergedName}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {/* Unique Features: ARR Impact, Lost Deals, Competitors */}
                    <div className="mt-2 flex flex-wrap gap-2">
                      {theme.avg_arr > 0 ? (
                        <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded">
                          💰 ${(theme.avg_arr / 1000).toFixed(0)}K avg ARR
                        </span>
                      ) : (
                        <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded">
                          💰 Calculating ARR...
                        </span>
                      )}
                      {theme.lost_deal_arr > 0 && (
                        <span className="text-xs px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded">
                          ⚠️ ${(theme.lost_deal_arr / 1000).toFixed(0)}K lost ARR
                        </span>
                      )}
                      {theme.lost_deal_count > 0 && (
                        <span className="text-xs px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 rounded">
                          📉 {theme.lost_deal_count} lost deal{theme.lost_deal_count > 1 ? 's' : ''}
                        </span>
                      )}
                      {theme.competitor_mentions && theme.competitor_mentions.length > 0 && (
                        <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded">
                          🎯 {theme.competitor_mentions.slice(0, 2).map((c: any) => {
                            if (typeof c === 'string') return c
                            if (c && typeof c === 'object') return c.name || String(c)
                            return String(c)
                          }).join(', ')}
                          {theme.competitor_mentions.length > 2 ? '...' : ''}
                        </span>
                      )}
                    </div>
                    {/* Time-Series Trend - UNIQUE FEATURE */}
                    {theme.trend_data && theme.trend_data.length > 0 && (
                      <div className="mt-2">
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Trend:</div>
                        <div className="flex items-end gap-1 h-8">
                          {theme.trend_data.map((point: any, idx: number) => (
                            <div
                              key={idx}
                              className="flex-1 bg-blue-200 dark:bg-blue-800 rounded-t"
                              style={{ height: `${(point.count / Math.max(...theme.trend_data.map((p: any) => p.count))) * 100}%` }}
                              title={`${point.month}: ${point.count} requests`}
                            />
                          ))}
                        </div>
                        <div className="flex justify-between text-xs text-gray-400 mt-1">
                          <span>{theme.trend_data[0]?.month}</span>
                          <span>{theme.trend_data[theme.trend_data.length - 1]?.month}</span>
                        </div>
                      </div>
                    )}
                  </div>
                  <Layers className="w-5 h-5 text-blue-500 flex-shrink-0 ml-2" />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Volume</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {theme.request_frequency} requests
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400 flex items-center gap-1">
                      <DollarSign className="w-3 h-3" /> Avg ARR
                    </span>
                    <span className={`font-medium ${theme.avg_arr > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-400'}`}>
                      {theme.avg_arr > 0 ? `$${(theme.avg_arr / 1000).toFixed(0)}K` : 'N/A'}
                    </span>
                  </div>

                  {(theme.lost_deal_count > 0 || theme.competitor_mentions?.length > 0) && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500 dark:text-gray-400">Lost Deals</span>
                      <span className="font-medium text-red-600 dark:text-red-400">
                        {theme.lost_deal_count > 0 ? `${theme.lost_deal_count} (${theme.lost_deal_arr > 0 ? `$${(theme.lost_deal_arr / 1000).toFixed(0)}K ARR` : 'No ARR data'})` : 'Competitor pressure'}
                      </span>
                    </div>
                  )}

                  {theme.competitor_mentions && theme.competitor_mentions.length > 0 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500 dark:text-gray-400">Competitors</span>
                      <span className="font-medium text-blue-600 dark:text-blue-400 text-xs">
                        {theme.competitor_mentions.slice(0, 2).map((c: any) => {
                          if (typeof c === 'string') return c
                          if (c && typeof c === 'object') return c.name || String(c)
                          return String(c)
                        }).join(', ')}
                        {theme.competitor_mentions.length > 2 ? '...' : ''}
                      </span>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Pain Score</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-red-500 h-2 rounded-full"
                          style={{ width: `${((theme.customer_value || 0) / 10) * 100}%` }}
                        />
                      </div>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {(theme.customer_value || 0).toFixed(1)}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Impact Score</span>
                    <span className="font-bold text-blue-600 dark:text-blue-400">
                      {(theme.impact_score || 0).toFixed(1)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Trend</span>
                    <div className="flex items-center space-x-1">
                      {getTrendIcon(theme.trend_velocity || 0)}
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {theme.trend || (theme.trend_velocity > 0 ? 'Growing' : theme.trend_velocity < 0 ? 'Declining' : 'Stable')}
                      </span>
                    </div>
                  </div>
                </div>

                <button className="mt-4 w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
                  <span className="text-sm font-medium">Open Theme</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {viewMode === 'bubble' && (
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-8 min-h-[600px] flex items-center justify-center">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <Layers className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Bubble map visualization coming soon</p>
            </div>
          </div>
        )}

        {viewMode === 'trend' && (
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-8 min-h-[600px] flex items-center justify-center">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <TrendingUp className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Trend visualization coming soon</p>
            </div>
          </div>
        )}
      </div>

      {/* Theme Detail Modal */}
      {selectedTheme && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
          onClick={() => setSelectedTheme(null)}
        >
          <div 
            className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 p-6 flex items-center justify-between z-10">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                {typeof selectedTheme.name === 'string' ? selectedTheme.name : (selectedTheme.name?.toString() || 'Unnamed Theme')}
              </h2>
              <button
                onClick={() => setSelectedTheme(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-2xl font-bold leading-none"
              >
                ×
              </button>
            </div>
            <div className="p-6">
              {selectedTheme.is_cluster && (
                <div className="mb-4 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                  <div className="text-xs font-medium text-purple-700 dark:text-purple-400 mb-2">
                    Major Cluster
                  </div>
                  <div className="text-sm text-gray-700 dark:text-gray-300">
                    {typeof selectedTheme.description === 'string' ? selectedTheme.description : (selectedTheme.description?.toString() || '')}
                  </div>
                </div>
              )}
              {!selectedTheme.is_cluster && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                  {typeof selectedTheme.description === 'string' ? selectedTheme.description : (selectedTheme.description?.toString() || '')}
                </p>
              )}

              <div className="space-y-6">
            {/* Show merged themes if this is a cluster */}
            {selectedTheme.is_cluster && selectedTheme.themes_merged && selectedTheme.themes_merged.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Themes Merged ({selectedTheme.themes_merged.length})
                </h3>
                <div className="space-y-2">
                  {selectedTheme.themes_merged.map((mergedTheme: any, idx: number) => (
                    <div key={idx} className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
                      <div className="font-medium text-sm text-gray-900 dark:text-white mb-1">
                        {mergedTheme.name}
                      </div>
                      {mergedTheme.description && (
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                          {mergedTheme.description}
                        </div>
                      )}
                      <div className="flex flex-wrap gap-2 text-xs">
                        {mergedTheme.avg_arr > 0 && (
                          <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded">
                            ${(mergedTheme.avg_arr / 1000).toFixed(0)}K ARR
                          </span>
                        )}
                        {mergedTheme.lost_deal_count > 0 && (
                          <span className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded">
                            {mergedTheme.lost_deal_count} lost deals
                          </span>
                        )}
                        {mergedTheme.competitor_mentions && mergedTheme.competitor_mentions.length > 0 && (
                          <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded">
                            {mergedTheme.competitor_mentions.slice(0, 2).map((c: any) => {
                              if (typeof c === 'string') return c
                              if (c && typeof c === 'object') return c.name || String(c)
                              return String(c)
                            }).join(', ')}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                {selectedTheme.is_cluster ? 'Combined Stats' : 'Key Metrics'}
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500 dark:text-gray-400">Feedback Volume</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {selectedTheme.request_frequency}
                  </span>
                </div>
                {selectedTheme.avg_arr > 0 && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1">
                      <DollarSign className="w-3 h-3" /> Average ARR
                    </span>
                    <span className="font-medium text-green-600 dark:text-green-400">
                      ${(selectedTheme.avg_arr / 1000).toFixed(0)}K
                    </span>
                  </div>
                )}
                {selectedTheme.total_arr > 0 && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Total ARR</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      ${(selectedTheme.total_arr / 1000).toFixed(0)}K
                    </span>
                  </div>
                )}
                {selectedTheme.has_lost_deals && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500 dark:text-gray-400">Lost Deals</span>
                      <span className="font-medium text-red-600 dark:text-red-400">
                        {selectedTheme.lost_deal_count} deals
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500 dark:text-gray-400">Lost ARR</span>
                      <span className="font-medium text-red-600 dark:text-red-400">
                        ${(selectedTheme.lost_deal_arr / 1000).toFixed(0)}K
                      </span>
                    </div>
                  </>
                )}
                {selectedTheme.competitor_mentions && selectedTheme.competitor_mentions.length > 0 && (
                  <div className="flex items-start justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Competitors</span>
                    <div className="text-right">
                      {selectedTheme.competitor_mentions.map((comp: any, idx: number) => {
                        let compName: string
                        if (typeof comp === 'string') {
                          compName = comp
                        } else if (comp && typeof comp === 'object') {
                          compName = comp.name || String(comp)
                        } else {
                          compName = String(comp)
                        }
                        return (
                          <span key={idx} className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded mr-1 mb-1 inline-block">
                            {compName}
                          </span>
                        )
                      })}
                    </div>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500 dark:text-gray-400">Customer Value</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {(selectedTheme.customer_value || 0).toFixed(1)}/10
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500 dark:text-gray-400">Impact Score</span>
                  <span className="font-bold text-blue-600 dark:text-blue-400">
                    {(selectedTheme.impact_score || 0).toFixed(1)}/10
                  </span>
                </div>
              </div>
            </div>

            {/* Show all individual feedback requests grouped in this theme */}
            {selectedTheme.feedback_items && selectedTheme.feedback_items.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  All Feedback Requests ({selectedTheme.feedback_items.length} requests grouped)
                </h3>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {selectedTheme.feedback_items.map((feedback: any, idx: number) => (
                    <div key={feedback.id || idx} className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            {feedback.source && typeof feedback.source === 'string' && (
                              <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded">
                                {feedback.source}
                              </span>
                            )}
                            {feedback.classification && typeof feedback.classification === 'string' && (
                              <span className="text-xs px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded">
                                {feedback.classification}
                              </span>
                            )}
                            {feedback.urgency && typeof feedback.urgency === 'string' && (
                              <span className={`text-xs px-2 py-1 rounded ${
                                feedback.urgency === 'high' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' :
                                feedback.urgency === 'medium' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400' :
                                'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                              }`}>
                                {feedback.urgency}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-900 dark:text-white mb-2">
                            {typeof feedback.content === 'string' ? feedback.content : JSON.stringify(feedback.content)}
                          </p>
                          <div className="flex flex-wrap gap-2 text-xs">
                            {feedback.arr && typeof feedback.arr === 'number' && feedback.arr > 0 && (
                              <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded">
                                💰 ${(feedback.arr / 1000).toFixed(0)}K ARR
                              </span>
                            )}
                            {feedback.pain_level && typeof feedback.pain_level === 'number' && feedback.pain_level > 0 && (
                              <span className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded">
                                Pain: {feedback.pain_level.toFixed(1)}/10
                              </span>
                            )}
                            {feedback.sentiment_score !== undefined && feedback.sentiment_score !== null && typeof feedback.sentiment_score === 'number' && (
                              <span className={`px-2 py-1 rounded ${
                                feedback.sentiment_score > 0 ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' :
                                feedback.sentiment_score < 0 ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' :
                                'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                              }`}>
                                Sentiment: {feedback.sentiment_score > 0 ? '+' : ''}{feedback.sentiment_score.toFixed(2)}
                              </span>
                            )}
                            {feedback.account_id && typeof feedback.account_id !== 'object' && (
                              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded">
                                Account: {String(feedback.account_id)}
                              </span>
                            )}
                            {feedback.user_segment && typeof feedback.user_segment !== 'object' && (
                              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded">
                                {String(feedback.user_segment)}
                              </span>
                            )}
                            {feedback.created_at && typeof feedback.created_at === 'string' && (
                              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded">
                                {new Date(feedback.created_at).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Actions
              </h3>
              <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 mb-2">
                Promote to Roadmap
              </button>
              </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

