'use client';

import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X } from 'lucide-react';
import styles from './FileUpload.module.css';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile?: File;
  onClear?: () => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ 
  onFileSelect, 
  selectedFile,
  onClear 
}) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024 // 5MB
  });

  if (selectedFile) {
    return (
      <div className={styles.selectedFile}>
        <div className="flex items-center justify-between p-4 bg-green-50 border-2 border-green-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <FileText className="w-6 h-6 text-green-600" />
            <div>
              <p className="font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-sm text-gray-500">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>
          {onClear && (
            <button
              onClick={onClear}
              className="p-2 hover:bg-green-100 rounded-full transition-colors"
              aria-label="Remove file"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={`${styles.dropzone} ${
        isDragActive ? styles.active : ''
      } border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer transition-all hover:border-primary-400`}
    >
      <input {...getInputProps()} />
      <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
      {isDragActive ? (
        <p className="text-lg font-medium text-primary-600">
          Drop your resume here...
        </p>
      ) : (
        <>
          <p className="text-lg font-medium text-gray-700 mb-2">
            Drag and drop your resume here
          </p>
          <p className="text-sm text-gray-500">
            or click to select a file (PDF, DOC, DOCX, TXT, MD)
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Max file size: 5MB
          </p>
        </>
      )}
    </div>
  );
};