'use client'

import { useTheme } from '@/components/providers/ThemeProvider'

export default function ProjectAIAssistant() {
  const { theme } = useTheme()

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2
          className="text-xl font-semibold mb-4"
          style={{ color: theme.textColor }}
        >
          AI Assistant
        </h2>
        <p
          className="text-sm"
          style={{ color: theme.secondaryColor }}
        >
          AI Assistant coming soon...
        </p>
        <p className="mt-2 text-sm" style={{ color: theme.secondaryColor }}>
          Get intelligent insights, analysis, and recommendations for your project using AI.
        </p>
      </div>
    </div>
  )
} 