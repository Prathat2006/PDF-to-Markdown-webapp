
import { ProcessingStep, ProcessingStatus } from './types';

export const INITIAL_PROCESSING_STEPS: ProcessingStep[] = [
  { name: 'Parsing PDF structure', status: ProcessingStatus.PENDING },
  { name: 'Extracting text and tables', status: ProcessingStatus.PENDING },
  { name: 'Identifying mathematical formulas', status: ProcessingStatus.PENDING },
  { name: 'Analyzing images with Gemini AI', status: ProcessingStatus.PENDING, isAiStep: true },
  { name: 'Converting formulas to LaTeX', status: ProcessingStatus.PENDING },
  { name: 'Generating final Markdown', status: ProcessingStatus.PENDING },
];
