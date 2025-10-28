
import React, { useState, useEffect } from 'react';
import SidebarNav from './components/SidebarNav';
import ConversionView from './components/ConversionView';
import NotesView from './components/NotesView';
import SettingsView from './components/SettingsView';
import HistoryView from './components/HistoryView';
import { getHistoryFile } from './services/apiService';
import { HistoryFile } from './types';

const App: React.FC = () => {
  const [activeView, setActiveView] = useState<'conversion' | 'notes' | 'settings' | 'history'>('conversion');
  const [ocrEnabled, setOcrEnabled] = useState<boolean>(false);
  const [aiSummarizationEnabled, setAiSummarizationEnabled] = useState<boolean>(true); // Default to ON
  const [loadedHistoryItem, setLoadedHistoryItem] = useState<{pdfUrl: string; markdown: string; filename: string} | null>(null);
  const [historyPdfBlobUrl, setHistoryPdfBlobUrl] = useState<string | null>(null);

  useEffect(() => {
    // Cleanup function to revoke the object URL when the component unmounts
    // or when the URL changes, preventing memory leaks.
    return () => {
      if (historyPdfBlobUrl) {
        URL.revokeObjectURL(historyPdfBlobUrl);
      }
    };
  }, [historyPdfBlobUrl]);

  const handleLoadHistoryItem = async (filename: string) => {
    if (historyPdfBlobUrl) {
      URL.revokeObjectURL(historyPdfBlobUrl);
    }
    
    try {
      const fileData: HistoryFile = await getHistoryFile(filename);
      const downloadUrl = `http://127.0.0.1:9898${fileData.pdf_url}`;

      // Fetch the PDF content as a Blob to bypass download-forcing headers
      const pdfResponse = await fetch(downloadUrl);
      if (!pdfResponse.ok) {
        throw new Error(`Failed to fetch PDF file. Status: ${pdfResponse.status}`);
      }
      const pdfBlob = await pdfResponse.blob();

      // Create a local URL for the blob to be displayed in the viewer
      const newBlobUrl = URL.createObjectURL(pdfBlob);
      setHistoryPdfBlobUrl(newBlobUrl);

      setLoadedHistoryItem({
        pdfUrl: newBlobUrl,
        markdown: fileData.markdown_content,
        filename: fileData.filename,
      });
      setActiveView('conversion');
    } catch (error) {
      console.error('Failed to load history item:', error);
      alert('Could not load the selected history item. Please check the console for details.');
    }
  };

  const clearLoadedHistory = () => {
    if (historyPdfBlobUrl) {
      URL.revokeObjectURL(historyPdfBlobUrl);
      setHistoryPdfBlobUrl(null);
    }
    setLoadedHistoryItem(null);
  }

  const renderActiveView = () => {
    switch (activeView) {
      case 'conversion':
        return <ConversionView ocrEnabled={ocrEnabled} aiSummarizationEnabled={aiSummarizationEnabled} loadedItem={loadedHistoryItem} onReset={clearLoadedHistory} />;
      case 'notes':
        return <NotesView />;
      case 'settings':
        return <SettingsView 
                  ocrEnabled={ocrEnabled} 
                  setOcrEnabled={setOcrEnabled} 
                  aiSummarizationEnabled={aiSummarizationEnabled}
                  setAiSummarizationEnabled={setAiSummarizationEnabled}
                />;
      case 'history':
        return <HistoryView onLoadItem={handleLoadHistoryItem} />;
      default:
        return <ConversionView ocrEnabled={ocrEnabled} aiSummarizationEnabled={aiSummarizationEnabled} loadedItem={loadedHistoryItem} onReset={clearLoadedHistory} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-200 font-sans antialiased">
      <SidebarNav activeView={activeView} setActiveView={setActiveView} />
      <div className="flex-1 flex flex-col overflow-hidden">
        {renderActiveView()}
      </div>
    </div>
  );
};

export default App;