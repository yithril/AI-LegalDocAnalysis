'use client'

import { useState } from 'react'
import DashboardSidebar from '@/components/dashboard/DashboardSidebar'
import DashboardOverview from '@/components/dashboard/sections/DashboardOverview'
import DashboardProjects from '@/components/dashboard/sections/DashboardProjects'
import DashboardMyGroups from '@/components/dashboard/sections/DashboardMyGroups'
import DashboardProfile from '@/components/dashboard/sections/DashboardProfile'
import DashboardUserGroups from '@/components/dashboard/sections/DashboardUserGroups'
import DashboardUserManagement from '@/components/dashboard/sections/DashboardUserManagement'

export default function DashboardPage() {
  const [activeSection, setActiveSection] = useState('overview')

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'overview':
        return <DashboardOverview />
      case 'projects':
        return <DashboardProjects />
      case 'my-groups':
        return <DashboardMyGroups />
      case 'profile':
        return <DashboardProfile />
      case 'user-groups':
        return <DashboardUserGroups />
      case 'user-management':
        return <DashboardUserManagement />
      default:
        return <DashboardOverview />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="w-full py-6 px-6">
        {/* Main Content with Sidebar */}
        <div className="flex gap-6">
          {/* Sidebar */}
          <DashboardSidebar
            activeSection={activeSection}
            onSectionChange={setActiveSection}
          />

                      {/* Main Content */}
            <div className="flex-1">
              {activeSection === 'overview' ? (
                <DashboardOverview onSectionChange={setActiveSection} />
              ) : (
                renderActiveSection()
              )}
            </div>
        </div>
      </div>
    </div>
  )
} 