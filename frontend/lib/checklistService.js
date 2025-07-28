import api from './api';

// Auth service
export const authService = {
  async loginWithGoogle(googleCredential) {
    try {
      const response = await api.post('/auth/google', {
        credential: googleCredential
      });
      
      // Store JWT token
      localStorage.setItem('access_token', response.data.access_token);
      
      return response.data;
    } catch (error) {
      console.error('Google login failed:', error);
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  },

  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      console.error('Get current user failed:', error);
      throw error;
    }
  },

  logout() {
    localStorage.removeItem('access_token');
  }
};

// Checklist service
export const checklistService = {
  async getChecklists(skip = 0, limit = 20) {
    try {
      const response = await api.get('/checklists', {
        params: { skip, limit }
      });
      
      // Backend returns PaginatedResponse with items array
      return {
        checklists: response.data.items,
        total: response.data.total,
        skip: response.data.skip,
        limit: response.data.limit
      };
    } catch (error) {
      console.error('Get checklists failed:', error);
      throw error;
    }
  },

  async getChecklist(checklistId) {
    try {
      const response = await api.get(`/checklists/${checklistId}`);
      return response.data;
    } catch (error) {
      console.error('Get checklist failed:', error);
      throw error;
    }
  },

  async createChecklist(checklistData) {
    try {
      // Map frontend format to backend format
      const backendData = {
        title: checklistData.title,
        description: checklistData.description || null,
        items: checklistData.items?.map((item, index) => ({
          description: item.description,
          priority: item.priority || 'medium',
          display_order: index,
          due_date: item.due_date || null
        })) || []
      };

      const response = await api.post('/checklists', backendData);
      return mapChecklistResponse(response.data);
    } catch (error) {
      console.error('Create checklist failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create checklist');
    }
  },

  async updateChecklist(checklistId, checklistData) {
    try {
      // Only send title and description for update
      const backendData = {
        title: checklistData.title,
        description: checklistData.description || null
      };

      const response = await api.put(`/checklists/${checklistId}`, backendData);
      return mapChecklistResponse(response.data);
    } catch (error) {
      console.error('Update checklist failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update checklist');
    }
  },

  async deleteChecklist(checklistId) {
    try {
      await api.delete(`/checklists/${checklistId}`);
      return true;
    } catch (error) {
      console.error('Delete checklist failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to delete checklist');
    }
  }
};

// Checklist Item service
export const checklistItemService = {
  async createItem(checklistId, itemData) {
    try {
      const backendData = {
        description: itemData.description,
        priority: itemData.priority || 'medium',
        display_order: itemData.order || 0,
        due_date: itemData.due_date || null
      };

      const response = await api.post(`/checklists/${checklistId}/items`, backendData);
      return mapItemResponse(response.data);
    } catch (error) {
      console.error('Create item failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create item');
    }
  },

  async updateItem(checklistId, itemId, itemData) {
    try {
      const backendData = {
        description: itemData.description,
        is_completed: itemData.is_completed,
        priority: itemData.priority,
        display_order: itemData.order,
        due_date: itemData.due_date || null
      };

      // Remove undefined values
      Object.keys(backendData).forEach(key => {
        if (backendData[key] === undefined) {
          delete backendData[key];
        }
      });

      const response = await api.put(`/checklists/${checklistId}/items/${itemId}`, backendData);
      return mapItemResponse(response.data);
    } catch (error) {
      console.error('Update item failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update item');
    }
  },

  async deleteItem(checklistId, itemId) {
    try {
      await api.delete(`/checklists/${checklistId}/items/${itemId}`);
      return true;
    } catch (error) {
      console.error('Delete item failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to delete item');
    }
  },

  async toggleItem(checklistId, itemId) {
    try {
      const response = await api.patch(`/checklists/${checklistId}/items/${itemId}/toggle`);
      return mapItemResponse(response.data);
    } catch (error) {
      console.error('Toggle item failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to toggle item');
    }
  }
};

// Helper functions to map backend responses to frontend format
function mapChecklistResponse(backendChecklist) {
  return {
    id: backendChecklist.id,
    title: backendChecklist.title,
    description: backendChecklist.description,
    created_at: backendChecklist.created_at,
    updated_at: backendChecklist.updated_at,
    items: backendChecklist.items?.map(mapItemResponse) || [],
    // Add computed fields that frontend expects
    total_items: backendChecklist.total_items,
    completed_items: backendChecklist.completed_items,
    completion_percentage: backendChecklist.completion_percentage
  };
}

function mapItemResponse(backendItem) {
  return {
    id: backendItem.id,
    checklist_id: backendItem.checklist_id,
    description: backendItem.description,
    is_completed: backendItem.is_completed,
    priority: backendItem.priority,
    order: backendItem.display_order, // Map display_order to order
    due_date: backendItem.due_date,
    created_at: backendItem.created_at,
    updated_at: backendItem.updated_at,
    is_overdue: backendItem.is_overdue
  };
}

// Export all services
export default {
  auth: authService,
  checklists: checklistService,
  items: checklistItemService
};