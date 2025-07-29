'use client'

import { useState, useRef } from 'react'
import UserGroupsList from '@/components/UserGroupsList'
import CreateUserGroupModal from '@/components/user-groups/CreateUserGroupModal'
import EditUserGroupModal from '@/components/user-groups/EditUserGroupModal'

interface UserGroup {
  id: number;
  name: string;
  tenant_id: number;
  created_at: string;
  created_by?: string;
  updated_at: string;
  updated_by?: string;
}

export default function DashboardUserGroups() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<UserGroup | null>(null);
  const userGroupsListRef = useRef<{ refresh: () => void }>(null);

  const handleCreateGroup = () => {
    setIsCreateModalOpen(true);
  };

  const handleEditGroup = (group: UserGroup) => {
    setSelectedGroup(group);
    setIsEditModalOpen(true);
  };

  const handleViewGroup = (groupId: number) => {
    // For now, we'll just edit the group when "View" is clicked
    // In the future, this could open a detailed view modal
    const group = { id: groupId, name: '', tenant_id: 0, created_at: '', updated_at: '' };
    setSelectedGroup(group);
    setIsEditModalOpen(true);
  };

  const handleModalSuccess = () => {
    // Refresh the groups list
    userGroupsListRef.current?.refresh();
  };

  return (
    <div>
      <UserGroupsList 
        ref={userGroupsListRef}
        onCreateGroup={handleCreateGroup}
        onEditGroup={handleEditGroup}
        onViewGroup={handleViewGroup}
      />
      
      <CreateUserGroupModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={handleModalSuccess}
      />
      
      <EditUserGroupModal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedGroup(null);
        }}
        onSuccess={handleModalSuccess}
        group={selectedGroup}
      />
    </div>
  )
} 