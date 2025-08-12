import { useState, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export const useFileOperations = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // List files in a directory
  const listFiles = useCallback(async (path = '/') => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/files/list`, {
        params: { path }
      });
      
      // Transform response to Chonky format
      const files = response.data.files.map(file => ({
        id: file.path,
        name: file.name,
        isDir: file.is_dir,
        size: file.size,
        modDate: file.modified,
        thumbnailUrl: file.thumbnail_url,
      }));
      
      return files;
    } catch (err) {
      setError(err.message);
      console.error('Failed to list files:', err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Upload files
  const uploadFiles = useCallback(async (path, files) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('path', path);
      
      files.forEach(file => {
        formData.append('files', file);
      });
      
      const response = await axios.post(
        `${API_BASE_URL}/api/files/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            console.log(`Upload progress: ${percentCompleted}%`);
          },
        }
      );
      
      return response.data;
    } catch (err) {
      setError(err.message);
      console.error('Failed to upload files:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Delete files
  const deleteFiles = useCallback(async (paths) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.delete(`${API_BASE_URL}/api/files`, {
        data: { paths }
      });
      
      return response.data;
    } catch (err) {
      setError(err.message);
      console.error('Failed to delete files:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Move files
  const moveFiles = useCallback(async (sourcePaths, destinationPath) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.put(`${API_BASE_URL}/api/files/move`, {
        source_paths: sourcePaths,
        destination_path: destinationPath,
      });
      
      return response.data;
    } catch (err) {
      setError(err.message);
      console.error('Failed to move files:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Create folder
  const createFolder = useCallback(async (path, folderName) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/files/folder`, {
        path,
        folder_name: folderName,
      });
      
      return response.data;
    } catch (err) {
      setError(err.message);
      console.error('Failed to create folder:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Download file
  const downloadFile = useCallback(async (path) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/files/download/${encodeURIComponent(path)}`,
        { responseType: 'blob' }
      );
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', path.split('/').pop());
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      return true;
    } catch (err) {
      setError(err.message);
      console.error('Failed to download file:', err);
      return false;
    }
  }, []);

  return {
    listFiles,
    uploadFiles,
    deleteFiles,
    moveFiles,
    createFolder,
    downloadFile,
    loading,
    error,
  };
};