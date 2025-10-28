
import React from 'react';
import FileConversionIcon from './icons/FileConversionIcon';
import NotebookIcon from './icons/NotebookIcon';
import SparklesIcon from './icons/SparklesIcon';
import SettingsIcon from './icons/SettingsIcon';
import HistoryIcon from './icons/HistoryIcon';

interface SidebarNavProps {
  activeView: 'conversion' | 'notes' | 'settings' | 'history';
  setActiveView: (view: 'conversion' | 'notes' | 'settings' | 'history') => void;
}

const NavItem: React.FC<{
    icon: React.ReactNode;
    label: string;
    isActive: boolean;
    onClick: () => void;
}> = ({ icon, label, isActive, onClick }) => (
    <button
        onClick={onClick}
        className={`flex flex-col items-center justify-center w-full h-20 space-y-1 transition-colors duration-200 ${
            isActive ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:bg-gray-700 hover:text-gray-200'
        }`}
        aria-current={isActive ? 'page' : undefined}
    >
        {icon}
        <span className="text-xs font-medium">{label}</span>
    </button>
);

const SidebarNav: React.FC<SidebarNavProps> = ({ activeView, setActiveView }) => {
  return (
    <nav className="w-20 bg-gray-800 flex flex-col items-center flex-shrink-0 border-r border-gray-700/50">
        <div className="flex items-center justify-center h-16 w-full flex-shrink-0">
            <SparklesIcon className="w-8 h-8 text-indigo-400" />
        </div>
        <div className="w-full">
            <NavItem
                icon={<FileConversionIcon className="w-6 h-6" />}
                label="Convert"
                isActive={activeView === 'conversion'}
                onClick={() => setActiveView('conversion')}
            />
             <NavItem
                icon={<HistoryIcon className="w-6 h-6" />}
                label="History"
                isActive={activeView === 'history'}
                onClick={() => setActiveView('history')}
            />
            <NavItem
                icon={<NotebookIcon className="w-6 h-6" />}
                label="Notes"
                isActive={activeView === 'notes'}
                onClick={() => setActiveView('notes')}
            />
            <NavItem
                icon={<SettingsIcon className="w-6 h-6" />}
                label="Settings"
                isActive={activeView === 'settings'}
                onClick={() => setActiveView('settings')}
            />
        </div>
    </nav>
  );
};

export default SidebarNav;
