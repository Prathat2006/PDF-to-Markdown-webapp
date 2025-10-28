
export enum ProcessingStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  DONE = 'DONE',
}

export interface ProcessingStep {
  name: string;
  status: ProcessingStatus;
  isAiStep?: boolean;
}

export interface HistoryItem {
  session_id: string;
  timestamp: string;
  input_pdf: string;
  output_md: string;
  filename: string;
  ocr: boolean;
}

export interface HistoryFile {
    filename: string;
    markdown_content: string;
    pdf_url: string;
}
