import React, { useState, useCallback, useEffect } from 'react';
import MarkdownRenderer from './MarkdownRenderer';
import { convertMdToDocx } from '../services/apiService';
import NotebookIcon from './icons/NotebookIcon';

const SESSION_STORAGE_KEY = 'docintelli-notes-content';

const NotesView: React.FC = () => {
  const [notesContent, setNotesContent] = useState<string>(() => {
    const savedNotes = sessionStorage.getItem(SESSION_STORAGE_KEY);
    return savedNotes !== null ? savedNotes : '# My Notes\n\nStart typing your markdown notes here...';
  });
  
  const [isDownloadingDocx, setIsDownloadingDocx] = useState(false);

  useEffect(() => {
    sessionStorage.setItem(SESSION_STORAGE_KEY, notesContent);
  }, [notesContent]);

  const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setNotesContent(e.target.value);
  };

  const handleDownloadDocx = useCallback(async () => {
    if (!notesContent) return;

    setIsDownloadingDocx(true);
    try {
      const blob = await convertMdToDocx(notesContent);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'my-notes.docx';
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
  }, [notesContent]);

  return (
    <div className="flex flex-col h-full p-4 space-y-4">
        <div className="flex-shrink-0 flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <NotebookIcon className="w-8 h-8 text-indigo-400" />
              <div>
                <h1 className="text-xl font-bold text-white tracking-tight">Notes Editor</h1>
                <p className="text-xs text-gray-400">Your personal markdown scratchpad</p>
              </div>
            </div>
            <button
              onClick={handleDownloadDocx}
              disabled={isDownloadingDocx || !notesContent}
              className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-indigo-500"
            >
              {isDownloadingDocx ? 'Generating...' : 'Download DOCX'}
            </button>
        </div>

        <div className="flex-grow grid grid-cols-1 md:grid-cols-2 gap-4 min-h-0">
            {/* Editor Pane */}
            <div className="bg-gray-800 rounded-lg shadow-lg flex flex-col">
                <div className="flex-shrink-0 p-3 bg-gray-700/50 rounded-t-lg">
                    <h2 className="text-lg font-semibold text-gray-300">Markdown</h2>
                </div>
                <div className="flex-grow relative">
                    <textarea
                        value={notesContent}
                        onChange={handleNotesChange}
                        className="absolute inset-0 w-full h-full p-4 bg-transparent text-gray-300 resize-none focus:outline-none font-mono text-sm"
                        placeholder="Write your notes..."
                        aria-label="Notes Editor"
                    />
                </div>
            </div>

            {/* Preview Pane */}
            <div className="bg-gray-800 rounded-lg shadow-lg flex flex-col">
                <div className="flex-shrink-0 p-3 bg-gray-700/50 rounded-t-lg">
                    <h2 className="text-lg font-semibold text-gray-300">Preview</h2>
                </div>
                <div className="flex-grow overflow-y-auto">
                    <MarkdownRenderer content={notesContent} />
                </div>
            </div>
        </div>
    </div>
  );
};

export default NotesView;