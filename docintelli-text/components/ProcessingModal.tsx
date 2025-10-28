
import React from 'react';
import { ProcessingStep, ProcessingStatus } from '../types';
import SparklesIcon from './icons/SparklesIcon';

interface ProcessingModalProps {
  steps: ProcessingStep[];
}

const getStatusIcon = (status: ProcessingStatus) => {
  switch (status) {
    case ProcessingStatus.DONE:
      return <span className="text-green-400">✓</span>;
    case ProcessingStatus.IN_PROGRESS:
      return (
        <svg className="animate-spin h-5 w-5 text-indigo-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      );
    case ProcessingStatus.PENDING:
      return <span className="text-gray-500">●</span>;
    default:
      return null;
  }
};

const ProcessingModal: React.FC<ProcessingModalProps> = ({ steps }) => {
  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-300">
      <div className="bg-gray-800 rounded-xl shadow-2xl p-8 w-full max-w-md border border-gray-700">
        <h2 className="text-2xl font-bold text-center text-white mb-2">Processing Document</h2>
        <p className="text-center text-gray-400 mb-6">Please wait while we work our magic...</p>
        <ul className="space-y-3">
          {steps.map((step, index) => (
            <li key={index} className="flex items-center space-x-4 text-gray-300">
              <div className="w-6 h-6 flex items-center justify-center font-bold text-sm">
                {getStatusIcon(step.status)}
              </div>
              <span className={`flex-grow ${step.status !== ProcessingStatus.PENDING ? 'text-white' : 'text-gray-400'}`}>
                {step.name}
              </span>
              {step.isAiStep && step.status !== ProcessingStatus.PENDING && (
                <SparklesIcon className={`w-5 h-5 ${step.status === ProcessingStatus.IN_PROGRESS ? 'text-indigo-400 animate-pulse' : 'text-indigo-500'}`} />
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ProcessingModal;
