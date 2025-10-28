
import React, { useState, useCallback } from 'react';
import { convertMdToDocx } from '../services/apiService';
import MarkdownRenderer from './MarkdownRenderer';

interface MarkdownPreviewProps {
  content: string | null;
}

const MarkdownPreview: React.FC<MarkdownPreviewProps> = ({ content }) => {
  const [copyButtonText, setCopyButtonText] = useState('Copy');
  const [isDownloadingDocx, setIsDownloadingDocx] = useState(false);

  const handleCopy = useCallback(() => {
    if (content) {
      navigator.clipboard.writeText(content).then(() => {
        setCopyButtonText('Copied!');
        setTimeout(() => setCopyButtonText('Copy'), 2000);
      });
    }
  }, [content]);

  const handleDownload = useCallback(() => {
    if (content) {
      const blob = new Blob([content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'extracted-document.md';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  }, [content]);
  
  const handleDownloadDocx = useCallback(async () => {
    if (!content) return;

    setIsDownloadingDocx(true);
    try {
      const blob = await convertMdToDocx(content);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'extracted-document.docx';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download DOCX file', error);
      alert('Failed to generate DOCX file. Please ensure the conversion server is running and check the console for details.');
    } finally {
      setIsDownloadingDocx(false);
    }
  }, [content]);

  if (!content) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <p>Processed content will appear here.</p>
      </div>
    );
  }

  return (
    <div className="relative h-full">
      <div className="absolute top-2 right-4 z-10 flex space-x-2">
        <button onClick={handleCopy} className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded-md transition-colors">{copyButtonText}</button>
        <button onClick={handleDownload} className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded-md transition-colors">Download MD</button>
        <button
          onClick={handleDownloadDocx}
          disabled={isDownloadingDocx}
          className="px-3 py-1 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-wait transition-colors"
        >
          {isDownloadingDocx ? 'Generating...' : 'Download DOCX'}
        </button>
      </div>
      <div className="h-full overflow-y-auto">
        <MarkdownRenderer content={content} />
      </div>
    </div>
  );
};

export default MarkdownPreview;
