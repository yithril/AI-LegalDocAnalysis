'use client'

import { useTheme } from '@/components/providers/ThemeProvider'

export default function ProjectDocuments() {
  const { theme } = useTheme()

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2
          className="text-xl font-semibold mb-4"
          style={{ color: theme.textColor }}
        >
          Documents
        </h2>
        <p
          className="text-sm"
          style={{ color: theme.secondaryColor }}
        >
          Document management coming soon...
        </p>
        <p className="mt-2 text-sm" style={{ color: theme.secondaryColor }}>
          Upload and analyze legal documents, contracts, and other project-related files.
        </p>
      </div>
    </div>
  )
} 