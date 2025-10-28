
import { HistoryItem, HistoryFile } from './types';

const API_BASE_URL = 'http://127.0.0.1:9898';

export const processPdf = async (file: File, ocr: boolean, useAi: boolean): Promise<string> => {
  const formData = new FormData();
  formData.append('file', file, file.name);
  formData.append('ocr', String(ocr));

  const endpoint = useAi ? '/convert' : '/convert_raw';
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error('API Error Response:', errorBody);
      throw new Error(`Failed to process PDF. Server responded with ${response.status}: ${response.statusText}`);
    }

    const blob = await response.blob();
    return await blob.text();
  } catch (error) {
    console.error(`An error occurred while calling the ${endpoint} API:`, error);
    throw error;
  }
};

export const convertMdToDocx = async (markdown: string): Promise<Blob> => {
  const markdownBlob = new Blob([markdown], { type: 'text/markdown' });
  const markdownFile = new File([markdownBlob], 'document.md', { type: 'text/markdown' });
  const formData = new FormData();
  formData.append('file', markdownFile);

  try {
    const response = await fetch(`${API_BASE_URL}/convert_md_to_docx`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error('DOCX Conversion API Error Response:', errorBody);
      throw new Error(`Failed to convert to DOCX. Server responded with ${response.status}: ${response.statusText}`);
    }

    return await response.blob();
  } catch (error) {
    console.error('An error occurred while calling the DOCX conversion API:', error);
    throw error;
  }
};

export const getHistory = async (): Promise<HistoryItem[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/history`);
    if (!response.ok) {
      throw new Error(`Failed to fetch history. Server responded with ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('An error occurred while fetching history:', error);
    throw error;
  }
};

export const getHistoryFile = async (filename: string): Promise<HistoryFile> => {
  try {
    const response = await fetch(`${API_BASE_URL}/get_file?filename=${encodeURIComponent(filename)}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch history file. Server responded with ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`An error occurred while fetching file with filename ${filename}:`, error);
    throw error;
  }
};