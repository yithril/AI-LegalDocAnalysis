'use client'

import { useTheme } from '@/components/providers/ThemeProvider'

export default function ProjectActors() {
  const { theme } = useTheme()

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2
          className="text-xl font-semibold mb-4"
          style={{ color: theme.textColor }}
        >
          Actors
        </h2>
        <p
          className="text-sm"
          style={{ color: theme.secondaryColor }}
        >
          Actor management coming soon...
        </p>
        <p className="mt-2 text-sm" style={{ color: theme.secondaryColor }}>
          Identify and track key individuals, organizations, and entities involved in the project.
        </p>
      </div>
    </div>
  )
} 