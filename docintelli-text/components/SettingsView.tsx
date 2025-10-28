
import React from 'react';
import SettingsIcon from './icons/SettingsIcon';

interface SettingsViewProps {
  ocrEnabled: boolean;
  setOcrEnabled: (enabled: boolean) => void;
  aiSummarizationEnabled: boolean;
  setAiSummarizationEnabled: (enabled: boolean) => void;
}

const ToggleSwitch: React.FC<{
  enabled: boolean;
  onChange: (enabled: boolean) => void;
}> = ({ enabled, onChange }) => {
  return (
    <button
      type="button"
      className={`${
        enabled ? 'bg-indigo-600' : 'bg-gray-600'
      } relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-900`}
      role="switch"
      aria-checked={enabled}
      onClick={() => onChange(!enabled)}
    >
      <span
        aria-hidden="true"
        className={`${
          enabled ? 'translate-x-5' : 'translate-x-0'
        } pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out`}
      />
    </button>
  );
};

const SettingsView: React.FC<SettingsViewProps> = ({ ocrEnabled, setOcrEnabled, aiSummarizationEnabled, setAiSummarizationEnabled }) => {
  return (
    <div className="flex flex-col h-full p-4 space-y-4 text-gray-200">
      <div className="flex-shrink-0 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <SettingsIcon className="w-8 h-8 text-indigo-400" />
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">Settings</h1>
            <p className="text-xs text-gray-400">Configure application behavior</p>
          </div>
        </div>
      </div>
      <div className="flex-grow bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="max-w-md space-y-8">
            <div>
              <h2 className="text-lg font-semibold text-white mb-4 border-b border-gray-700 pb-2">PDF Processing</h2>
              <div className="flex items-center justify-between">
                  <div>
                      <label htmlFor="ocr-toggle" className="font-medium text-gray-300">Enable OCR</label>
                      <p className="text-sm text-gray-400 mt-1">
                          Use Optical Character Recognition for scanned documents. May increase processing time.
                      </p>
                  </div>
                  <ToggleSwitch enabled={ocrEnabled} onChange={setOcrEnabled} />
              </div>
            </div>

            <div>
              <h2 className="text-lg font-semibold text-white mb-4 border-b border-gray-700 pb-2">AI Features</h2>
              <div className="flex items-center justify-between">
                <div>
                  <label htmlFor="ai-summary-toggle" className="font-medium text-gray-300">AI Summarization</label>
                  <p className="text-sm text-gray-400 mt-1">
                    Use AI to analyze content structure and Rewrite it for better readability and coherence.
                  </p>
                </div>
                <ToggleSwitch enabled={aiSummarizationEnabled} onChange={setAiSummarizationEnabled} />
              </div>
            </div>
          </div>
      </div>
    </div>
  );
};

export default SettingsView;