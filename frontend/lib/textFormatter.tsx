/**
 * Utility functions to clean and format text content
 * Removes markdown formatting and converts to clean, readable text
 */

import React from 'react'

export function cleanMarkdown(text: string | null | undefined): string {
  if (!text) return ''
  
  let cleaned = String(text)
  
  // Keep markdown bold (**text**) for formatTextWithBold to process
  // Only remove __text__ format
  cleaned = cleaned.replace(/__(.*?)__/g, '$1')
  
  // Remove markdown headers (# ## ###)
  cleaned = cleaned.replace(/^#{1,6}\s+/gm, '')
  
  // Remove markdown links [text](url) -> text
  cleaned = cleaned.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
  
  // Remove markdown code blocks
  cleaned = cleaned.replace(/```[\s\S]*?```/g, '')
  cleaned = cleaned.replace(/`([^`]+)`/g, '$1')
  
  // Remove markdown lists (convert to plain text)
  cleaned = cleaned.replace(/^\s*[-*+]\s+/gm, '• ')
  cleaned = cleaned.replace(/^\s*\d+\.\s+/gm, '')
  
  // Clean up multiple spaces/newlines
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n')
  cleaned = cleaned.replace(/[ \t]{2,}/g, ' ')
  
  return cleaned.trim()
}

export function formatText(text: string | null | undefined, maxLength?: number): string {
  if (!text) return ''
  
  let formatted = cleanMarkdown(text)
  
  // Truncate if maxLength specified
  if (maxLength && formatted.length > maxLength) {
    formatted = formatted.substring(0, maxLength) + '...'
  }
  
  return formatted
}

export function formatBusinessImpact(text: string | null | undefined): string {
  if (!text) return ''
  
  let formatted = cleanMarkdown(text)
  
  // Make it more concise - extract key points
  const lines = formatted.split('\n').filter(line => line.trim().length > 0)
  const keyPoints: string[] = []
  
  for (const line of lines) {
    const trimmed = line.trim()
    // Skip headers and empty lines
    if (trimmed.startsWith('#') || trimmed.length < 10) continue
    
    // Extract bullet points or key statements
    if (trimmed.startsWith('•') || trimmed.startsWith('-') || trimmed.match(/^[A-Z][^:]+:/)) {
      keyPoints.push(trimmed.replace(/^[•-]\s*/, ''))
    }
    
    // Limit to 5-7 key points for brevity
    if (keyPoints.length >= 7) break
  }
  
  // If we extracted key points, return them; otherwise return first 300 chars
  if (keyPoints.length > 0) {
    return keyPoints.join('\n\n')
  }
  
  return formatted.substring(0, 400) + (formatted.length > 400 ? '...' : '')
}

export function summarizeText(text: string, maxLength: number = 500): string {
  if (!text || text.length <= maxLength) return text
  
  // Try to break at sentence boundaries
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 20)
  
  if (sentences.length === 0) {
    return text.substring(0, maxLength - 3) + '...'
  }
  
  // Take first 3-4 sentences that fit within maxLength
  let summary = ''
  for (const sentence of sentences) {
    if ((summary + sentence).length > maxLength) break
    summary += sentence.trim() + '. '
    if (summary.length > maxLength * 0.8) break // Stop at 80% to leave room
  }
  
  return summary.trim() || text.substring(0, maxLength - 3) + '...'
}

export function formatTextWithBold(text: string): React.ReactNode {
  if (!text) return null
  
  // Remove markdown asterisks and convert to bold spans
  const parts: React.ReactNode[] = []
  const lines = text.split('\n').filter(line => line.trim())
  
  lines.forEach((line, lineIdx) => {
    if (lineIdx > 0) parts.push(<br key={`br-${lineIdx}`} />)
    
    // Remove markdown bold (**text**)
    const cleaned = line.replace(/\*\*(.*?)\*\*/g, '<BOLD>$1</BOLD>')
    
    // Split by bold markers and create React elements
    const segments = cleaned.split(/(<BOLD>.*?<\/BOLD>)/g)
    segments.forEach((segment, segIdx) => {
      if (segment.startsWith('<BOLD>') && segment.endsWith('</BOLD>')) {
        const boldText = segment.replace(/<\/?BOLD>/g, '')
        parts.push(<strong key={`bold-${lineIdx}-${segIdx}`} className="font-semibold text-gray-900 dark:text-white">{boldText}</strong>)
      } else if (segment.trim()) {
        parts.push(<span key={`text-${lineIdx}-${segIdx}`}>{segment}</span>)
      }
    })
  })
  
  return <>{parts}</>
}

export function formatReasoning(text: string | null | undefined): string {
  if (!text) return ''
  
  let formatted = cleanMarkdown(text)
  
  // Extract first 2-3 sentences for concise reasoning
  const sentences = formatted.split(/[.!?]+/).filter(s => s.trim().length > 20)
  
  if (sentences.length <= 3) {
    return formatted.substring(0, 300) + (formatted.length > 300 ? '...' : '')
  }
  
  // Return first 2-3 sentences
  return sentences.slice(0, 3).join('. ') + '.'
}

export function formatList(items: string[] | null | undefined): string[] {
  if (!items || !Array.isArray(items)) return []
  
  return items.map(item => cleanMarkdown(item))
}




