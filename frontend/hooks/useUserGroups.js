'use client';

import { useState, useEffect } from 'react';
import { useSession } from '@auth0/nextjs-auth0/client';

export function useUserGroups() {
  const [userGroups, setUserGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { data: session, isLoading: sessionLoading } = useSession();

  const fetchUserGroups = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/user-groups', {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setUserGroups(data);
    } catch (err) {
      console.error('Error fetching user groups:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createUserGroup = async (groupData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/user-groups', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(groupData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const newGroup = await response.json();
      setUserGroups(prev => [...prev, newGroup]);
      return newGroup;
    } catch (err) {
      console.error('Error creating user group:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateUserGroup = async (groupId, groupData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/user-groups/${groupId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(groupData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const updatedGroup = await response.json();
      setUserGroups(prev => 
        prev.map(group => 
          group.id === groupId ? updatedGroup : group
        )
      );
      return updatedGroup;
    } catch (err) {
      console.error('Error updating user group:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteUserGroup = async (groupId) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/user-groups/${groupId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setUserGroups(prev => prev.filter(group => group.id !== groupId));
    } catch (err) {
      console.error('Error deleting user group:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const addUserToGroup = async (groupId, userId) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/user-groups/${groupId}/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Refresh the user groups to get updated member counts
      await fetchUserGroups();
    } catch (err) {
      console.error('Error adding user to group:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const removeUserFromGroup = async (groupId, userId) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/user-groups/${groupId}/users/${userId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Refresh the user groups to get updated member counts
      await fetchUserGroups();
    } catch (err) {
      console.error('Error removing user from group:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Fetch user groups when session is available
  useEffect(() => {
    if (!sessionLoading && session) {
      fetchUserGroups();
    }
  }, [session, sessionLoading]);

  return {
    userGroups,
    loading,
    error,
    fetchUserGroups,
    createUserGroup,
    updateUserGroup,
    deleteUserGroup,
    addUserToGroup,
    removeUserFromGroup,
  };
} 