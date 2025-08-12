import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  FileBrowser,
  FileContextMenu,
  FileList,
  FileNavbar,
  FileToolbar,
  ChonkyActions,
  defineFileAction,
  ChonkyIconName,
} from 'chonky';
import { ChonkyIconFA } from 'chonky-icon-fontawesome';
import { useFileOperations } from '../../hooks/useFileOperations';

// Custom actions for AI integration
const analyzeAction = defineFileAction({
  id: 'analyze_files',
  button: {
    name: 'Analyze with AI',
    toolbar: true,
    contextMenu: true,
    icon: ChonkyIconName.config,
  },
});

const createExperimentAction = defineFileAction({
  id: 'create_experiment',
  button: {
    name: 'Create Experiment Folder',
    toolbar: true,
    icon: ChonkyIconName.folderCreate,
  },
});

const ChonkyFileManager = ({ onFileSelect, onAnalyze }) => {
  const [files, setFiles] = useState([]);
  const [folderChain, setFolderChain] = useState([]);
  const [currentPath, setCurrentPath] = useState('/');
  
  const { 
    listFiles, 
    uploadFiles, 
    deleteFiles, 
    moveFiles,
    createFolder 
  } = useFileOperations();

  // Load files for current path
  useEffect(() => {
    loadFiles(currentPath);
  }, [currentPath]);

  const loadFiles = async (path) => {
    try {
      const fileList = await listFiles(path);
      setFiles(fileList);
    } catch (error) {
      console.error('Failed to load files:', error);
    }
  };

  // File actions configuration
  const fileActions = useMemo(
    () => [
      ChonkyActions.CreateFolder,
      ChonkyActions.DeleteFiles,
      ChonkyActions.UploadFiles,
      ChonkyActions.DownloadFiles,
      ChonkyActions.CopyFiles,
      ChonkyActions.MoveFiles,
      analyzeAction,
      createExperimentAction,
    ],
    []
  );

  // Handle file actions
  const handleFileAction = useCallback(
    async (data) => {
      console.log('File action:', data);
      
      switch (data.id) {
        case ChonkyActions.OpenFiles.id:
          const { targetFile } = data.payload;
          if (targetFile && targetFile.isDir) {
            setCurrentPath(targetFile.id);
            setFolderChain([...folderChain, targetFile]);
          } else if (targetFile) {
            onFileSelect?.(targetFile);
          }
          break;
          
        case ChonkyActions.CreateFolder.id:
          const folderName = prompt('Enter folder name:');
          if (folderName) {
            await createFolder(currentPath, folderName);
            await loadFiles(currentPath);
          }
          break;
          
        case ChonkyActions.DeleteFiles.id:
          if (confirm('Delete selected files?')) {
            const filesToDelete = data.state.selectedFiles;
            await deleteFiles(filesToDelete.map(f => f.id));
            await loadFiles(currentPath);
          }
          break;
          
        case ChonkyActions.UploadFiles.id:
          const input = document.createElement('input');
          input.type = 'file';
          input.multiple = true;
          input.onchange = async (e) => {
            const files = Array.from(e.target.files);
            await uploadFiles(currentPath, files);
            await loadFiles(currentPath);
          };
          input.click();
          break;
          
        case 'analyze_files':
          const selectedFiles = data.state.selectedFiles;
          if (selectedFiles.length > 0) {
            onAnalyze?.(selectedFiles);
          }
          break;
          
        case 'create_experiment':
          const expName = prompt('Enter experiment name:');
          if (expName) {
            const folderName = `exp_${Date.now()}_${expName.toLowerCase().replace(/\s+/g, '_')}`;
            await createFolder(currentPath, folderName);
            await loadFiles(currentPath);
          }
          break;
          
        default:
          console.log('Unhandled action:', data.id);
      }
    },
    [currentPath, folderChain, onFileSelect, onAnalyze]
  );

  return (
    <div style={{ height: '100vh', width: '100%' }}>
      <FileBrowser
        files={files}
        folderChain={folderChain}
        fileActions={fileActions}
        onFileAction={handleFileAction}
        iconComponent={ChonkyIconFA}
        darkMode={false}
      >
        <FileNavbar />
        <FileToolbar />
        <FileList />
        <FileContextMenu />
      </FileBrowser>
    </div>
  );
};

export default ChonkyFileManager;