'use client'

import { useTheme } from '@/components/providers/ThemeProvider'

export default function ProjectTimeline() {
  const { theme } = useTheme()

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2
          className="text-xl font-semibold mb-4"
          style={{ color: theme.textColor }}
        >
          Timeline
        </h2>
        <p
          className="text-sm"
          style={{ color: theme.secondaryColor }}
        >
          Timeline view coming soon...
        </p>
        <p className="mt-2 text-sm" style={{ color: theme.secondaryColor }}>
          Visualize project events, deadlines, and key milestones in chronological order.
        </p>
      </div>
    </div>
  )
} 