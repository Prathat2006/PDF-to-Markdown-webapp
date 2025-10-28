
import React, { useState, useEffect } from 'react';
import { getHistory } from '../services/apiService';
import { HistoryItem } from '../types';
import HistoryIcon from './icons/HistoryIcon';

interface HistoryViewProps {
  onLoadItem: (filename: string) => void;
}

const HistoryView: React.FC<HistoryViewProps> = ({ onLoadItem }) => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getHistory();
        // Sort by timestamp descending to show the most recent first
        const sortedData = data.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        setHistory(sortedData);
      } catch (err) {
        setError('Failed to load conversion history.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  };

  return (
    <div className="flex flex-col h-full p-4 space-y-4 text-gray-200">
      <div className="flex-shrink-0">
        <div className="flex items-center space-x-3">
          <HistoryIcon className="w-8 h-8 text-indigo-400" />
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">Conversion History</h1>
            <p className="text-xs text-gray-400">Review your past processed documents</p>
          </div>
        </div>
      </div>
      <div className="flex-grow bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <svg className="animate-spin h-8 w-8 text-indigo-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full text-red-400">{error}</div>
        ) : history.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">No history found.</div>
        ) : (
          <ul className="divide-y divide-gray-700 h-full overflow-y-auto">
            {history.map((item) => (
              <li key={item.session_id}>
                <button
                  onClick={() => onLoadItem(item.filename)}
                  className="w-full text-left p-4 hover:bg-gray-700/50 transition-colors duration-150 focus:outline-none focus:bg-gray-700"
                >
                  <div className="flex justify-between items-center">
                    <div className="flex-grow truncate pr-4">
                      <p className="font-semibold text-white truncate" title={item.filename}>{item.filename}</p>
                      <p className="text-sm text-gray-400">{formatDate(item.timestamp)}</p>
                    </div>
                    <div className="flex-shrink-0">
                      {item.ocr && <span className="text-xs font-bold text-indigo-400 bg-indigo-900/50 px-2 py-1 rounded-full">OCR</span>}
                    </div>
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default HistoryView;
