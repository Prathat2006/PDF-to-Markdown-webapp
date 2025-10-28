
import React from 'react';

interface PdfViewerProps {
  url: string;
}

const PdfViewer: React.FC<PdfViewerProps> = ({ url }) => {
  return (
    <div className="w-full h-full">
      <embed src={url} type="application/pdf" className="w-full h-full" />
    </div>
  );
};

export default PdfViewer;
