
import React, { useState, useCallback, useEffect } from 'react';
import Header from './Header';
import FileUpload from './FileUpload';
import PdfViewer from './PdfViewer';
import MarkdownPreview from './MarkdownPreview';
import ProcessingModal from './ProcessingModal';
import { processPdf } from '../services/apiService';
import { ProcessingStep, ProcessingStatus } from '../types';
import { INITIAL_PROCESSING_STEPS } from '../constants';

interface ConversionViewProps {
  ocrEnabled: boolean;
  aiSummarizationEnabled: boolean;
  loadedItem: { pdfUrl: string; markdown: string; filename: string } | null;
  onReset: () => void;
}

const ConversionView: React.FC<ConversionViewProps> = ({ ocrEnabled, aiSummarizationEnabled, loadedItem, onReset }) => {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [uploadedPdfUrl, setUploadedPdfUrl] = useState<string | null>(null);
  const [markdownContent, setMarkdownContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>(INITIAL_PROCESSING_STEPS);

  // Derived state to decide what to display
  const displayPdfUrl = loadedItem?.pdfUrl || uploadedPdfUrl;
  const displayMarkdown = loadedItem?.markdown ?? markdownContent;
  const displayFilename = loadedItem?.filename || pdfFile?.name;

  useEffect(() => {
    // If a history item is loaded from props, we clear any local state related to a new file upload.
    if (loadedItem) {
      if (uploadedPdfUrl) URL.revokeObjectURL(uploadedPdfUrl);
      setPdfFile(null);
      setUploadedPdfUrl(null);
      setMarkdownContent(null);
      setError(null);
      setIsLoading(false);
      setProcessingSteps(INITIAL_PROCESSING_STEPS);
    }
  }, [loadedItem, uploadedPdfUrl]);

  const handleFileSelect = useCallback((file: File) => {
    // When a new file is selected, clear any loaded history item from the parent.
    onReset();
    setPdfFile(file);
    const url = URL.createObjectURL(file);
    setUploadedPdfUrl(url);
    setMarkdownContent(null);
    setError(null);
    setProcessingSteps(INITIAL_PROCESSING_STEPS);
  }, [onReset]);

  const handleProcessClick = useCallback(async () => {
    if (!pdfFile) return;

    setIsLoading(true);
    setError(null);
    setMarkdownContent(null);
    setProcessingSteps(INITIAL_PROCESSING_STEPS);

    const updateProgress = (stepIndex: number) => {
      setProcessingSteps(prevSteps =>
        prevSteps.map((step, index) => {
          if (index < stepIndex) return { ...step, status: ProcessingStatus.DONE };
          if (index === stepIndex) return { ...step, status: ProcessingStatus.IN_PROGRESS };
          return { ...step, status: ProcessingStatus.PENDING };
        })
      );
    };

    const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

    try {
      updateProgress(0); await sleep(300);
      updateProgress(1); await sleep(400);
      updateProgress(2); await sleep(300);
      updateProgress(3);
      const markdown = await processPdf(pdfFile, ocrEnabled, aiSummarizationEnabled);
      updateProgress(4); await sleep(300);
      updateProgress(5); await sleep(200);

      setMarkdownContent(markdown);
      setProcessingSteps(prevSteps => prevSteps.map(step => ({...step, status: ProcessingStatus.DONE})));
    } catch (err) {
      setError('An error occurred during processing. Please try again.');
      setProcessingSteps(INITIAL_PROCESSING_STEPS);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [pdfFile, ocrEnabled, aiSummarizationEnabled]);

  const handleReset = useCallback(() => {
    if (uploadedPdfUrl) {
      URL.revokeObjectURL(uploadedPdfUrl);
    }
    setPdfFile(null);
    setUploadedPdfUrl(null);
    setMarkdownContent(null);
    setIsLoading(false);
    setError(null);
    setProcessingSteps(INITIAL_PROCESSING_STEPS);
    onReset(); // Clear loaded history item in parent
  }, [uploadedPdfUrl, onReset]);

  return (
    <div className="flex flex-col h-full bg-gray-900 text-gray-200">
      <Header onReset={handleReset} showReset={!!displayPdfUrl} />
      {isLoading && <ProcessingModal steps={processingSteps} />}
      <main className="flex-grow p-4 overflow-hidden">
          {!displayPdfUrl ? (
            <div className="h-full flex items-center justify-center">
              <FileUpload onFileSelect={handleFileSelect} />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
              <div className="flex flex-col h-full bg-gray-800 rounded-lg shadow-lg">
                <div className="flex-shrink-0 p-3 bg-gray-700/50 rounded-t-lg flex justify-between items-center">
                  <h2 className="text-lg font-semibold text-gray-300 truncate" title={displayFilename}>{displayFilename || 'Original PDF'}</h2>
                  {/* Only show Process button for new uploads that haven't been processed */}
                  {pdfFile && !displayMarkdown && (
                    <button
                      onClick={handleProcessClick}
                      disabled={isLoading}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-indigo-500"
                    >
                      Process Document
                    </button>
                  )}
                </div>
                <div className="flex-grow overflow-auto">
                  {displayPdfUrl && <PdfViewer url={displayPdfUrl} />}
                </div>
              </div>
              <div className="flex flex-col h-full bg-gray-800 rounded-lg shadow-lg">
                 <div className="flex-shrink-0 p-3 bg-gray-700/50 rounded-t-lg">
                    <h2 className="text-lg font-semibold text-gray-300">Extracted Markdown</h2>
                 </div>
                <div className="flex-grow overflow-auto">
                  <MarkdownPreview content={displayMarkdown} />
                </div>
              </div>
            </div>
          )}
          {error && <p className="text-red-500 text-center mt-4">{error}</p>}
        </main>
    </div>
  );
};

export default ConversionView;