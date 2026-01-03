'use client'

import { useState } from 'react'
import { Bell, Send, CheckCircle, TrendingUp, Users, Mail } from 'lucide-react'

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

export default function NotificationsPanel() {
  const [notifications] = useState([
    {
      id: 1,
      feature: 'Advanced Analytics Dashboard',
      shippedDate: '2024-01-15',
      requestedBy: ['Customer A', 'Customer B', 'Customer C'],
      adoptionRate: 0.75,
      requestVolume: 12
    },
    {
      id: 2,
      feature: 'API Webhooks',
      shippedDate: '2024-01-10',
      requestedBy: ['Customer D', 'Customer E'],
      adoptionRate: 0.60,
      requestVolume: 8
    }
  ])

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Customer Updates & Notifications
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Track feature shipments and customer adoption
        </p>
      </div>

      <div className="space-y-6">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                  {notification.feature}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Shipped on {formatDate(notification.shippedDate)}
                </p>
              </div>
              <CheckCircle className="w-6 h-6 text-green-500" />
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <Users className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Requested By
                  </span>
                </div>
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {notification.requestedBy.length}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {notification.requestedBy.join(', ')}
                </div>
              </div>

              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-green-600 dark:text-green-400" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Adoption Rate
                  </span>
                </div>
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {(notification.adoptionRate * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {notification.requestVolume} total requests
                </div>
              </div>
            </div>

            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Adoption vs Demand
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {Math.round(notification.adoptionRate * notification.requestVolume)} / {notification.requestVolume}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${notification.adoptionRate * 100}%` }}
                />
              </div>
            </div>

            <div className="flex space-x-2">
              <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2">
                <Mail className="w-4 h-4" />
                <span>Send Update Message</span>
              </button>
              <button className="px-4 py-2 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
          Pending Notifications
        </h2>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          No pending notifications. Customers will be automatically notified when features they requested are shipped.
        </div>
      </div>
    </div>
  )
}

