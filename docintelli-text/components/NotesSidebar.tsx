
import React, { useState, useCallback } from 'react';
import MarkdownRenderer from './MarkdownRenderer';
import { convertMdToDocx } from '../services/apiService';
import NotebookIcon from './icons/NotebookIcon';

interface NotesSidebarProps {
  isOpen: boolean;
}

const NotesSidebar: React.FC<NotesSidebarProps> = ({ isOpen }) => {
  const [notesContent, setNotesContent] = useState<string>('# My Notes\n\nStart typing your markdown notes here...');
  const [isDownloadingDocx, setIsDownloadingDocx] = useState(false);

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
    <aside
      className={`flex-shrink-0 bg-gray-800/70 backdrop-blur-sm border-l border-gray-700 flex flex-col transition-all duration-300 ease-in-out ${isOpen ? 'w-[45rem]' : 'w-0'}`}
      aria-hidden={!isOpen}
    >
      <div className={`flex flex-col h-full overflow-hidden ${isOpen ? 'opacity-100' : 'opacity-0'}`}>
        <div className="flex-shrink-0 p-3 bg-gray-700/50 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <NotebookIcon className="w-5 h-5 text-gray-300" />
            <h2 className="text-lg font-semibold text-gray-300">Notes Editor</h2>
          </div>
          <button
            onClick={handleDownloadDocx}
            disabled={isDownloadingDocx || !notesContent}
            className="px-3 py-1 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed transition-colors"
          >
            {isDownloadingDocx ? 'Generating...' : 'Download DOCX'}
          </button>
        </div>

        <div className="flex-grow grid grid-rows-2 gap-px bg-gray-700">
          {/* Editor Pane */}
          <div className="bg-gray-800 flex flex-col">
            <textarea
              value={notesContent}
              onChange={handleNotesChange}
              className="w-full h-full p-4 bg-transparent text-gray-300 resize-none focus:outline-none font-mono text-sm"
              placeholder="Write your notes in Markdown..."
              aria-label="Notes Editor"
            />
          </div>

          {/* Preview Pane */}
          <div className="bg-gray-800 flex flex-col overflow-hidden">
            <div className="p-2 bg-gray-900/50 text-xs text-gray-400 font-semibold uppercase tracking-wider">
              Live Preview
            </div>
            <div className="flex-grow overflow-y-auto">
                <MarkdownRenderer content={notesContent} />
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default NotesSidebar;
