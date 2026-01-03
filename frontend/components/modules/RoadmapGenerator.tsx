'use client'

import { useState, useEffect } from 'react'
import { Calendar, Target, CheckCircle, XCircle, Download, Share2, Sparkles, Quote, Users, TrendingUp, AlertTriangle, Zap, DollarSign, Clock, Users2, Shield, FileText, ArrowRight } from 'lucide-react'
import { roadmapApi } from '@/lib/api'
import MainLayout from '@/components/layout/MainLayout'

// Cache key for roadmap data
const ROADMAP_CACHE_KEY = 'naio_roadmap_cache'

export default function RoadmapGenerator() {
  const [step, setStep] = useState(1)
  const [timeframe, setTimeframe] = useState({ quarter: 'Q1', year: 2024 })
  const [roadmap, setRoadmap] = useState<any>(null)
  const [generating, setGenerating] = useState(false)
  const [selectedFeature, setSelectedFeature] = useState<any>(null)
  const [progress, setProgress] = useState<string>('')
  const [autoLoaded, setAutoLoaded] = useState(false)
  const [isCached, setIsCached] = useState(false)

  // Load from cache on mount
  useEffect(() => {
    loadFromCache()
  }, [])

  const loadFromCache = () => {
    try {
      const cached = localStorage.getItem(ROADMAP_CACHE_KEY)
      if (cached) {
        const cachedData = JSON.parse(cached)
        // Try to load the most recent roadmap from cache
        if (cachedData.roadmaps && Object.keys(cachedData.roadmaps).length > 0) {
          const latestKey = Object.keys(cachedData.roadmaps).sort().reverse()[0]
          const latestRoadmap = cachedData.roadmaps[latestKey]
          if (latestRoadmap) {
            const [quarter, year] = latestKey.split('-')
            setTimeframe({ quarter, year: parseInt(year) })
            setRoadmap(latestRoadmap.roadmap)
            setStep(3)
            setIsCached(true)
            console.log('✅ Loaded roadmap from cache:', latestKey)
          }
        }
      }
    } catch (error) {
      console.error('Error loading from cache:', error)
    }
  }

  const saveToCache = (quarter: string, year: number, roadmapData: any) => {
    try {
      const cacheKey = `${quarter}-${year}`
      const cached = localStorage.getItem(ROADMAP_CACHE_KEY)
      const cachedData = cached ? JSON.parse(cached) : { roadmaps: {} }
      
      cachedData.roadmaps[cacheKey] = {
        roadmap: roadmapData,
        timestamp: new Date().toISOString()
      }
      
      localStorage.setItem(ROADMAP_CACHE_KEY, JSON.stringify(cachedData))
      console.log('💾 Saved roadmap to cache:', cacheKey)
    } catch (error) {
      console.error('Error saving to cache:', error)
    }
  }

  const generateRoadmap = async (isAutoLoad: boolean = false) => {
    setGenerating(true)
    setStep(2)
    setProgress('Initializing roadmap generation...')
    
    try {
      const response = await roadmapApi.generate({
        quarter: timeframe.quarter,
        year: timeframe.year
      })
      
      // Backend returns {status: "success", roadmap: {...}}
      if (response.data.status === 'success' && response.data.roadmap) {
        // Get the full roadmap with all features
        const roadmapData = response.data.roadmap
        setRoadmap(roadmapData)
        setIsCached(false)
        saveToCache(timeframe.quarter, timeframe.year, roadmapData)
        setStep(3)
        if (isAutoLoad) {
          setProgress('✅ Roadmap loaded automatically!')
        }
      } else {
        throw new Error('Roadmap generation failed: Invalid response format')
      }
    } catch (error: any) {
      console.error('Error generating roadmap:', error)
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || error.message || 'Roadmap generation failed'
      
      // If we have cached roadmap, keep showing it
      if (roadmap) {
        setIsCached(true)
        setStep(3)
        setProgress('')
        if (!isAutoLoad) {
          console.log('⚠️ API error, but showing cached roadmap')
        }
      } else {
        // No cached data, show error
        if (!isAutoLoad) {
          // Only show alert if user manually clicked
          alert(`Error generating roadmap: ${errorMessage}`)
        }
        setStep(1)
        setProgress(`⚠️ ${errorMessage}`)
      }
    } finally {
      setGenerating(false)
      // Clear progress after 3 seconds if auto-loaded
      if (isAutoLoad && progress.includes('✅')) {
        setTimeout(() => setProgress(''), 3000)
      }
    }
  }

  // Auto-generate roadmap on mount (only if not in cache)
  useEffect(() => {
    if (!autoLoaded && !roadmap) {
      setAutoLoaded(true)
      // Check cache first, if not found, generate
      const cacheKey = `${timeframe.quarter}-${timeframe.year}`
      const cached = localStorage.getItem(ROADMAP_CACHE_KEY)
      if (cached) {
        try {
          const cachedData = JSON.parse(cached)
          if (cachedData.roadmaps && cachedData.roadmaps[cacheKey]) {
            setRoadmap(cachedData.roadmaps[cacheKey].roadmap)
            setIsCached(true)
            setStep(3)
            console.log('✅ Loaded roadmap from cache on mount:', cacheKey)
            return
          }
        } catch (error) {
          console.error('Error reading cache:', error)
        }
      }
      // If not in cache, generate
      generateRoadmap(true) // Pass true to indicate auto-load
    }
  }, [])

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border-red-300 dark:border-red-700'
      case 'high': return 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 border-orange-300 dark:border-orange-700'
      case 'medium': return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 border-yellow-300 dark:border-yellow-700'
      default: return 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-700'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'P0': return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
      case 'P1': return 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400'
      case 'P2': return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
      case 'P3': return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
      default: return 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
    }
  }

  return (
    <MainLayout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            🗺️ AI Roadmap Generator
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Generate quarterly roadmap proposals with customer quotes, data justification, ARR impact, and team benefits
          </p>
        </div>

        {/* Step 1: Timeframe Selection */}
        {step === 1 && (
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Select Quarter for Roadmap
              </h2>
              {roadmap && (
                <button
                  onClick={() => {
                    setStep(3)
                  }}
                  className="px-4 py-2 text-sm text-blue-600 dark:text-blue-400 hover:underline"
                >
                  View Current Roadmap →
                </button>
              )}
            </div>
            <div className="grid grid-cols-4 gap-4 mb-6">
              {['Q1', 'Q2', 'Q3', 'Q4'].map((q) => (
                <button
                  key={q}
                  onClick={() => setTimeframe({ ...timeframe, quarter: q })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    timeframe.quarter === q
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-800 hover:border-blue-300'
                  }`}
                >
                  <div className="font-semibold text-gray-900 dark:text-white">{q}</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">{timeframe.year}</div>
                </button>
              ))}
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Year
              </label>
              <input
                type="number"
                value={timeframe.year}
                onChange={(e) => setTimeframe({ ...timeframe, year: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                min="2020"
                max="2100"
              />
            </div>
            <button
              onClick={() => generateRoadmap(false)}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-all"
            >
              Generate {timeframe.quarter} {timeframe.year} Roadmap
            </button>
            {roadmap && (
              <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-sm text-blue-700 dark:text-blue-400">
                  💡 You have a roadmap for {timeframe.quarter} {timeframe.year}. Generate a new one or view the current roadmap above.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Step 2: Generation Progress */}
        {step === 2 && generating && (
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
              <div className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {progress.includes('✅') ? 'Roadmap Loaded!' : 'Generating Roadmap...'}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {progress || 'Analyzing themes, features, competitors, and impact scores'}
              </div>
              {progress.includes('✅') && (
                <div className="mt-4 text-sm text-green-600 dark:text-green-400">
                  Automatically loaded {timeframe.quarter} {timeframe.year} roadmap
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Roadmap Display */}
        {step >= 3 && roadmap && (
          <div className="space-y-6">
            {/* Roadmap Header */}
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-4 mb-2">
                    <button
                      onClick={() => {
                        setStep(1)
                        setRoadmap(null)
                        setSelectedFeature(null)
                      }}
                      className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300"
                    >
                      ← Back to Selection
                    </button>
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                      {timeframe.quarter} {timeframe.year} Roadmap Proposal
                    </h2>
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {roadmap.debate_process?.themes_analyzed || 0} themes analyzed, {roadmap.debate_process?.final_selected || 0} features selected
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => {
                      setStep(1)
                      setRoadmap(null)
                      setSelectedFeature(null)
                    }}
                    className="px-4 py-2 border border-blue-300 dark:border-blue-700 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 flex items-center gap-2 text-blue-700 dark:text-blue-400 font-medium"
                  >
                    Change Quarter
                  </button>
                  <button className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
                    <Download className="w-4 h-4" />
                    Export
                  </button>
                  <button className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
                    <Share2 className="w-4 h-4" />
                    Share
                  </button>
                </div>
              </div>

              {/* Summary Stats */}
              {roadmap.debate_process && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded">
                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Themes Analyzed</div>
                    <div className="text-lg font-bold text-red-600 dark:text-red-400">
                      {roadmap.debate_process.themes_analyzed || 0}
                    </div>
                  </div>
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded">
                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Features Selected</div>
                    <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                      {roadmap.debate_process.final_selected || 0}
                    </div>
                  </div>
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded">
                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Recommendations Created</div>
                    <div className="text-lg font-bold text-green-600 dark:text-green-400">
                      {roadmap.debate_process.recommendations_created || 0}
                    </div>
                  </div>
                  <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded">
                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Quarter</div>
                    <div className="text-lg font-bold text-purple-600 dark:text-purple-400">
                      {timeframe.quarter} {timeframe.year}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Roadmap Items - Enhanced with All Requested Fields */}
            <div className="space-y-6">
              {roadmap.items && roadmap.items.map((item: any, index: number) => (
                <div
                  key={item.id}
                  className="bg-white dark:bg-gray-900 rounded-lg border-2 border-gray-200 dark:border-gray-800 p-6 hover:shadow-xl transition-all cursor-pointer"
                  onClick={() => setSelectedFeature(item)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-3">
                        <span className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-bold text-lg">
                          {index + 1}
                        </span>
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">
                            {item.title}
                          </h3>
                          <div className="flex items-center gap-2 flex-wrap">
                            {item.priority && (
                              <span className={`px-3 py-1 text-xs rounded-full font-semibold ${getPriorityColor(item.priority)}`}>
                                {item.priority}
                              </span>
                            )}
                            <span className="px-3 py-1 text-xs rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-semibold">
                              Impact: {item.impact_score?.toFixed(1) || 'N/A'}/10
                            </span>
                            {item.estimated_timeline && (
                              <span className="px-3 py-1 text-xs rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 font-semibold flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {item.estimated_timeline.weeks || item.estimated_timeline.quarter}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Summary */}
                      {item.summary && (
                        <p className="text-sm text-gray-700 dark:text-gray-300 mb-4 ml-13 leading-relaxed">
                          {item.summary}
                        </p>
                      )}

                      {/* Why This Matters Now */}
                      {item.why_this_matters_now && (
                        <div className="mb-4 ml-13 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-l-4 border-blue-500">
                          <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                            <span className="text-sm font-semibold text-blue-900 dark:text-blue-300">Why This Matters Now</span>
                          </div>
                          <p className="text-sm text-blue-800 dark:text-blue-200">
                            {item.why_this_matters_now}
                          </p>
                        </div>
                      )}

                      {/* Quick Stats Grid */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 ml-13 mb-4">
                        {item.arr_impact_potential && (
                          <>
                            {item.arr_impact_potential.total_arr_requested > 0 && (
                              <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded border border-green-200 dark:border-green-800">
                                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Total ARR</div>
                                <div className="text-sm font-bold text-green-600 dark:text-green-400">
                                  ${(item.arr_impact_potential.total_arr_requested / 1000).toFixed(0)}K
                                </div>
                              </div>
                            )}
                            {item.arr_impact_potential.customers_affected > 0 && (
                              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
                                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Customers</div>
                                <div className="text-sm font-bold text-blue-600 dark:text-blue-400">
                                  {item.arr_impact_potential.customers_affected}
                                </div>
                              </div>
                            )}
                            {item.arr_impact_potential.lost_deal_arr > 0 && (
                              <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
                                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">ARR at Risk</div>
                                <div className="text-sm font-bold text-red-600 dark:text-red-400">
                                  ${(item.arr_impact_potential.lost_deal_arr / 1000).toFixed(0)}K
                                </div>
                              </div>
                            )}
                          </>
                        )}
                        {item.teams_benefit && item.teams_benefit.length > 0 && (
                          <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded border border-purple-200 dark:border-purple-800">
                            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Teams Benefit</div>
                            <div className="text-sm font-bold text-purple-600 dark:text-purple-400">
                              {item.teams_benefit.join(', ')}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Risk Indicator */}
                      {item.risk_of_not_doing_it && (
                        <div className={`ml-13 p-3 rounded-lg border-2 ${getRiskColor(item.risk_of_not_doing_it.level)} mb-4`}>
                          <div className="flex items-center gap-2 mb-1">
                            <Shield className="w-4 h-4" />
                            <span className="text-sm font-semibold">Risk of Not Doing It: {item.risk_of_not_doing_it.level.toUpperCase()}</span>
                          </div>
                          <ul className="text-xs space-y-1 ml-6">
                            {item.risk_of_not_doing_it.reasons.map((reason: string, i: number) => (
                              <li key={i}>• {reason}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Top Customer Quotes Preview */}
                      {item.top_customer_quotes && item.top_customer_quotes.length > 0 && (
                        <div className="ml-13 mb-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Quote className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                              Top Customer Quotes ({item.top_customer_quotes.length})
                            </span>
                          </div>
                          <div className="space-y-2">
                            {item.top_customer_quotes.slice(0, 2).map((quote: any, i: number) => {
                              const quoteText = typeof quote === 'string' ? quote : (quote.quote || quote.content || JSON.stringify(quote))
                              return (
                                <div key={i} className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded border-l-4 border-yellow-400">
                                  <p className="text-xs text-gray-700 dark:text-gray-300 italic">
                                    "{quoteText.length > 150 ? quoteText.substring(0, 150) + '...' : quoteText}"
                                  </p>
                                </div>
                              )
                            })}
                            {item.top_customer_quotes.length > 2 && (
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                +{item.top_customer_quotes.length - 2} more quotes
                              </p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 text-sm">
                        View Details
                        <ArrowRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Feature Detail Modal with All Fields */}
        {selectedFeature && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
            onClick={() => setSelectedFeature(null)}
          >
            <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 p-6 flex items-center justify-between z-10">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {selectedFeature.title}
                </h2>
                <button
                  onClick={() => setSelectedFeature(null)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-2xl font-bold leading-none"
                >
                  ×
                </button>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Summary */}
                {selectedFeature.summary && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                      <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      Summary
                    </h3>
                    <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                      {selectedFeature.summary}
                    </p>
                  </div>
                )}

                {/* Why This Matters Now */}
                {selectedFeature.why_this_matters_now && (
                  <div className="p-5 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-l-4 border-blue-500">
                    <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-300 mb-3 flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5" />
                      Why This Matters Now
                    </h3>
                    <p className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
                      {selectedFeature.why_this_matters_now}
                    </p>
                  </div>
                )}

                {/* Top Customer Quotes */}
                {selectedFeature.top_customer_quotes && selectedFeature.top_customer_quotes.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                      <Quote className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                      Top Customer Quotes ({selectedFeature.top_customer_quotes.length})
                    </h3>
                    <div className="space-y-4">
                      {selectedFeature.top_customer_quotes.map((quote: any, i: number) => {
                        const quoteText = typeof quote === 'string' ? quote : (quote.quote || quote.content || JSON.stringify(quote))
                        const quoteData = typeof quote === 'object' ? quote : {}
                        return (
                          <div key={i} className="p-5 bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-lg border-2 border-yellow-300 dark:border-yellow-700">
                            <p className="text-sm text-gray-800 dark:text-gray-200 italic leading-relaxed mb-3">
                              "{quoteText}"
                            </p>
                            <div className="flex items-center justify-between pt-3 border-t border-yellow-200 dark:border-yellow-800">
                              {quoteData.source && (
                                <span className="text-xs text-gray-600 dark:text-gray-400 font-medium">
                                  Source: {quoteData.source}
                                </span>
                              )}
                              {quoteData.arr && quoteData.arr > 0 && (
                                <span className="text-xs font-bold text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded">
                                  ${(quoteData.arr / 1000).toFixed(0)}K ARR
                                </span>
                              )}
                              {quoteData.data_justification && (
                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                  {quoteData.data_justification}
                                </span>
                              )}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}

                {/* ARR Impact Potential */}
                {selectedFeature.arr_impact_potential && (
                  <div className="p-5 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <h3 className="text-lg font-semibold text-green-900 dark:text-green-300 mb-4 flex items-center gap-2">
                      <DollarSign className="w-5 h-5" />
                      ARR Impact Potential
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="p-4 bg-white dark:bg-gray-800 rounded border border-green-300 dark:border-green-700">
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Total ARR Requested</div>
                        <div className="text-xl font-bold text-green-600 dark:text-green-400">
                          ${(selectedFeature.arr_impact_potential.total_arr_requested / 1000).toFixed(0)}K
                        </div>
                      </div>
                      <div className="p-4 bg-white dark:bg-gray-800 rounded border border-green-300 dark:border-green-700">
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Avg Customer ARR</div>
                        <div className="text-xl font-bold text-green-600 dark:text-green-400">
                          ${(selectedFeature.arr_impact_potential.avg_customer_arr / 1000).toFixed(0)}K
                        </div>
                      </div>
                      <div className="p-4 bg-white dark:bg-gray-800 rounded border border-red-300 dark:border-red-700">
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Lost Deal ARR</div>
                        <div className="text-xl font-bold text-red-600 dark:text-red-400">
                          ${(selectedFeature.arr_impact_potential.lost_deal_arr / 1000).toFixed(0)}K
                        </div>
                      </div>
                      <div className="p-4 bg-white dark:bg-gray-800 rounded border border-blue-300 dark:border-blue-700">
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Customers Affected</div>
                        <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
                          {selectedFeature.arr_impact_potential.customers_affected}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Which Teams Benefit */}
                {selectedFeature.teams_benefit && selectedFeature.teams_benefit.length > 0 && (
                  <div className="p-5 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                    <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-300 mb-4 flex items-center gap-2">
                      <Users2 className="w-5 h-5" />
                      Which Teams Benefit
                    </h3>
                    <div className="flex flex-wrap gap-3">
                      {selectedFeature.teams_benefit.map((team: string, i: number) => (
                        <span key={i} className="px-4 py-2 bg-purple-100 dark:bg-purple-900/40 rounded-full text-sm font-semibold text-purple-700 dark:text-purple-400">
                          {team}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Risk of Not Doing It */}
                {selectedFeature.risk_of_not_doing_it && (
                  <div className={`p-5 rounded-lg border-2 ${getRiskColor(selectedFeature.risk_of_not_doing_it.level)}`}>
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <Shield className="w-5 h-5" />
                      Risk of Not Doing It: {selectedFeature.risk_of_not_doing_it.level.toUpperCase()}
                    </h3>
                    <div className="space-y-2 mb-3">
                      {selectedFeature.risk_of_not_doing_it.reasons.map((reason: string, i: number) => (
                        <div key={i} className="flex items-start gap-2">
                          <span className="text-lg">•</span>
                          <span className="text-sm">{reason}</span>
                        </div>
                      ))}
                    </div>
                    <div className="pt-3 border-t-2 mt-3">
                      <span className="text-sm font-semibold">Impact: </span>
                      <span className="text-sm">{selectedFeature.risk_of_not_doing_it.impact}</span>
                    </div>
                  </div>
                )}

                {/* Estimated Timeline */}
                {selectedFeature.estimated_timeline && (
                  <div className="p-5 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                    <h3 className="text-lg font-semibold text-indigo-900 dark:text-indigo-300 mb-4 flex items-center gap-2">
                      <Clock className="w-5 h-5" />
                      Estimated Timeline
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Target Quarter</div>
                        <div className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                          {selectedFeature.estimated_timeline.quarter || timeframe.quarter}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Estimated Duration</div>
                        <div className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                          {selectedFeature.estimated_timeline.weeks || '8-10 weeks'}
                        </div>
                      </div>
                      {selectedFeature.estimated_timeline.feasibility_score && (
                        <div className="col-span-2">
                          <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Feasibility Score</div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-indigo-600 h-2 rounded-full"
                              style={{ width: `${(selectedFeature.estimated_timeline.feasibility_score / 10) * 100}%` }}
                            />
                          </div>
                          <div className="text-sm font-semibold text-indigo-600 dark:text-indigo-400 mt-1">
                            {selectedFeature.estimated_timeline.feasibility_score.toFixed(1)}/10
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Alternatives Considered */}
                {selectedFeature.alternatives_considered && selectedFeature.alternatives_considered.length > 0 && (
                  <div className="p-5 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                      <Target className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                      Alternatives Considered
                    </h3>
                    <ul className="space-y-2">
                      {selectedFeature.alternatives_considered.map((alt: string, i: number) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                          <span className="mt-1">•</span>
                          <span>{alt}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  )
}
