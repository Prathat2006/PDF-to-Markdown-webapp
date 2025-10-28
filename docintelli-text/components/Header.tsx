
import React from 'react';
import SparklesIcon from './icons/SparklesIcon';

interface HeaderProps {
    onReset: () => void;
    showReset: boolean;
}

const Header: React.FC<HeaderProps> = ({ onReset, showReset }) => {
  return (
    <header className="flex-shrink-0 bg-gray-800/50 backdrop-blur-sm shadow-md z-20">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <SparklesIcon className="w-8 h-8 text-indigo-400" />
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">DocIntelli-Text</h1>
            <p className="text-xs text-gray-400">AI-Powered PDF to Markdown Converter</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          {showReset && (
               <button
                  onClick={onReset}
                  className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-500 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-gray-400 text-sm"
                >
                  Process New PDF
                </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
