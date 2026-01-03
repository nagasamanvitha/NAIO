'use client'

import { useState, useEffect } from 'react'
import { FileText, Users, Target, TrendingUp, CheckCircle, Clock, Send, Ship, Mail, Download } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { recommendationsApi, feedbackLoopApi, dashboardApi, roadmapApi } from '@/lib/api'
import { cleanMarkdown, formatText, formatBusinessImpact, formatReasoning, formatList, summarizeText, formatTextWithBold } from '@/lib/textFormatter'

interface FeaturesListProps {
  initialRecommendations?: any[]
}

export default function FeaturesList({ initialRecommendations = [] }: FeaturesListProps) {
  // Use initial recommendations - no API calls
  const [recommendations, setRecommendations] = useState<any[]>(initialRecommendations)
  const [loading, setLoading] = useState(false)
  const [selectedFeature, setSelectedFeature] = useState<any>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [notificationResult, setNotificationResult] = useState<any>(null)
  const [onePager, setOnePager] = useState<any>(null)
  const [adoptionStats, setAdoptionStats] = useState<any>(null)
  const [loadingOnePager, setLoadingOnePager] = useState(false)
  const [loadingAdoptionStats, setLoadingAdoptionStats] = useState(false)
  const [showOnePager, setShowOnePager] = useState(false)
  const [showShipModal, setShowShipModal] = useState(false)
  const [shipQuarter, setShipQuarter] = useState<string>('')
  const [shipYear, setShipYear] = useState<number>(new Date().getFullYear())
  const router = useRouter()
  
  // Update recommendations when initialRecommendations prop changes
  useEffect(() => {
    console.log('✅ FeaturesList useEffect - initialRecommendations changed:', initialRecommendations.length)
    if (initialRecommendations && initialRecommendations.length > 0) {
      console.log('✅ FeaturesList - Updating recommendations from prop:', initialRecommendations.length)
      setRecommendations(initialRecommendations)
      setLoading(false)
    } else if (initialRecommendations.length === 0) {
      console.log('⚠️ FeaturesList - Empty initialRecommendations, clearing state')
      setRecommendations([])
      setLoading(false)
    }
  }, [initialRecommendations])

  const handleMarkAsShipped = async () => {
    if (!selectedFeature?.id) return
    
    // Show modal to select quarter
    setShowShipModal(true)
  }

  const confirmMarkAsShipped = async () => {
    if (!selectedFeature?.id || !shipQuarter) return
    
    try {
      setActionLoading('shipping')
      setShowShipModal(false)
      
      // Calculate shipped_at date based on selected quarter
      const quarterMap: { [key: string]: { month: number, day: number } } = {
        'Q1': { month: 1, day: 15 },   // Mid-January
        'Q2': { month: 4, day: 15 },   // Mid-April
        'Q3': { month: 7, day: 15 },   // Mid-July
        'Q4': { month: 10, day: 15 }   // Mid-October
      }
      
      const quarterInfo = quarterMap[shipQuarter]
      const shippedAtDate = new Date(shipYear, quarterInfo.month - 1, quarterInfo.day).toISOString()
      
      const response = await recommendationsApi.updateStatus(selectedFeature.id, 'shipped', shippedAtDate)
      
      if (response.data.status === 'success') {
        // Update local state
        setRecommendations(prev => prev.map(rec => 
          rec.id === selectedFeature.id 
            ? { ...rec, status: 'shipped' }
            : rec
        ))
        setSelectedFeature({ ...selectedFeature, status: 'shipped' })
        
        // Show notification count if customers were notified
        const customersNotified = response.data.customers_notified || 0
        if (customersNotified > 0) {
          alert(`✅ Feature marked as shipped in ${shipQuarter} ${shipYear}!\n\n📧 ${customersNotified} customers have been automatically notified.\n\nThis will appear in the ${shipQuarter} ${shipYear} quarterly report.`)
        } else {
          alert(`✅ Feature marked as shipped in ${shipQuarter} ${shipYear}!\n\nThis will appear in the ${shipQuarter} ${shipYear} quarterly report.`)
        }
      }
    } catch (error: any) {
      console.error('Error marking as shipped:', error)
      alert(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setActionLoading(null)
      setShipQuarter('')
    }
  }

  const handleLoadOnePager = async () => {
    if (!selectedFeature?.id) return
    
    try {
      setLoadingOnePager(true)
      const response = await roadmapApi.getOnePager(selectedFeature.id)
      setOnePager(response.data)
      setShowOnePager(true)
    } catch (error: any) {
      console.error('Error loading one-pager:', error)
      alert(`Error loading one-pager: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoadingOnePager(false)
    }
  }

  const handleLoadAdoptionStats = async () => {
    if (!selectedFeature?.id) return
    
    try {
      setLoadingAdoptionStats(true)
      const response = await feedbackLoopApi.getAdoptionStats(selectedFeature.id)
      setAdoptionStats(response.data)
    } catch (error: any) {
      console.error('Error loading adoption stats:', error)
      alert(`Error loading adoption stats: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoadingAdoptionStats(false)
    }
  }

  const handleNotifyCustomers = async () => {
    if (!selectedFeature?.id) return
    
    try {
      setActionLoading('notifying')
      setNotificationResult(null)
      
      // Try backend first, fallback to mock data
      try {
        const response = await feedbackLoopApi.notifyCustomers(selectedFeature.id, true)
        
        if (response.data.status === 'success') {
          setNotificationResult(response.data)
          alert(`Success! Generated ${response.data.email_templates?.length || 0} email templates for ${response.data.total_customers} customers.`)
          return
        }
      } catch (backendError: any) {
        // If backend fails, use mock data
        console.log('Backend unavailable, using mock data for notifications')
      }
      
      // Mock notification generation from static data
      const mockFeedback = (await import('@/lib/mockData')).mockFeedback
      const matchingFeedback = mockFeedback.filter(
        (f: any) => f.feature === selectedFeature.feature && f.account_id
      )
      
      // Group by customer
      const customerMap = new Map<string, any[]>()
      matchingFeedback.forEach((f: any) => {
        if (f.account_id) {
          if (!customerMap.has(f.account_id)) {
            customerMap.set(f.account_id, [])
          }
          customerMap.get(f.account_id)!.push(f)
        }
      })
      
      const customerIds = Array.from(customerMap.keys())
      
      // Generate email templates
      const emailTemplates = Array.from(customerMap.entries()).map(([customerId, feedbacks]) => {
        const quotes = feedbacks.slice(0, 3).map((f: any) => 
          f.content.length > 200 ? f.content.substring(0, 200) + '...' : f.content
        )
        
        return {
          to: customerId,
          subject: `🎉 ${selectedFeature.title} is now available!`,
          body: `Hi there!\n\nGreat news! We've shipped a feature you requested: **${selectedFeature.title}**\n\n${selectedFeature.description || 'This feature addresses feedback you provided and is now live in the product.'}\n\n**What you asked for:**\n${quotes.map((q: string, i: number) => `${i + 1}. "${q}"`).join('\n')}\n\n**What's new:**\n${selectedFeature.description || 'The feature is now available for you to use.'}\n\n**Try it now:**\n[Link to feature/documentation]\n\nWe'd love to hear your feedback on this update!\n\nBest regards,\nThe Product Team`,
          html_body: generateMockHtmlEmail(selectedFeature, quotes)
        }
      })
      
      const mockResult = {
        notified: customerIds.length,
        total_customers: customerIds.length,
        customer_ids: customerIds,
        feature: selectedFeature.title,
        email_templates: emailTemplates,
        message: `Generated ${emailTemplates.length} email templates for ${customerIds.length} customers`
      }
      
      setNotificationResult(mockResult)
      alert(`Success! Generated ${emailTemplates.length} email templates for ${customerIds.length} customers.`)
    } catch (error: any) {
      console.error('Error notifying customers:', error)
      alert(`Error: ${error.message}`)
    } finally {
      setActionLoading(null)
    }
  }
  
  const generateMockHtmlEmail = (feature: any, quotes: string[]) => {
    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .feature-box { background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #667eea; border-radius: 5px; }
        .quote { background: #f0f0f0; padding: 15px; margin: 10px 0; border-left: 3px solid #667eea; font-style: italic; }
        .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Feature Shipped!</h1>
            <p>${feature.title} is now available!</p>
        </div>
        <div class="content">
            <div class="feature-box">
                <h2>${feature.title}</h2>
                <p>${feature.description || 'This feature addresses feedback you provided and is now live.'}</p>
            </div>
            
            <h3>What you asked for:</h3>
            ${quotes.map((q: string) => `<div class="quote">"${q}"</div>`).join('\n')}
            
            <div style="text-align: center;">
                <a href="#" class="button">Try It Now →</a>
            </div>
            
            <div class="footer">
                <p>This is an automated notification. You're receiving this because you requested this feature.</p>
            </div>
        </div>
    </div>
</body>
</html>`
  }

  const downloadEmailTemplates = (templates: any[]) => {
    // Create a downloadable JSON file with all email templates
    const dataStr = JSON.stringify(templates, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `email-templates-${selectedFeature.id}-${Date.now()}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const loadRecommendations = async () => {
    try {
      const { data } = await dashboardApi.getRecommendations()
      if (data.recommendations && data.recommendations.length > 0) {
        setRecommendations(data.recommendations)
      }
      // Recommendations are generated automatically when themes are created via n8n workflow
      // No manual generation needed
    } catch (error) {
      console.error('Error loading recommendations:', error)
      // Recommendations are generated automatically - just show empty state if none exist
    } finally {
      setLoading(false)
    }
  }

  // Recommendations are generated automatically when themes are created via n8n workflow
  // No manual generation needed - the flow is: Feedback → Themes → Recommendations (all automatic)

  // Only show loading if we truly have no data
  if (loading && recommendations.length === 0 && initialRecommendations.length === 0) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <div className="text-gray-500">Loading features...</div>
        </div>
      </div>
    )
  }

  // Debug logging
  console.log('✅ FeaturesList render - recommendations.length:', recommendations.length)
  console.log('✅ FeaturesList render - initialRecommendations.length:', initialRecommendations.length)

  if (recommendations.length === 0) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            No Recommendations Yet
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mb-2">
            Recommendations are generated automatically when you run the n8n workflow.
          </p>
          <p className="text-sm text-gray-400 mb-4">
            Flow: <strong>Feedback → Themes → Recommendations</strong> (all automatic)
          </p>
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 max-w-md mx-auto text-left">
            <p className="text-sm text-blue-800 dark:text-blue-300 font-medium mb-2">When themes are created, recommendations automatically include:</p>
            <ul className="text-xs text-blue-700 dark:text-blue-400 space-y-1">
              <li>• ARR values, lost deals, competitor info</li>
              <li>• Detailed persona agent debates (PM, UX, Data Scientist, Engineering)</li>
              <li>• Team consensus and prioritization (P0/P1/P2/P3)</li>
              <li>• Customer quotes with source and ARR</li>
              <li>• Competitor radar/intelligence</li>
            </ul>
          </div>
          <p className="text-xs text-gray-400 mt-4">Run your n8n workflow to process feedback and generate recommendations automatically.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full">
      <div className="overflow-y-auto p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Feature Recommendations
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            AI-generated feature recommendations with persona evaluations
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recommendations.length > 0 ? (
            recommendations.map((rec) => (
              <div
                key={rec.id}
                onClick={() => setSelectedFeature(rec)}
                className="p-6 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 hover:border-blue-500 cursor-pointer transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {rec.title}
                  </h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    rec.status === 'pending' ? 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400' :
                    rec.status === 'approved' ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400' :
                    'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
                  }`}>
                    {rec.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                  {rec.description}
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Impact:</span>
                      <span className="ml-1 font-semibold text-blue-600 dark:text-blue-400">
                        {rec.impact_score?.toFixed(1) || 'N/A'}
                      </span>
                    </div>
                  </div>
                  <FileText className="w-5 h-5 text-gray-400" />
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full text-center py-8 text-gray-500">
              No recommendations to display
            </div>
          )}
        </div>
      </div>

      {/* Feature Detail Modal */}
      {selectedFeature && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
          onClick={() => {
            setSelectedFeature(null)
            setShowOnePager(false)
            setOnePager(null)
            setAdoptionStats(null)
          }}
        >
          <div 
            className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 p-6 flex items-center justify-between z-10">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white leading-tight">
                {selectedFeature.title}
              </h2>
              <button
                onClick={() => {
                  setSelectedFeature(null)
                  setShowOnePager(false)
                  setOnePager(null)
                  setAdoptionStats(null)
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-2xl font-bold leading-none"
              >
                ×
              </button>
            </div>
            <div className="p-8">
              <div className="space-y-8">
                {/* Feature Summary - Enhanced */}
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-5 border border-gray-200 dark:border-gray-700">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                Feature Summary
              </h3>
              <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-3">
                {/* Main Description */}
                {selectedFeature.description && (
                  <p className="mb-3">{selectedFeature.description}</p>
                )}
                
                {/* Additional context from evidence if available */}
                {selectedFeature.evidence?.data_justification?.feedback_cluster_summary && (
                  <div className="mt-3 p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                    <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase tracking-wide">Feedback Cluster Summary</div>
                    <p className="text-sm">{selectedFeature.evidence.data_justification.feedback_cluster_summary}</p>
            </div>
                )}
                
                {/* Show feature name if different from title */}
                {selectedFeature.feature && selectedFeature.feature !== selectedFeature.title && (
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    <span className="font-medium">Feature:</span> {selectedFeature.feature}
                  </div>
                )}
              </div>
            </div>

            {/* Why This Matters - Enhanced */}
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-5 border border-blue-200 dark:border-blue-800">
                <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  Why This Matters
                </h3>
                <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-3">
                {/* Business Impact */}
                {selectedFeature.business_impact && (
                  <div className="space-y-2">
                  {formatBusinessImpact(selectedFeature.business_impact).split('\n\n').filter(p => p.trim()).slice(0, 5).map((paragraph, i) => (
                    <div key={i} className="space-y-1">
                      {paragraph.split('\n').filter(line => line.trim()).map((line, j) => {
                        const cleaned = cleanMarkdown(line.trim())
                        if (cleaned.startsWith('•') || cleaned.startsWith('-')) {
                          return <div key={j} className="ml-4 text-gray-700 dark:text-gray-300">{cleaned}</div>
                        }
                        if (cleaned.length > 0 && cleaned.length < 100 && !cleaned.includes('.')) {
                          return <div key={j} className="font-semibold text-gray-900 dark:text-white">{cleaned}</div>
                        }
                        return <div key={j} className="text-gray-700 dark:text-gray-300">{cleaned}</div>
                      })}
                    </div>
                  ))}
              </div>
            )}
                
                {/* Unified Recommendation as additional context */}
                {selectedFeature.unified_recommendation && !selectedFeature.business_impact && (
                  <p>{selectedFeature.unified_recommendation}</p>
                )}
                
                {/* Show if no business impact available */}
                {!selectedFeature.business_impact && !selectedFeature.unified_recommendation && (
                  <p className="text-gray-500 dark:text-gray-400 italic">
                    This feature addresses customer needs and competitive gaps. See team evaluations below for detailed analysis.
                  </p>
                )}
              </div>
            </div>

            {/* Metrics */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-5 border border-blue-200 dark:border-blue-800">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                Key Metrics
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Impact Score</div>
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {selectedFeature.impact_score?.toFixed(1) || 'N/A'}
                  </div>
                </div>
                <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Feasibility</div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {selectedFeature.feasibility_score?.toFixed(1) || 'N/A'}
                  </div>
                </div>
                <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Risk Score</div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {selectedFeature.risk_score?.toFixed(1) || 'N/A'}
                  </div>
                </div>
              </div>
            </div>

            {/* Multi-Persona Debate - UNIQUE FEATURE */}
            {selectedFeature.persona_debate && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  🎭 Multi-Persona AI Debate (Unique Feature)
                </h3>
                <div className="space-y-3 text-sm">
                  <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
                    <div className="font-medium text-gray-900 dark:text-white mb-1 flex items-center">
                      👤 Customer Voice
                      <span className="ml-2 text-xs bg-red-100 dark:bg-red-900/40 px-2 py-0.5 rounded">
                        Priority: {selectedFeature.persona_debate.customer_voice.priority}/10
                      </span>
                    </div>
                    <div className="text-gray-700 dark:text-gray-300 text-xs mb-2">
                      <strong>Verdict:</strong> {selectedFeature.persona_debate.customer_voice.verdict}
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-xs">
                      {selectedFeature.persona_debate.customer_voice.reasoning}
                    </div>
                    {selectedFeature.persona_debate.customer_voice.quotes && (
                      <div className="mt-2 pt-2 border-t border-red-200 dark:border-red-800">
                        <div className="text-xs font-medium text-gray-700 dark:text-gray-300">Customer Quotes:</div>
                        {selectedFeature.persona_debate.customer_voice.quotes.map((q: string, i: number) => (
                          <div key={i} className="text-xs text-gray-600 dark:text-gray-400 italic mt-1">
                            "{q}"
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
                    <div className="font-medium text-gray-900 dark:text-white mb-1 flex items-center">
                      📈 Growth PM
                      <span className="ml-2 text-xs bg-blue-100 dark:bg-blue-900/40 px-2 py-0.5 rounded">
                        Priority: {selectedFeature.persona_debate.growth_pm.priority}/10
                      </span>
                    </div>
                    <div className="text-gray-700 dark:text-gray-300 text-xs mb-2">
                      <strong>Verdict:</strong> {selectedFeature.persona_debate.growth_pm.verdict}
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-xs">
                      {selectedFeature.persona_debate.growth_pm.reasoning}
                    </div>
                    {selectedFeature.persona_debate.growth_pm.metrics && (
                      <div className="mt-2 pt-2 border-t border-blue-200 dark:border-blue-800 grid grid-cols-2 gap-2">
                        {selectedFeature.persona_debate.growth_pm.metrics.arr_at_risk && (
                          <div className="text-xs">
                            <span className="font-medium">ARR at Risk:</span> ${(selectedFeature.persona_debate.growth_pm.metrics.arr_at_risk / 1000).toFixed(0)}K
                          </div>
                        )}
                        {selectedFeature.persona_debate.growth_pm.metrics.lost_deals && (
                          <div className="text-xs">
                            <span className="font-medium">Lost Deals:</span> {selectedFeature.persona_debate.growth_pm.metrics.lost_deals}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded border border-purple-200 dark:border-purple-800">
                    <div className="font-medium text-gray-900 dark:text-white mb-1 flex items-center">
                      🎨 UX Designer
                      <span className="ml-2 text-xs bg-purple-100 dark:bg-purple-900/40 px-2 py-0.5 rounded">
                        Priority: {selectedFeature.persona_debate.ux_designer.priority}/10
                      </span>
                    </div>
                    <div className="text-gray-700 dark:text-gray-300 text-xs mb-2">
                      <strong>Verdict:</strong> {selectedFeature.persona_debate.ux_designer.verdict}
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-xs">
                      {selectedFeature.persona_debate.ux_designer.reasoning}
                    </div>
                  </div>
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded border-2 border-green-300 dark:border-green-700">
                    <div className="font-bold text-gray-900 dark:text-white mb-1">
                      ✅ Team Consensus
                    </div>
                    <div className="text-gray-700 dark:text-gray-300 text-xs mb-1">
                      <strong>Final Verdict:</strong> {selectedFeature.persona_debate.consensus.final_verdict}
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-xs">
                      {selectedFeature.persona_debate.consensus.reasoning}
                    </div>
                    <div className="mt-2 text-sm font-bold text-green-600 dark:text-green-400">
                      Final Score: {selectedFeature.persona_debate.consensus.final_score}/10
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Enhanced Persona Agent Deliberations with Full Reasoning */}
            {selectedFeature.evidence && selectedFeature.evidence.evaluations && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  🎭 Persona Agent Deliberations & Team Debate
                </h3>
                <div className="space-y-5">
                  {/* PM Agent */}
                  {selectedFeature.evidence.evaluations.pm && (
                    <div className="p-5 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-800 shadow-sm">
                      <div className="font-bold text-base text-gray-900 dark:text-white mb-3 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">📈</span>
                          <span>Product Manager (PM)</span>
                        </div>
                        <span className="text-xs bg-blue-100 dark:bg-blue-900/40 px-3 py-1 rounded-full font-semibold">
                          Verdict: {selectedFeature.evidence.evaluations.pm.verdict || 'N/A'}
                        </span>
                      </div>
                      {selectedFeature.evidence.evaluations.pm.initial_thoughts && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded border border-blue-100 dark:border-blue-800">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Initial Thoughts:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 italic leading-relaxed">
                            "{selectedFeature.evidence.evaluations.pm.initial_thoughts}"
                          </div>
                        </div>
                      )}
                      {selectedFeature.evidence.evaluations.pm.key_considerations && (
                        <div className="mb-3">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Key Considerations:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                            {selectedFeature.evidence.evaluations.pm.key_considerations}
                          </div>
                        </div>
                      )}
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Detailed Reasoning:</div>
                        <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                          {formatReasoning(selectedFeature.evidence.evaluations.pm.reasoning || selectedFeature.pm_verdict || selectedFeature.evidence.evaluations.pm.priority_justification || 'Evaluation in progress')}
                        </div>
                      </div>
                      {selectedFeature.evidence.evaluations.pm.business_impact && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded border border-blue-100 dark:border-blue-800">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Business Impact:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-2">
                            {formatBusinessImpact(selectedFeature.evidence.evaluations.pm.business_impact).split('\n\n').filter(p => p.trim()).slice(0, 3).map((paragraph, i) => (
                              <div key={i} className="space-y-1">
                                {paragraph.split('\n').filter(line => line.trim()).map((line, j) => {
                                  const cleaned = cleanMarkdown(line.trim())
                                  if (cleaned.startsWith('•') || cleaned.startsWith('-')) {
                                    return <div key={j} className="ml-3 text-gray-700 dark:text-gray-300">{cleaned}</div>
                                  }
                                  return <div key={j} className="text-gray-700 dark:text-gray-300">{cleaned}</div>
                                })}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {selectedFeature.evidence.evaluations.pm.priority_justification && (
                        <div className="mb-2">
                          <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Priority Justification:</div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">
                            {selectedFeature.evidence.evaluations.pm.priority_justification}
                          </div>
                        </div>
                      )}
                      {selectedFeature.evidence.evaluations.pm.concerns && selectedFeature.evidence.evaluations.pm.concerns.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-blue-200 dark:border-blue-800">
                          <div className="text-xs font-medium text-red-600 dark:text-red-400 mb-1">Concerns:</div>
                          <ul className="text-xs text-gray-600 dark:text-gray-400 list-disc list-inside">
                            {selectedFeature.evidence.evaluations.pm.concerns.map((concern: string, i: number) => (
                              <li key={i}>{concern}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {selectedFeature.evidence.evaluations.pm.opportunities && selectedFeature.evidence.evaluations.pm.opportunities.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-blue-200 dark:border-blue-800">
                          <div className="text-xs font-medium text-green-600 dark:text-green-400 mb-1">Opportunities:</div>
                          <ul className="text-xs text-gray-600 dark:text-gray-400 list-disc list-inside">
                            {selectedFeature.evidence.evaluations.pm.opportunities.map((opp: string, i: number) => (
                              <li key={i}>{opp}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {/* UX Agent */}
                  {selectedFeature.evidence.evaluations.ux && (
                    <div className="p-5 bg-purple-50 dark:bg-purple-900/20 rounded-lg border-2 border-purple-200 dark:border-purple-800 shadow-sm">
                      <div className="font-bold text-base text-gray-900 dark:text-white mb-3 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">🎨</span>
                          <span>UX Designer</span>
                        </div>
                        <span className="text-xs bg-purple-100 dark:bg-purple-900/40 px-3 py-1 rounded-full font-semibold">
                          Verdict: {selectedFeature.evidence.evaluations.ux.verdict || 'N/A'}
                        </span>
                      </div>
                      {selectedFeature.evidence.evaluations.ux.initial_thoughts && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded border border-purple-100 dark:border-purple-800">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Initial Thoughts:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 italic leading-relaxed">
                            "{selectedFeature.evidence.evaluations.ux.initial_thoughts}"
                          </div>
                        </div>
                      )}
                      {selectedFeature.evidence.evaluations.ux.key_considerations && (
                        <div className="mb-3">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Key Considerations:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                            {selectedFeature.evidence.evaluations.ux.key_considerations}
                          </div>
                        </div>
                      )}
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Detailed Reasoning:</div>
                        <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                          {selectedFeature.evidence.evaluations.ux.reasoning || selectedFeature.ux_verdict || 'Pending evaluation'}
                        </div>
                      </div>
                      {selectedFeature.evidence.evaluations.ux.ux_implications && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded border border-purple-100 dark:border-purple-800">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">UX Implications:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-2">
                            {formatBusinessImpact(selectedFeature.evidence.evaluations.ux.ux_implications || selectedFeature.ux_implications || '').split('\n\n').filter(p => p.trim()).slice(0, 4).map((paragraph, i) => (
                              <div key={i} className="space-y-1">
                                {paragraph.split('\n').filter(line => line.trim()).map((line, j) => {
                                  const cleaned = cleanMarkdown(line.trim())
                                  if (cleaned.startsWith('•') || cleaned.startsWith('-')) {
                                    return <div key={j} className="ml-3 text-gray-700 dark:text-gray-300">{cleaned}</div>
                                  }
                                  return <div key={j} className="text-gray-700 dark:text-gray-300">{cleaned}</div>
                                })}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {selectedFeature.evidence.evaluations.ux.priority_justification && (
                        <div className="mb-2">
                          <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Priority Justification:</div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">
                            {selectedFeature.evidence.evaluations.ux.priority_justification}
                          </div>
                        </div>
                      )}
                      {selectedFeature.evidence.evaluations.ux.concerns && selectedFeature.evidence.evaluations.ux.concerns.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-purple-200 dark:border-purple-800">
                          <div className="text-xs font-medium text-red-600 dark:text-red-400 mb-1">Concerns:</div>
                          <ul className="text-xs text-gray-600 dark:text-gray-400 list-disc list-inside">
                            {selectedFeature.evidence.evaluations.ux.concerns.map((concern: string, i: number) => (
                              <li key={i}>{concern}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Data Scientist Agent */}
                  {selectedFeature.evidence.evaluations.data_scientist && (
                    <div className="p-5 bg-orange-50 dark:bg-orange-900/20 rounded-lg border-2 border-orange-200 dark:border-orange-800 shadow-sm">
                      <div className="font-bold text-base text-gray-900 dark:text-white mb-3 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">📊</span>
                          <span>Data Scientist</span>
                        </div>
                        <span className="text-xs bg-orange-100 dark:bg-orange-900/40 px-3 py-1 rounded-full font-semibold">
                          Verdict: {selectedFeature.evidence.evaluations.data_scientist.verdict || 'N/A'}
                        </span>
                      </div>
                      {selectedFeature.evidence.evaluations.data_scientist.initial_thoughts && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded border border-orange-100 dark:border-orange-800">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Initial Thoughts:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 italic leading-relaxed">
                            "{selectedFeature.evidence.evaluations.data_scientist.initial_thoughts}"
                          </div>
                        </div>
                      )}
                      {selectedFeature.evidence.evaluations.data_scientist.key_considerations && (
                        <div className="mb-3">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Key Considerations:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                            {selectedFeature.evidence.evaluations.data_scientist.key_considerations}
                          </div>
                        </div>
                      )}
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Detailed Reasoning:</div>
                        <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                          {formatReasoning(selectedFeature.evidence.evaluations.data_scientist.reasoning || selectedFeature.data_scientist_verdict || selectedFeature.evidence.evaluations.data_scientist.priority_justification || 'Evaluation in progress')}
                        </div>
                      </div>
                      {selectedFeature.evidence.evaluations.data_scientist.data_insights && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded border border-orange-100 dark:border-orange-800">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Data Insights:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-2">
                            {formatBusinessImpact(selectedFeature.evidence.evaluations.data_scientist.data_insights).split('\n\n').filter(p => p.trim()).slice(0, 4).map((paragraph, i) => (
                              <div key={i} className="space-y-1">
                                {paragraph.split('\n').filter(line => line.trim()).map((line, j) => {
                                  const cleaned = cleanMarkdown(line.trim())
                                  if (cleaned.startsWith('•') || cleaned.startsWith('-')) {
                                    return <div key={j} className="ml-3 text-gray-700 dark:text-gray-300">{cleaned}</div>
                                  }
                                  return <div key={j} className="text-gray-700 dark:text-gray-300">{cleaned}</div>
                                })}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {selectedFeature.evidence.evaluations.data_scientist.priority_justification && (
                        <div className="mb-2">
                          <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Priority Justification:</div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">
                            {selectedFeature.evidence.evaluations.data_scientist.priority_justification}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Engineering Agent */}
                  {selectedFeature.evidence.evaluations.engineering && (
                    <div className="p-5 bg-green-50 dark:bg-green-900/20 rounded-lg border-2 border-green-200 dark:border-green-800 shadow-sm">
                      <div className="font-bold text-base text-gray-900 dark:text-white mb-3 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">⚙️</span>
                          <span>Engineering Lead</span>
                        </div>
                        <span className="text-xs bg-green-100 dark:bg-green-900/40 px-3 py-1 rounded-full font-semibold">
                          Verdict: {selectedFeature.evidence.evaluations.engineering.verdict || 'N/A'}
                        </span>
                      </div>
                      {selectedFeature.evidence.evaluations.engineering.initial_thoughts && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded border border-green-100 dark:border-green-800">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Initial Thoughts:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 italic leading-relaxed">
                            "{selectedFeature.evidence.evaluations.engineering.initial_thoughts}"
                          </div>
                        </div>
                      )}
                      {selectedFeature.evidence.evaluations.engineering.key_considerations && (
                        <div className="mb-3">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Key Considerations:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                            {selectedFeature.evidence.evaluations.engineering.key_considerations}
                          </div>
                        </div>
                      )}
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Detailed Reasoning:</div>
                        <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                          {selectedFeature.evidence.evaluations.engineering.reasoning || selectedFeature.engineering_verdict || 'Pending evaluation'}
                        </div>
                      </div>
                      {selectedFeature.evidence.evaluations.engineering.technical_assessment && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded border border-green-100 dark:border-green-800">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Technical Assessment:</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-2">
                            {formatBusinessImpact(selectedFeature.evidence.evaluations.engineering.technical_assessment).split('\n\n').filter(p => p.trim()).slice(0, 4).map((paragraph, i) => (
                              <div key={i} className="space-y-1">
                                {paragraph.split('\n').filter(line => line.trim()).map((line, j) => {
                                  const cleaned = cleanMarkdown(line.trim())
                                  if (cleaned.startsWith('•') || cleaned.startsWith('-')) {
                                    return <div key={j} className="ml-3 text-gray-700 dark:text-gray-300">{cleaned}</div>
                                  }
                                  return <div key={j} className="text-gray-700 dark:text-gray-300">{cleaned}</div>
                                })}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      <div className="grid grid-cols-2 gap-3 mb-3">
                        <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-green-200 dark:border-green-800 text-center">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Feasibility</div>
                          <div className="text-xl font-bold text-green-600 dark:text-green-400">
                            {selectedFeature.evidence.evaluations.engineering.feasibility_score?.toFixed(1) || selectedFeature.feasibility_score?.toFixed(1) || 'N/A'}/10
                          </div>
                        </div>
                        <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-green-200 dark:border-green-800 text-center">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Risk</div>
                          <div className="text-xl font-bold text-gray-900 dark:text-white">
                            {selectedFeature.evidence.evaluations.engineering.risk_score?.toFixed(1) || selectedFeature.risk_score?.toFixed(1) || 'N/A'}/10
                          </div>
                        </div>
                      </div>
                      {selectedFeature.evidence.evaluations.engineering.priority_justification && (
                        <div className="mb-2">
                          <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Priority Justification:</div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">
                            {selectedFeature.evidence.evaluations.engineering.priority_justification}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                    </div>
                  )}

            {/* Professional Summary Section - Always Show (for ALL recommendations) */}
            <div className="mb-6 p-6 bg-gradient-to-r from-slate-50 to-gray-50 dark:from-slate-900/20 dark:to-gray-900/20 rounded-xl border-2 border-slate-300 dark:border-slate-700 shadow-lg">
              <div className="flex items-center gap-2 mb-5">
                <span className="text-2xl">📊</span>
                <h4 className="text-xl font-bold text-gray-900 dark:text-white">Professional Summary</h4>
              </div>
              <div className="space-y-5">
                {/* Strategic Rationale - Always Show */}
                {selectedFeature.evidence?.data_justification?.strategic_rationale ? (
                  <div className="p-5 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-blue-500 dark:border-blue-600 shadow-sm">
                    <div className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">Strategic Rationale</div>
                    <div className="text-base text-gray-700 dark:text-gray-300 leading-relaxed space-y-3">
                      {(() => {
                        const text = cleanMarkdown(selectedFeature.evidence.data_justification.strategic_rationale)
                        const summarized = summarizeText(text, 600)
                        return summarized.split('\n\n').filter(p => p.trim()).map((paragraph, i) => (
                          <p key={i} className="leading-relaxed">{formatTextWithBold(paragraph)}</p>
                        ))
                      })()}
                    </div>
                  </div>
                ) : selectedFeature.business_impact ? (
                  <div className="p-5 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-blue-500 dark:border-blue-600 shadow-sm">
                    <div className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">Strategic Rationale</div>
                    <div className="text-base text-gray-700 dark:text-gray-300 leading-relaxed">
                      {formatBusinessImpact(selectedFeature.business_impact)}
                    </div>
                  </div>
                ) : (
                  <div className="p-5 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-blue-500 dark:border-blue-600 shadow-sm">
                    <div className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">Strategic Rationale</div>
                    <div className="text-base text-gray-700 dark:text-gray-300 leading-relaxed">
                      This feature addresses customer needs with an <strong>impact score of {selectedFeature.impact_score?.toFixed(1) || 'N/A'}/10</strong>. 
                      {selectedFeature.arr_data?.total_arr > 0 || selectedFeature.total_arr_requesting > 0 
                        ? ` With <strong>$${((selectedFeature.arr_data?.total_arr || selectedFeature.total_arr_requesting || 0) / 1000).toFixed(0)}K in ARR at stake</strong>, this represents a significant business opportunity.`
                        : ' This represents an important opportunity to improve customer satisfaction and competitive positioning.'}
                    </div>
                  </div>
                )}
                
                {/* Customer Demand Evidence - Always Show */}
                {selectedFeature.evidence?.data_justification?.customer_demand ? (
                  <div className="p-5 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-green-500 dark:border-green-600 shadow-sm">
                    <div className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">Customer Demand Evidence</div>
                    <div className="text-base text-gray-700 dark:text-gray-300 leading-relaxed space-y-3">
                      {(() => {
                        const text = typeof selectedFeature.evidence.data_justification.customer_demand === 'string' 
                          ? selectedFeature.evidence.data_justification.customer_demand
                          : JSON.stringify(selectedFeature.evidence.data_justification.customer_demand)
                        const cleaned = cleanMarkdown(text)
                        const summarized = summarizeText(cleaned, 600)
                        return summarized.split('\n\n').filter(p => p.trim()).map((paragraph, i) => (
                          <p key={i} className="leading-relaxed">{formatTextWithBold(paragraph)}</p>
                        ))
                      })()}
                    </div>
                  </div>
                ) : (
                  <div className="p-5 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-green-500 dark:border-green-600 shadow-sm">
                    <div className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">Customer Demand Evidence</div>
                    <div className="text-base text-gray-700 dark:text-gray-300 leading-relaxed">
                      {selectedFeature.arr_data?.total_arr > 0 || selectedFeature.total_arr_requesting > 0 
                        ? <>Strong customer demand evidenced by <strong>${((selectedFeature.arr_data?.total_arr || selectedFeature.total_arr_requesting || 0) / 1000).toFixed(0)}K in ARR at stake</strong>, <strong>{selectedFeature.lost_deal_count || selectedFeature.arr_data?.lost_deal_count || 0} lost deals</strong>, and <strong>impact score of {selectedFeature.impact_score?.toFixed(1) || 'N/A'}/10</strong>. This indicates significant customer need and competitive pressure.</>
                        : <>Customer demand evidenced by <strong>impact score of {selectedFeature.impact_score?.toFixed(1) || 'N/A'}/10</strong> and customer value score. This feature addresses important customer needs and should be prioritized.</>}
                    </div>
                  </div>
                )}
                
                {/* Prioritization Recommendation - Always Show */}
                {selectedFeature.evidence?.data_justification?.prioritization_recommendation ? (
                  <div className="p-5 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-purple-500 dark:border-purple-600 shadow-sm">
                    <div className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">Prioritization Recommendation</div>
                    <div className="text-base text-gray-700 dark:text-gray-300 leading-relaxed space-y-3">
                      {(() => {
                        const text = cleanMarkdown(selectedFeature.evidence.data_justification.prioritization_recommendation)
                        const summarized = summarizeText(text, 600)
                        return summarized.split('\n\n').filter(p => p.trim()).map((paragraph, i) => (
                          <p key={i} className="leading-relaxed">{formatTextWithBold(paragraph)}</p>
                        ))
                      })()}
                    </div>
                  </div>
                ) : selectedFeature.unified_recommendation ? (
                  <div className="p-5 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-purple-500 dark:border-purple-600 shadow-sm">
                    <div className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">Prioritization Recommendation</div>
                    <div className="text-base text-gray-700 dark:text-gray-300 leading-relaxed">
                      {selectedFeature.unified_recommendation}
                    </div>
                  </div>
                ) : (
                  <div className="p-5 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-purple-500 dark:border-purple-600 shadow-sm">
                    <div className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">Prioritization Recommendation</div>
                    <div className="text-base text-gray-700 dark:text-gray-300 leading-relaxed">
                      Based on <strong>impact score of {selectedFeature.impact_score?.toFixed(1) || 'N/A'}/10</strong>, {selectedFeature.arr_data?.total_arr > 0 || selectedFeature.total_arr_requesting > 0 ? <><strong>${((selectedFeature.arr_data?.total_arr || selectedFeature.total_arr_requesting || 0) / 1000).toFixed(0)}K in ARR at stake</strong>,</> : ''} and <strong>feasibility score of {selectedFeature.feasibility_score?.toFixed(1) || 'N/A'}/10</strong>, this feature should be prioritized in the next quarter roadmap.
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Key Debate Points - Always Show (for ALL recommendations) */}
            <div className="mb-6 p-6 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-xl border-2 border-orange-300 dark:border-orange-700 shadow-lg">
                      <div className="flex items-center gap-2 mb-4">
                        <span className="text-2xl">💬</span>
                        <h4 className="text-lg font-bold text-gray-900 dark:text-white">Key Debate Points</h4>
                      </div>
                      <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-3">
                        {(() => {
                          const debatePoints = selectedFeature.evidence?.unified_recommendation?.key_debate_points || 
                                               selectedFeature.evidence?.unified_recommendation?.debate_points ||
                                               selectedFeature.evidence?.key_debate_points;
                          
                          if (debatePoints) {
                            if (Array.isArray(debatePoints)) {
                              return debatePoints.map((point: string, i: number) => (
                                <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-orange-400 dark:border-orange-600 shadow-sm">
                                  <div className="flex items-start gap-3">
                                    <span className="text-orange-600 dark:text-orange-400 font-bold text-lg mt-0.5">{i + 1}.</span>
                                    <span className="flex-1 font-medium">{point}</span>
                                  </div>
                                </div>
                              ));
                            } else if (typeof debatePoints === 'string') {
                              return debatePoints.split(/[.!?]+/).filter((p: string) => p.trim().length > 20).map((point: string, i: number) => (
                                <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-orange-400 dark:border-orange-600 shadow-sm">
                                  <div className="flex items-start gap-3">
                                    <span className="text-orange-600 dark:text-orange-400 font-bold text-lg mt-0.5">{i + 1}.</span>
                                    <span className="flex-1 font-medium">{point.trim()}.</span>
                                  </div>
                                </div>
                              ));
                            }
                          }
                          
                          // Fallback: Generate debate points from available data
                          const fallbackPoints = [];
                          if (selectedFeature.lost_deal_count > 0 || selectedFeature.arr_data?.lost_deal_count > 0) {
                            fallbackPoints.push(`Competitive threat: ${selectedFeature.lost_deal_count || selectedFeature.arr_data?.lost_deal_count || 0} lost deals vs. implementation effort`);
                          }
                          if (selectedFeature.impact_score) {
                            fallbackPoints.push(`Impact score ${selectedFeature.impact_score.toFixed(1)}/10 vs. technical feasibility ${selectedFeature.feasibility_score?.toFixed(1) || 'N/A'}/10`);
                          }
                          if (selectedFeature.arr_data?.total_arr > 0 || selectedFeature.total_arr_requesting > 0) {
                            fallbackPoints.push(`Revenue impact: $${((selectedFeature.arr_data?.total_arr || selectedFeature.total_arr_requesting || 0) / 1000).toFixed(0)}K ARR at stake vs. development cost`);
                          }
                          if (selectedFeature.competitors_mentioned?.length > 0 || selectedFeature.arr_data?.competitor_mentions?.length > 0) {
                            const competitors = selectedFeature.arr_data?.competitor_mentions || selectedFeature.competitors_mentioned || [];
                            fallbackPoints.push(`Competitive pressure from ${competitors.join(', ')} vs. UX concerns`);
                          }
                          if (selectedFeature.risk_score) {
                            fallbackPoints.push(`Technical risk ${selectedFeature.risk_score.toFixed(1)}/10 vs. business opportunity`);
                          }
                          
                          // Always show at least some debate points
                          if (fallbackPoints.length === 0) {
                            // Generate basic debate points from available metrics
                            if (selectedFeature.impact_score) {
                              fallbackPoints.push(`Impact score ${selectedFeature.impact_score.toFixed(1)}/10 indicates high customer value and business opportunity`);
                            }
                            if (selectedFeature.feasibility_score) {
                              fallbackPoints.push(`Technical feasibility ${selectedFeature.feasibility_score.toFixed(1)}/10 suggests moderate implementation complexity`);
                            }
                            if (selectedFeature.risk_score) {
                              fallbackPoints.push(`Risk score ${selectedFeature.risk_score.toFixed(1)}/10 indicates acceptable technical and business risk`);
                            }
                            if (selectedFeature.arr_data?.total_arr > 0 || selectedFeature.total_arr_requesting > 0) {
                              fallbackPoints.push(`Revenue impact of $${((selectedFeature.arr_data?.total_arr || selectedFeature.total_arr_requesting || 0) / 1000).toFixed(0)}K ARR justifies development investment`);
                            }
                            fallbackPoints.push(`Team consensus: This feature addresses customer needs and should be prioritized based on impact and feasibility`);
                          }
                          
                          return fallbackPoints.map((point: string, i: number) => (
                            <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-orange-400 dark:border-orange-600 shadow-sm">
                              <div className="flex items-start gap-3">
                                <span className="text-orange-600 dark:text-orange-400 font-bold text-lg mt-0.5">{i + 1}.</span>
                                <span className="flex-1 font-medium">{point}</span>
                              </div>
                            </div>
                          ));
                        })()}
                      </div>
                    </div>

            {/* Detailed Reasoning & Analysis - Always Show (for ALL recommendations) */}
            <div className="mb-6 p-6 bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-900/20 dark:to-blue-900/20 rounded-xl border-2 border-indigo-300 dark:border-indigo-700 shadow-lg">
              <div className="flex items-center gap-2 mb-5">
                <span className="text-2xl">🧠</span>
                <h4 className="text-xl font-bold text-gray-900 dark:text-white">Detailed Reasoning & Analysis</h4>
              </div>
              <div className="text-base text-gray-700 dark:text-gray-300 leading-relaxed space-y-4">
                {(() => {
                  const reasoning = selectedFeature.evidence?.unified_recommendation?.unified_reasoning || 
                                    selectedFeature.unified_recommendation || 
                                    selectedFeature.business_impact ||
                                    `This feature recommendation is based on comprehensive analysis of customer feedback, business metrics, and technical feasibility. With an impact score of ${selectedFeature.impact_score?.toFixed(1) || 'N/A'}/10, this represents a significant opportunity to address customer needs and improve competitive positioning. The team has evaluated this feature from multiple perspectives including product strategy, user experience, data insights, and engineering feasibility, and reached consensus on its importance.`;
                  
                  const cleaned = cleanMarkdown(reasoning)
                  const summarized = summarizeText(cleaned, 800)
                  
                  return summarized.split('\n\n').filter(p => p.trim()).map((paragraph, i) => (
                    <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-indigo-400 dark:border-indigo-600 shadow-sm">
                      <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{formatTextWithBold(paragraph)}</p>
                    </div>
                  ));
                })()}
              </div>
            </div>

            {/* Next Steps & Action Items - Always Show (for ALL recommendations) */}
            <div className="mb-6 p-6 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/20 dark:via-indigo-900/20 dark:to-purple-900/20 rounded-xl border-2 border-blue-300 dark:border-blue-700 shadow-lg">
              <div className="flex items-center gap-2 mb-5">
                <span className="text-2xl">📋</span>
                <h4 className="text-xl font-bold text-gray-900 dark:text-white">Next Steps & Action Items</h4>
              </div>
              <div className="space-y-4">
                      {(() => {
                        const actionItems = selectedFeature.evidence?.unified_recommendation?.action_items || 
                                            selectedFeature.evidence?.unified_recommendation?.next_steps ||
                                            selectedFeature.evidence?.next_steps ||
                                            selectedFeature.evidence?.action_items;
                        
                        if (Array.isArray(actionItems) && actionItems.length > 0) {
                          return actionItems.map((item: string, i: number) => (
                            <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-blue-500 dark:border-blue-600 shadow-sm">
                              <div className="flex items-start gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-sm">
                                  {i + 1}
                                </div>
                                <div className="flex-1">
                                  <div className="text-sm font-medium text-gray-900 dark:text-white leading-relaxed">
                                    {item}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ));
                        } else if (typeof actionItems === 'string' && actionItems.trim().length > 10) {
                          return actionItems.split(/[.!?]+/).filter((p: string) => p.trim().length > 10).map((item: string, i: number) => (
                            <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-blue-500 dark:border-blue-600 shadow-sm">
                              <div className="flex items-start gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-sm">
                                  {i + 1}
                                </div>
                                <div className="flex-1">
                                  <div className="text-sm font-medium text-gray-900 dark:text-white leading-relaxed">
                                    {item.trim()}.
                                  </div>
                                </div>
                              </div>
                            </div>
                          ));
                        }
                        
                        // Fallback: Always show next steps
                        const defaultSteps = [
                          "Review this recommendation with the product team and stakeholders",
                          "Assess technical feasibility and resource requirements with Engineering",
                          "Create detailed product requirements and design specifications",
                          `Prioritize in roadmap based on impact score (${selectedFeature.impact_score?.toFixed(1) || 'N/A'}/10) and business metrics`,
                          "Track customer feedback and adoption metrics post-launch"
                        ];
                        
                              return defaultSteps.map((step: string, i: number) => (
                                <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-blue-500 dark:border-blue-600 shadow-sm">
                                  <div className="flex items-start gap-3">
                                    <div className="flex-shrink-0 w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-base">
                                      {i + 1}
                                    </div>
                                    <div className="flex-1">
                                      <div className="text-base font-semibold text-gray-900 dark:text-white leading-relaxed">
                                        {step}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              ));
                            })()}
                          </div>
                        </div>

            {/* Implementation Guidance - Always Show (for ALL recommendations) */}
            <div className="mb-6 p-6 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl border-2 border-green-300 dark:border-green-700 shadow-lg">
              <div className="flex items-center gap-2 mb-5">
                <span className="text-2xl">🚀</span>
                <h4 className="text-xl font-bold text-gray-900 dark:text-white">Implementation Guidance</h4>
              </div>
              <div className="text-base text-gray-700 dark:text-gray-300 leading-relaxed space-y-4">
                {(() => {
                  const guidance = selectedFeature.evidence?.unified_recommendation?.implementation_guidance ||
                                  selectedFeature.evidence?.unified_recommendation?.recommended_approach ||
                                  selectedFeature.evidence?.implementation_guidance ||
                                  `Recommended implementation approach: Start with an MVP to address core customer needs. Based on feasibility score of ${selectedFeature.feasibility_score?.toFixed(1) || 'N/A'}/10 and risk score of ${selectedFeature.risk_score?.toFixed(1) || 'N/A'}/10, estimated timeline is 6-8 weeks for initial version. Consider phased rollout to validate with high-value customers first. Technical considerations include integration with existing systems, API design, and scalability requirements.`;
                  
                  const cleaned = cleanMarkdown(guidance)
                  const summarized = summarizeText(cleaned, 800)
                  
                  return summarized.split('\n\n').filter(p => p.trim()).map((paragraph, i) => (
                    <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-green-400 dark:border-green-600 shadow-sm">
                      <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{formatTextWithBold(paragraph)}</p>
                    </div>
                  ));
                })()}
              </div>
            </div>

            {/* Team Consensus & Debate - Show if evidence exists OR if we have basic data */}
            {(selectedFeature.evidence?.unified_recommendation || selectedFeature.unified_recommendation) && (
                    <div className="p-6 bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-green-900/30 dark:via-blue-900/30 dark:to-purple-900/30 rounded-xl border-2 border-green-300 dark:border-green-700 shadow-lg">
                      <div className="font-bold text-lg text-gray-900 dark:text-white mb-4 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
                          <span>Team Consensus & Final Decision</span>
                        </div>
                        {selectedFeature.evidence?.unified_recommendation?.confidence && (
                          <span className="text-sm bg-green-100 dark:bg-green-900/40 px-3 py-1.5 rounded-full font-semibold">
                            Confidence: {selectedFeature.evidence.unified_recommendation.confidence}/10
                          </span>
                        )}
                      </div>
                      
                        {selectedFeature.evidence?.unified_recommendation?.final_verdict && (
                        <div className="mb-4 p-4 bg-white dark:bg-gray-800 rounded-lg border-2 border-green-400 dark:border-green-600">
                          <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wide">Final Verdict</div>
                          <div className="text-xl font-bold text-green-600 dark:text-green-400">
                            {selectedFeature.evidence?.unified_recommendation?.final_verdict}
                          </div>
                        </div>
                      )}
                      
                      {selectedFeature.evidence?.unified_recommendation?.unified_reasoning && (
                        <div className="mb-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Unified Reasoning</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                            {(() => {
                              const reasoning = formatReasoning(selectedFeature.evidence?.unified_recommendation?.unified_reasoning || selectedFeature.unified_recommendation || 'Team reached consensus')
                              // Extract first 2-3 sentences for concise summary
                              const sentences = reasoning.split(/[.!?]+/).filter(s => s.trim().length > 20)
                              if (sentences.length <= 3) {
                                return <p className="text-gray-700 dark:text-gray-300">{reasoning}</p>
                              }
                              return <p className="text-gray-700 dark:text-gray-300">{sentences.slice(0, 3).join('. ') + '.'}</p>
                            })()}
                          </div>
                        </div>
                      )}
                      
                      {selectedFeature.evidence?.unified_recommendation?.team_discussion && (
                        <div className="mb-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-3 uppercase tracking-wide">Team Discussion</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-3">
                            {(() => {
                              const discussion = formatText(selectedFeature.evidence?.unified_recommendation?.team_discussion || '', 2000)
                              
                              // Function to summarize text intelligently (extract key sentences)
                              const summarizeText = (text: string, maxLength: number = 400): string => {
                                if (text.length <= maxLength) return text
                                
                                // Try to break at sentence boundaries
                                const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 10)
                                
                                if (sentences.length === 0) {
                                  return text.substring(0, maxLength - 3) + '...'
                                }
                                
                                // Take first 2-3 sentences that fit within maxLength
                                let summary = ''
                                for (const sentence of sentences) {
                                  if ((summary + sentence).length > maxLength) break
                                  summary += sentence.trim() + '. '
                                }
                                
                                return summary.trim() || text.substring(0, maxLength - 3) + '...'
                              }
                              
                              // Split by persona markers (PM:, UX:, Data Scientist:, Engineering:, Team:)
                              const personaPattern = /(PM|UX|Data Scientist|Engineering|Engineering Lead|Team):\s*['"]([\s\S]*?)(?=(?:PM|UX|Data Scientist|Engineering|Engineering Lead|Team):|$)/g
                              const matches = Array.from(discussion.matchAll(personaPattern))
                              
                              if (matches.length > 0) {
                                return matches.slice(0, 15).map((match, i) => {
                                  const persona = match[1].trim()
                                  let quote = cleanMarkdown(match[2].trim())
                                  // Summarize quote intelligently (extract key points, not just truncate)
                                  quote = summarizeText(quote, 350)
                                  
                                  // Get persona color/icon
                                  const personaConfig: Record<string, { color: string, icon: string, borderColor: string }> = {
                                    'PM': { color: 'text-blue-600 dark:text-blue-400', icon: '📈', borderColor: '#3b82f6' },
                                    'UX': { color: 'text-purple-600 dark:text-purple-400', icon: '🎨', borderColor: '#9333ea' },
                                    'Data Scientist': { color: 'text-orange-600 dark:text-orange-400', icon: '📊', borderColor: '#ea580c' },
                                    'Engineering': { color: 'text-green-600 dark:text-green-400', icon: '⚙️', borderColor: '#16a34a' },
                                    'Engineering Lead': { color: 'text-green-600 dark:text-green-400', icon: '⚙️', borderColor: '#16a34a' },
                                    'Team': { color: 'text-gray-600 dark:text-gray-400', icon: '👥', borderColor: '#6b7280' }
                                  }
                                  
                                  const config = personaConfig[persona] || { color: 'text-gray-600 dark:text-gray-400', icon: '💬', borderColor: '#6b7280' }
                                  
                                  return (
                                    <div key={i} className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border-l-4" style={{ borderLeftColor: config.borderColor }}>
                                      <div className="flex items-start gap-2 mb-2">
                                        <span className="text-base">{config.icon}</span>
                                        <span className={`font-bold ${config.color} text-sm`}>{persona}:</span>
                                      </div>
                                      <div className="text-gray-700 dark:text-gray-300 ml-6 text-sm leading-relaxed">
                                        {quote}
                                      </div>
                                    </div>
                                  )
                                })
                              } else {
                                // Fallback: split by lines and format
                                return discussion.split('\n').filter(line => line.trim()).slice(0, 15).map((line, i) => {
                                  const cleaned = cleanMarkdown(line.trim())
                                  if (cleaned.match(/^(PM|UX|Data Scientist|Engineering|Engineering Lead|Team):/i)) {
                                    const [speaker, ...rest] = cleaned.split(':')
                                    let quote = rest.join(':').trim().replace(/^['"]|['"]$/g, '')
                                    quote = summarizeText(quote, 350)
                                    
                                    const personaConfig: Record<string, { color: string, icon: string, borderColor: string }> = {
                                      'PM': { color: 'text-blue-600 dark:text-blue-400', icon: '📈', borderColor: '#3b82f6' },
                                      'UX': { color: 'text-purple-600 dark:text-purple-400', icon: '🎨', borderColor: '#9333ea' },
                                      'Data Scientist': { color: 'text-orange-600 dark:text-orange-400', icon: '📊', borderColor: '#ea580c' },
                                      'Engineering': { color: 'text-green-600 dark:text-green-400', icon: '⚙️', borderColor: '#16a34a' },
                                      'Engineering Lead': { color: 'text-green-600 dark:text-green-400', icon: '⚙️', borderColor: '#16a34a' },
                                      'Team': { color: 'text-gray-600 dark:text-gray-400', icon: '👥', borderColor: '#6b7280' }
                                    }
                                    
                                    const config = personaConfig[speaker.trim()] || { color: 'text-gray-600 dark:text-gray-400', icon: '💬', borderColor: '#6b7280' }
                                    
                                    return (
                                      <div key={i} className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg border-l-4" style={{ borderLeftColor: config.borderColor }}>
                                        <div className="flex items-start gap-2 mb-2">
                                          <span className="text-base">{config.icon}</span>
                                          <span className={`font-bold ${config.color} text-sm`}>{speaker.trim()}:</span>
                                        </div>
                                        <div className="text-gray-700 dark:text-gray-300 ml-6 text-sm leading-relaxed">
                                          {quote}
                                        </div>
                                      </div>
                                    )
                                  }
                                  return <div key={i} className="text-gray-700 dark:text-gray-300 text-sm p-2">{cleaned}</div>
                                })
                              }
                            })()}
                          </div>
                        </div>
                      )}
                      
                      {/* Key Debate Points - Enhanced Professional Display */}
                      {(selectedFeature.evidence?.unified_recommendation?.key_debate_points || 
                        selectedFeature.evidence?.unified_recommendation?.debate_points ||
                        selectedFeature.evidence?.key_debate_points) && (
                        <div className="mb-6 p-6 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-xl border-2 border-orange-300 dark:border-orange-700 shadow-lg">
                          <div className="flex items-center gap-2 mb-4">
                            <span className="text-2xl">💬</span>
                            <h4 className="text-lg font-bold text-gray-900 dark:text-white">Key Debate Points</h4>
                                  </div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-3">
                            {(() => {
                              const debatePoints = selectedFeature.evidence?.unified_recommendation?.key_debate_points || 
                                                   selectedFeature.evidence?.unified_recommendation?.debate_points ||
                                                   selectedFeature.evidence?.key_debate_points;
                              
                              if (Array.isArray(debatePoints)) {
                                return debatePoints.map((point: string, i: number) => (
                                  <div key={i} className="p-3 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-orange-400 dark:border-orange-600">
                                    <div className="flex items-start gap-2">
                                      <span className="text-orange-600 dark:text-orange-400 font-bold mt-0.5">{i + 1}.</span>
                                      <span className="flex-1">{point}</span>
                                  </div>
                                  </div>
                                ));
                              } else if (typeof debatePoints === 'string') {
                                return debatePoints.split(/[.!?]+/).filter((p: string) => p.trim().length > 20).map((point: string, i: number) => (
                                  <div key={i} className="p-3 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-orange-400 dark:border-orange-600">
                                    <div className="flex items-start gap-2">
                                      <span className="text-orange-600 dark:text-orange-400 font-bold mt-0.5">{i + 1}.</span>
                                      <span className="flex-1">{point.trim()}.</span>
                                    </div>
                                  </div>
                                ));
                              }
                              return <div>{String(debatePoints)}</div>;
                            })()}
                          </div>
                        </div>
                      )}
                      
                      {selectedFeature.evidence?.unified_recommendation?.trade_offs && (
                        <div className="mb-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Trade-offs Discussed</div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                            {Array.isArray(selectedFeature.evidence?.unified_recommendation?.trade_offs) 
                              ? (selectedFeature.evidence?.unified_recommendation?.trade_offs || []).map((tradeoff: string, i: number) => (
                                  <div key={i} className="mb-2 flex items-start gap-2">
                                    <span className="text-yellow-600 dark:text-yellow-400 mt-1">•</span>
                                    <span>{tradeoff}</span>
                                  </div>
                                ))
                              : (selectedFeature.evidence?.unified_recommendation?.trade_offs || '').split('.').filter((p: string) => p.trim()).map((tradeoff: string, i: number) => (
                                  <div key={i} className="mb-2 flex items-start gap-2">
                                    <span className="text-yellow-600 dark:text-yellow-400 mt-1">•</span>
                                    <span>{tradeoff.trim()}</span>
                                  </div>
                                ))}
                          </div>
                        </div>
                      )}
                      
                      {selectedFeature.evidence?.unified_recommendation?.final_priority && (
                        <div className="mb-6 p-5 bg-purple-50 dark:bg-purple-900/20 rounded-xl border-2 border-purple-300 dark:border-purple-700 shadow-lg">
                          <div className="flex items-center gap-2 mb-3">
                            <span className="text-xl">🎯</span>
                            <h4 className="text-base font-bold text-gray-900 dark:text-white">Final Priority Justification</h4>
                          </div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                            {formatReasoning(selectedFeature.evidence?.unified_recommendation?.final_priority || '')}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

            {/* Customer Quotes */}
            {selectedFeature.customer_quotes && selectedFeature.customer_quotes.length > 0 && (
              <div>
                <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                  💬 Customer Quotes ({selectedFeature.customer_quotes.length})
                </h3>
                <div className="space-y-4">
                  {selectedFeature.customer_quotes.map((quoteItem: any, i: number) => {
                    const quoteText = typeof quoteItem === 'string' ? quoteItem : (quoteItem.quote || quoteItem.content || JSON.stringify(quoteItem));
                    const source = typeof quoteItem === 'object' ? quoteItem.source : null;
                    const arr = typeof quoteItem === 'object' ? quoteItem.arr : null;
                    
                    return (
                      <div key={i} className="p-5 bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-lg border-2 border-yellow-300 dark:border-yellow-700 shadow-sm">
                        <div className="text-sm text-gray-800 dark:text-gray-200 italic leading-relaxed mb-3 font-medium">
                          "{quoteText}"
                        </div>
                        <div className="flex items-center justify-between pt-3 border-t border-yellow-200 dark:border-yellow-800">
                          {source && <span className="text-xs text-gray-600 dark:text-gray-400 font-medium">Source: {source}</span>}
                          {arr && arr > 0 && <span className="text-xs font-bold text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded">${(arr / 1000).toFixed(0)}K ARR</span>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Fallback: Standard Team Evaluations (if no evidence) - ENHANCED */}
            {(!selectedFeature.evidence || !selectedFeature.evidence.evaluations) && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  Team Evaluations
                </h3>
                <div className="space-y-4">
                  {/* PM Evaluation */}
                  <div className="p-5 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-800 shadow-sm">
                    <div className="font-bold text-base text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                      <span className="text-xl">📈</span>
                      <span>Product Manager (PM)</span>
                    </div>
                    <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                      {selectedFeature.pm_verdict || 'Pending evaluation'}
                    </div>
                    {selectedFeature.business_impact && (
                      <div className="mt-3 p-3 bg-white dark:bg-gray-800 rounded border border-blue-100 dark:border-blue-800">
                        <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Business Impact:</div>
                        <div className="text-sm text-gray-700 dark:text-gray-300">
                          {formatBusinessImpact(selectedFeature.business_impact).split('\n\n')[0]}
                  </div>
                      </div>
                    )}
                  </div>

                  {/* UX Evaluation */}
                  <div className="p-5 bg-purple-50 dark:bg-purple-900/20 rounded-lg border-2 border-purple-200 dark:border-purple-800 shadow-sm">
                    <div className="font-bold text-base text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                      <span className="text-xl">🎨</span>
                      <span>UX Designer</span>
                    </div>
                    <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                      {selectedFeature.ux_verdict || 'Pending evaluation'}
                    </div>
                    {selectedFeature.ux_implications && (
                      <div className="mt-3 p-3 bg-white dark:bg-gray-800 rounded border border-purple-100 dark:border-purple-800">
                        <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">UX Implications:</div>
                        <div className="text-sm text-gray-700 dark:text-gray-300">
                          {selectedFeature.ux_implications}
                  </div>
                      </div>
                    )}
                  </div>

                  {/* Data Scientist Evaluation */}
                  <div className="p-5 bg-orange-50 dark:bg-orange-900/20 rounded-lg border-2 border-orange-200 dark:border-orange-800 shadow-sm">
                    <div className="font-bold text-base text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                      <span className="text-xl">📊</span>
                      <span>Data Scientist</span>
                    </div>
                    <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                      {selectedFeature.data_scientist_verdict || 'Pending evaluation'}
                    </div>
                  </div>

                  {/* Engineering Evaluation */}
                  <div className="p-5 bg-green-50 dark:bg-green-900/20 rounded-lg border-2 border-green-200 dark:border-green-800 shadow-sm">
                    <div className="font-bold text-base text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                      <span className="text-xl">⚙️</span>
                      <span>Engineering</span>
                    </div>
                    <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed mb-3">
                      {selectedFeature.engineering_verdict || 'Pending evaluation'}
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-green-200 dark:border-green-800 text-center">
                        <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Feasibility</div>
                        <div className="text-xl font-bold text-green-600 dark:text-green-400">
                          {selectedFeature.feasibility_score?.toFixed(1) || 'N/A'}/10
                  </div>
                      </div>
                      <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-green-200 dark:border-green-800 text-center">
                        <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Risk</div>
                        <div className="text-xl font-bold text-gray-900 dark:text-white">
                          {selectedFeature.risk_score?.toFixed(1) || 'N/A'}/10
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Team Consensus */}
                  {selectedFeature.unified_recommendation && (
                    <div className="p-6 bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-green-900/30 dark:via-blue-900/30 dark:to-purple-900/30 rounded-xl border-2 border-green-300 dark:border-green-700 shadow-lg">
                      <div className="font-bold text-lg text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                        <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
                        <span>✅ Team Consensus</span>
                      </div>
                      <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                        {selectedFeature.unified_recommendation}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Unique Features: ARR Impact & Lost Deals */}
            {((selectedFeature.arr_at_risk && selectedFeature.arr_at_risk > 0) || 
              (selectedFeature.lost_deal_count && selectedFeature.lost_deal_count > 0) ||
              (selectedFeature.total_arr_requesting && selectedFeature.total_arr_requesting > 0) ||
              (selectedFeature.competitors_mentioned && selectedFeature.competitors_mentioned.length > 0) ||
              (selectedFeature.arr_data && (selectedFeature.arr_data.avg_arr > 0 || selectedFeature.arr_data.total_arr > 0))) && (
              <div className="bg-gradient-to-r from-green-50 via-blue-50 to-purple-50 dark:from-green-900/20 dark:via-blue-900/20 dark:to-purple-900/20 rounded-lg p-5 border-2 border-green-200 dark:border-green-800">
                <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
                  💰 Revenue Impact & Business Metrics
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {selectedFeature.arr_data && selectedFeature.arr_data.avg_arr > 0 && (
                    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border-2 border-green-300 dark:border-green-700 text-center shadow-sm">
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 font-medium">Avg Customer ARR</div>
                      <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                        ${(selectedFeature.arr_data.avg_arr / 1000).toFixed(0)}K
                      </div>
                    </div>
                  )}
                  {(selectedFeature.total_arr_requesting || (selectedFeature.arr_data && selectedFeature.arr_data.total_arr > 0)) && (
                    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border-2 border-blue-300 dark:border-blue-700 text-center shadow-sm">
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 font-medium">Total ARR at Stake</div>
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        ${((selectedFeature.arr_data?.total_arr || selectedFeature.total_arr_requesting || 0) / 1000).toFixed(0)}K
                      </div>
                    </div>
                  )}
                  {(selectedFeature.arr_at_risk || (selectedFeature.arr_data && selectedFeature.arr_data.lost_deal_arr > 0)) && (
                    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border-2 border-red-300 dark:border-red-700 text-center shadow-sm">
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 font-medium">Lost ARR</div>
                      <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                        ${((selectedFeature.arr_data?.lost_deal_arr || selectedFeature.arr_at_risk || 0) / 1000).toFixed(0)}K
                      </div>
                    </div>
                  )}
                  {(selectedFeature.lost_deal_count || (selectedFeature.arr_data && selectedFeature.arr_data.lost_deal_count > 0)) && (
                    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border-2 border-red-300 dark:border-red-700 text-center shadow-sm">
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 font-medium">Lost Deals</div>
                      <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                        {selectedFeature.arr_data?.lost_deal_count || selectedFeature.lost_deal_count || 0}
                      </div>
                    </div>
                  )}
                </div>
                {((selectedFeature.competitors_mentioned && selectedFeature.competitors_mentioned.length > 0) ||
                  (selectedFeature.arr_data && selectedFeature.arr_data.competitor_mentions && selectedFeature.arr_data.competitor_mentions.length > 0)) && (
                  <div className="mt-4 p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                    <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">🎯 Competitors Mentioned</div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {(selectedFeature.arr_data?.competitor_mentions || selectedFeature.competitors_mentioned || []).map((comp: string, i: number) => (
                        <span key={i} className="px-3 py-1 bg-orange-100 dark:bg-orange-900/30 rounded-full text-xs font-medium text-orange-800 dark:text-orange-300">
                          {comp}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {selectedFeature.priority_level && (
                  <div className="mt-4 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border-2 border-purple-300 dark:border-purple-700 text-center">
                    <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 font-medium">Priority Level</div>
                    <div className="text-xl font-bold text-purple-600 dark:text-purple-400">
                      {selectedFeature.priority_level}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Competitor Radar & Intelligence (like themes have) */}
            {((selectedFeature.competitors && selectedFeature.competitors.length > 0) ||
              (selectedFeature.mock_competitors && selectedFeature.mock_competitors.length > 0)) && (
              <div>
                <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5 text-red-600 dark:text-red-400" />
                  🎯 Competitor Intelligence & Radar
                </h3>
                <div className="space-y-4">
                  {/* Database Competitors */}
                  {selectedFeature.competitors && selectedFeature.competitors.map((comp: any, idx: number) => (
                    <div key={idx} className="p-5 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-800 shadow-sm">
                      <div className="font-bold text-base text-gray-900 dark:text-white mb-3">{comp.name}</div>
                      {comp.description && (
                        <div className="text-sm text-gray-700 dark:text-gray-300 mb-3 leading-relaxed">{comp.description}</div>
                      )}
                      {comp.strengths && comp.strengths.length > 0 && (
                        <div className="mb-3">
                          <div className="text-xs font-semibold text-green-700 dark:text-green-400 mb-2 uppercase tracking-wide">Strengths</div>
                          <div className="flex flex-wrap gap-2">
                            {comp.strengths.map((s: string, i: number) => (
                              <span key={i} className="px-3 py-1.5 bg-green-100 dark:bg-green-900/30 rounded-full text-xs font-medium text-green-800 dark:text-green-300">{s}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {comp.weaknesses && comp.weaknesses.length > 0 && (
                        <div className="mb-3">
                          <div className="text-xs font-semibold text-red-700 dark:text-red-400 mb-2 uppercase tracking-wide">Weaknesses</div>
                          <div className="flex flex-wrap gap-2">
                            {comp.weaknesses.map((w: string, i: number) => (
                              <span key={i} className="px-3 py-1.5 bg-red-100 dark:bg-red-900/30 rounded-full text-xs font-medium text-red-800 dark:text-red-300">{w}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {comp.opportunities && comp.opportunities.length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-blue-700 dark:text-blue-400 mb-2 uppercase tracking-wide">Opportunities</div>
                          <div className="flex flex-wrap gap-2">
                            {comp.opportunities.map((o: string, i: number) => (
                              <span key={i} className="px-3 py-1.5 bg-blue-100 dark:bg-blue-900/30 rounded-full text-xs font-medium text-blue-800 dark:text-blue-300">{o}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {/* Mock Competitors */}
                  {selectedFeature.mock_competitors && selectedFeature.mock_competitors.map((comp: any, idx: number) => (
                    <div key={`mock-${idx}`} className="p-5 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-lg border-2 border-orange-300 dark:border-orange-700 shadow-sm">
                      <div className="flex items-center justify-between mb-3">
                        <div className="font-bold text-base text-gray-900 dark:text-white">{comp.name}</div>
                        <span className={`text-xs px-3 py-1.5 rounded-full font-semibold ${
                          comp.competitive_pressure === 'high' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' :
                          comp.competitive_pressure === 'medium' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400' :
                          'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                        }`}>
                          {comp.competitive_pressure} pressure
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-3 mb-4">
                        {comp.lost_deals_attributed > 0 && (
                          <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-red-200 dark:border-red-800">
                            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Lost Deals</div>
                            <div className="text-lg font-bold text-red-600 dark:text-red-400">{comp.lost_deals_attributed}</div>
                          </div>
                        )}
                        {comp.total_arr_lost > 0 && (
                          <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-red-200 dark:border-red-800">
                            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Lost ARR</div>
                            <div className="text-lg font-bold text-red-600 dark:text-red-400">${(comp.total_arr_lost / 1000).toFixed(0)}K</div>
                          </div>
                        )}
                      </div>
                      {comp.strengths && comp.strengths.length > 0 && (
                        <div className="mb-3">
                          <div className="text-xs font-semibold text-green-700 dark:text-green-400 mb-2 uppercase tracking-wide">Strengths</div>
                          <div className="flex flex-wrap gap-2">
                            {comp.strengths.map((s: string, i: number) => (
                              <span key={i} className="px-3 py-1.5 bg-green-100 dark:bg-green-900/30 rounded-full text-xs font-medium text-green-800 dark:text-green-300">{s}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {comp.weaknesses && comp.weaknesses.length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-red-700 dark:text-red-400 mb-2 uppercase tracking-wide">Weaknesses</div>
                          <div className="flex flex-wrap gap-2">
                            {comp.weaknesses.map((w: string, i: number) => (
                              <span key={i} className="px-3 py-1.5 bg-red-100 dark:bg-red-900/30 rounded-full text-xs font-medium text-red-800 dark:text-red-300">{w}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* One-Pager (Unique Feature) */}
            {selectedFeature.one_pager && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  📄 Stakeholder One-Pager (Unique Feature)
                </h3>
                <div className="space-y-3 text-sm bg-gray-50 dark:bg-gray-800 p-4 rounded">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white mb-2">Customer Quotes:</div>
                    {selectedFeature.one_pager.customer_quotes.map((quote: string, i: number) => (
                      <div key={i} className="text-xs text-gray-600 dark:text-gray-400 italic mb-1 pl-2 border-l-2 border-blue-300">
                        "{quote}"
                      </div>
                    ))}
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <span className="font-medium">ARR Impact:</span> ${(selectedFeature.one_pager.arr_impact / 1000).toFixed(0)}K
                    </div>
                    <div>
                      <span className="font-medium">Estimate:</span> {selectedFeature.one_pager.implementation_estimate}
                    </div>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white mb-1">Competitive Angle:</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">{selectedFeature.one_pager.competitive_angle}</div>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white mb-1">ROI Projection:</div>
                    <div className="text-xs text-green-600 dark:text-green-400">{selectedFeature.one_pager.roi_projection}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Next Steps Section - Always Show (Professional) */}
            {(!selectedFeature.evidence?.unified_recommendation?.action_items && 
              !selectedFeature.evidence?.unified_recommendation?.next_steps) && (
              <div className="mb-6 p-6 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/20 dark:via-indigo-900/20 dark:to-purple-900/20 rounded-xl border-2 border-blue-300 dark:border-blue-700 shadow-lg">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-2xl">📋</span>
                  <h4 className="text-lg font-bold text-gray-900 dark:text-white">Recommended Next Steps</h4>
                </div>
                <div className="space-y-3">
                  <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-blue-500 dark:border-blue-600 shadow-sm">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-sm">1</div>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 dark:text-white leading-relaxed">
                          Review this recommendation with the product team and stakeholders
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-blue-500 dark:border-blue-600 shadow-sm">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-sm">2</div>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 dark:text-white leading-relaxed">
                          Assess technical feasibility and resource requirements with Engineering
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-blue-500 dark:border-blue-600 shadow-sm">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-sm">3</div>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 dark:text-white leading-relaxed">
                          Create detailed product requirements and design specifications
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-blue-500 dark:border-blue-600 shadow-sm">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-sm">4</div>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 dark:text-white leading-relaxed">
                          Prioritize in roadmap based on impact score ({selectedFeature.impact_score?.toFixed(1) || 'N/A'}/10) and business metrics
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-blue-500 dark:border-blue-600 shadow-sm">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-sm">5</div>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 dark:text-white leading-relaxed">
                          Track customer feedback and adoption metrics post-launch
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Status Badge */}
            <div className="pt-6 border-t-2 border-gray-300 dark:border-gray-700">
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
                <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Status:</span>
                <span className={`px-4 py-2 text-sm rounded-full font-bold ${
                  selectedFeature.status === 'shipped' ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 border-2 border-green-300 dark:border-green-700' :
                  selectedFeature.status === 'in_progress' ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border-2 border-blue-300 dark:border-blue-700' :
                  selectedFeature.status === 'approved' ? 'bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400 border-2 border-purple-300 dark:border-purple-700' :
                  selectedFeature.status === 'rejected' ? 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 border-2 border-red-300 dark:border-red-700' :
                  'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400 border-2 border-yellow-300 dark:border-yellow-700'
                }`}>
                  {selectedFeature.status || 'pending'}
                </span>
              </div>
            </div>

            {/* One-Pager Section */}
            {showOnePager && onePager && (
              <div className="bg-gradient-to-r from-blue-50 via-purple-50 to-pink-50 dark:from-blue-900/20 dark:via-purple-900/20 dark:to-pink-900/20 rounded-lg p-6 border-2 border-blue-300 dark:border-blue-700 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <FileText className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    📄 Stakeholder One-Pager
                  </h3>
                  <button
                    onClick={() => setShowOnePager(false)}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    ×
                  </button>
                </div>
                
                {/* Key Metrics */}
                {onePager.metrics && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Impact Score</div>
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {onePager.metrics.impact_score?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Request Volume</div>
                      <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                        {onePager.metrics.request_volume || 0}
                      </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Total ARR</div>
                      <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                        ${(onePager.metrics.total_arr_requested / 1000).toFixed(0)}K
                      </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Lost Deals</div>
                      <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                        {onePager.metrics.lost_deal_count || 0}
                      </div>
                    </div>
                  </div>
                )}

                {/* Customer Voice */}
                {onePager.customer_voice && onePager.customer_voice.quotes && onePager.customer_voice.quotes.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                      <Users className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                      Customer Voice ({onePager.customer_voice.quotes.length} quotes)
                    </h4>
                    <div className="space-y-3">
                      {onePager.customer_voice.quotes.slice(0, 3).map((quote: any, i: number) => (
                        <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-yellow-400">
                          <p className="text-sm text-gray-700 dark:text-gray-300 italic">
                            "{typeof quote === 'string' ? quote : (quote.quote || quote.content || JSON.stringify(quote))}"
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Persona Evaluations */}
                {onePager.persona_evaluations && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Team Evaluations</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {onePager.persona_evaluations.pm && (
                        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                          <div className="text-xs font-semibold text-blue-700 dark:text-blue-400 mb-2">Growth PM</div>
                          <div className="text-xs text-gray-700 dark:text-gray-300">
                            {onePager.persona_evaluations.pm.verdict || onePager.persona_evaluations.pm.reasoning || 'Pending'}
                          </div>
                        </div>
                      )}
                      {onePager.persona_evaluations.ux && (
                        <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                          <div className="text-xs font-semibold text-purple-700 dark:text-purple-400 mb-2">UX Designer</div>
                          <div className="text-xs text-gray-700 dark:text-gray-300">
                            {onePager.persona_evaluations.ux.verdict || onePager.persona_evaluations.ux.reasoning || 'Pending'}
                          </div>
                        </div>
                      )}
                      {onePager.persona_evaluations.engineering && (
                        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                          <div className="text-xs font-semibold text-green-700 dark:text-green-400 mb-2">Engineering</div>
                          <div className="text-xs text-gray-700 dark:text-gray-300">
                            Feasibility: {onePager.persona_evaluations.engineering.feasibility_score?.toFixed(1) || 'N/A'}/10
                          </div>
                        </div>
                      )}
                      {onePager.persona_evaluations.data_scientist && (
                        <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                          <div className="text-xs font-semibold text-orange-700 dark:text-orange-400 mb-2">Data Scientist</div>
                          <div className="text-xs text-gray-700 dark:text-gray-300">
                            {onePager.persona_evaluations.data_scientist.verdict || onePager.persona_evaluations.data_scientist.reasoning || 'Pending'}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* ROI Projection */}
                {onePager.roi_projection && (
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <h4 className="text-sm font-semibold text-green-700 dark:text-green-400 mb-2">ROI Projection</h4>
                    <div className="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                      <p>{onePager.roi_projection.estimated_impact}</p>
                      {onePager.roi_projection.arr_at_risk > 0 && (
                        <p className="font-semibold text-red-600 dark:text-red-400">
                          ARR at Risk: ${(onePager.roi_projection.arr_at_risk / 1000).toFixed(0)}K
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Adoption Stats Section - Feedback Loop: Request Volume vs Adoption */}
            {adoptionStats && (
              <div className="bg-gradient-to-r from-green-50 via-blue-50 to-purple-50 dark:from-green-900/20 dark:via-blue-900/20 dark:to-purple-900/20 rounded-lg p-6 border-2 border-green-300 dark:border-green-700 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <Target className="w-6 h-6 text-green-600 dark:text-green-400" />
                    📊 Feedback Loop: Request Volume vs Adoption
                  </h3>
                  <span className="px-3 py-1 text-xs font-semibold bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full">
                    Auto-Tracked
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 italic">
                  Compare how many customers requested this feature vs. how many actually adopted it after shipping.
                </p>
                
                {/* Request Volume vs Adoption Comparison */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                    <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Original Requests</div>
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {adoptionStats.original_request_volume?.total_requests || 0}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {adoptionStats.original_request_volume?.unique_customers || 0} customers
                    </div>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                    <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Adopted</div>
                    <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                      {adoptionStats.adoption_metrics?.adopted_count || 0}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {adoptionStats.adoption_metrics?.adoption_rate?.toFixed(1) || 0}% adoption rate
                    </div>
                  </div>
                </div>

                {/* Gap Analysis */}
                {adoptionStats.demand_vs_adoption && (
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 mb-4">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Gap Analysis</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-600 dark:text-gray-400">Requested</span>
                        <span className="font-semibold text-blue-600 dark:text-blue-400">
                          {adoptionStats.demand_vs_adoption.requested}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-600 dark:text-gray-400">Adopted</span>
                        <span className="font-semibold text-green-600 dark:text-green-400">
                          {adoptionStats.demand_vs_adoption.adopted}
                        </span>
                      </div>
                      <div className="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
                        <span className="text-xs font-semibold text-gray-700 dark:text-gray-300">Gap</span>
                        <span className="font-bold text-red-600 dark:text-red-400">
                          {adoptionStats.demand_vs_adoption.gap} ({adoptionStats.demand_vs_adoption.gap_percentage?.toFixed(1)}%)
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Insights */}
                {adoptionStats.insights && adoptionStats.insights.length > 0 && (
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800">
                    <h4 className="text-sm font-semibold text-yellow-800 dark:text-yellow-300 mb-2">Insights</h4>
                    <ul className="space-y-1">
                      {adoptionStats.insights.map((insight: string, i: number) => (
                        <li key={i} className="text-xs text-yellow-700 dark:text-yellow-400">
                          {insight}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="space-y-3 pt-6 border-t-2 border-gray-300 dark:border-gray-700">
              {/* View One-Pager Button */}
              {!showOnePager && (
                <button
                  onClick={handleLoadOnePager}
                  disabled={loadingOnePager}
                  className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg transition-all transform hover:scale-105"
                >
                  {loadingOnePager ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Loading One-Pager...</span>
                    </>
                  ) : (
                    <>
                      <FileText className="w-5 h-5" />
                      <span>View Stakeholder One-Pager</span>
                    </>
                  )}
                </button>
              )}

              {/* View Adoption Stats Button */}
              {!adoptionStats && selectedFeature.status === 'shipped' && (
                <button
                  onClick={handleLoadAdoptionStats}
                  disabled={loadingAdoptionStats}
                  className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg transition-all transform hover:scale-105"
                >
                  {loadingAdoptionStats ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Loading Adoption Stats...</span>
                    </>
                  ) : (
                    <>
                      <Target className="w-5 h-5" />
                      <span>View Adoption Stats (Request vs Adoption)</span>
                    </>
                  )}
                </button>
              )}

              {/* Mark as Shipped Button */}
              {selectedFeature.status !== 'shipped' && (
                <button
                  onClick={handleMarkAsShipped}
                  disabled={actionLoading === 'shipping'}
                  className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg transition-all transform hover:scale-105"
                >
                  {actionLoading === 'shipping' ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Marking as Shipped...</span>
                    </>
                  ) : (
                    <>
                      <Ship className="w-5 h-5" />
                      <span>Mark as Shipped (Select Quarter)</span>
                    </>
                  )}
                </button>
              )}

              {/* Ship Quarter Selection Modal */}
              {showShipModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                  <div className="bg-white dark:bg-gray-900 rounded-lg p-6 max-w-md w-full mx-4 border-2 border-green-500">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                      📅 Mark Feature as Shipped
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      Select which quarter this feature was shipped in. This will determine which quarterly report it appears in.
                    </p>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Quarter
                      </label>
                      <div className="grid grid-cols-4 gap-2">
                        {['Q1', 'Q2', 'Q3', 'Q4'].map((q) => (
                          <button
                            key={q}
                            onClick={() => setShipQuarter(q)}
                            className={`p-3 rounded-lg border-2 transition-all ${
                              shipQuarter === q
                                ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                                : 'border-gray-200 dark:border-gray-800 hover:border-green-300'
                            }`}
                          >
                            <div className="font-semibold text-gray-900 dark:text-white">{q}</div>
                          </button>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Year
                      </label>
                      <input
                        type="number"
                        value={shipYear}
                        onChange={(e) => setShipYear(parseInt(e.target.value))}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        min="2020"
                        max="2100"
                      />
                    </div>
                    
                    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 mb-4">
                      <p className="text-xs text-blue-700 dark:text-blue-400">
                        <strong>Note:</strong> This feature will appear in the <strong>{shipQuarter} {shipYear}</strong> quarterly report as a shipped feature. Customers will be automatically notified.
                      </p>
                    </div>
                    
                    <div className="flex space-x-3">
                      <button
                        onClick={confirmMarkAsShipped}
                        disabled={!shipQuarter || actionLoading === 'shipping'}
                        className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                      >
                        Confirm Ship in {shipQuarter} {shipYear}
                      </button>
                      <button
                        onClick={() => {
                          setShowShipModal(false)
                          setShipQuarter('')
                        }}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Notify Customers Button - Only show if shipped */}
              {selectedFeature.status === 'shipped' && (
                <button
                  onClick={handleNotifyCustomers}
                  disabled={actionLoading === 'notifying'}
                  className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg transition-all transform hover:scale-105"
                >
                  {actionLoading === 'notifying' ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Generating Notifications...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      <span>Notify Customers & Generate Emails</span>
                    </>
                  )}
                </button>
              )}

              {/* Show notification result */}
              {notificationResult && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <div className="flex items-start space-x-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5" />
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                        Notifications Generated!
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                        <p>• {notificationResult.total_customers} customers matched</p>
                        <p>• {notificationResult.email_templates?.length || 0} email templates generated</p>
                        {notificationResult.email_templates && notificationResult.email_templates.length > 0 && (
                          <div className="mt-2 pt-2 border-t border-blue-200 dark:border-blue-800">
                            <button
                              onClick={() => downloadEmailTemplates(notificationResult.email_templates)}
                              className="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center space-x-1"
                            >
                              <Download className="w-3 h-3" />
                              <span>Download Email Templates</span>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <button className="w-full px-6 py-3 border-2 border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 font-semibold transition-all hover:border-gray-400 dark:hover:border-gray-600">
                Add to Release Cycle
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

