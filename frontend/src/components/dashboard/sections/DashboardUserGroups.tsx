'use client'

import { useState, useRef } from 'react'
import UserGroupsList from '@/components/UserGroupsList'
import CreateUserGroupModal from '@/components/user-groups/CreateUserGroupModal'
import EditUserGroupModal from '@/components/user-groups/EditUserGroupModal'
import ViewGroupDetailsModal from '@/components/user-groups/ViewGroupDetailsModal'
import ManageGroupUsersModal from '@/components/user-groups/ManageGroupUsersModal'
import { useApiClient } from '@/lib/api-client'
import type { GetUserGroupResponse } from '@/types/api'

export default function DashboardUserGroups() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isManageUsersModalOpen, setIsManageUsersModalOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<GetUserGroupResponse | null>(null);
  const userGroupsListRef = useRef<{ refresh: () => void }>(null);
  const apiClient = useApiClient();

  const handleCreateGroup = () => {
    setIsCreateModalOpen(true);
  };

  const handleEditGroup = (group: GetUserGroupResponse) => {
    setSelectedGroup(group);
    setIsEditModalOpen(true);
  };

  const handleViewGroup = async (groupId: number) => {
    try {
      // Fetch the group details from the API
      const group = await apiClient.getUserGroupById(groupId);
      setSelectedGroup(group);
      setIsViewModalOpen(true);
    } catch (error) {
      console.error('Failed to fetch group details:', error);
      // Fallback to a basic group object if API call fails
      const fallbackGroup = { 
        id: groupId, 
        name: 'Unknown Group', 
        tenant_id: 0, 
        created_at: new Date().toISOString(), 
        updated_at: new Date().toISOString() 
      } as GetUserGroupResponse;
      setSelectedGroup(fallbackGroup);
      setIsViewModalOpen(true);
    }
  };

  const handleManageUsers = (group: GetUserGroupResponse) => {
    setSelectedGroup(group);
    setIsManageUsersModalOpen(true);
  };

  const handleModalSuccess = () => {
    // Refresh the groups list
    userGroupsListRef.current?.refresh();
  };

  const closeModals = () => {
    setIsCreateModalOpen(false);
    setIsEditModalOpen(false);
    setIsViewModalOpen(false);
    setIsManageUsersModalOpen(false);
    setSelectedGroup(null);
  };

  return (
    <div>
      <UserGroupsList 
        ref={userGroupsListRef}
        onCreateGroup={handleCreateGroup}
        onEditGroup={handleEditGroup}
        onViewGroup={handleViewGroup}
        onManageUsers={handleManageUsers}
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

      <ViewGroupDetailsModal
        isOpen={isViewModalOpen}
        onClose={() => {
          setIsViewModalOpen(false);
          setSelectedGroup(null);
        }}
        group={selectedGroup}
      />

      <ManageGroupUsersModal
        isOpen={isManageUsersModalOpen}
        onClose={() => {
          setIsManageUsersModalOpen(false);
          setSelectedGroup(null);
        }}
        onSuccess={handleModalSuccess}
        group={selectedGroup}
      />
    </div>
  )
} 