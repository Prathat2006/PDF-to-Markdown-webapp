
import React, { useEffect, useRef } from 'react';

declare global {
  interface Window {
    marked: {
      parse: (markdown: string, options?: object) => string;
    };
    DOMPurify: {
      sanitize: (html: string) => string;
    };
    renderMathInElement?: (element: HTMLElement, options: object) => void;
  }
}

interface MarkdownRendererProps {
  content: string | null;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (content && containerRef.current) {
      const element = containerRef.current;
      
      const parsedHtml = window.marked.parse(content, { 
        gfm: true, 
        breaks: true,
        mangle: false,
        headerIds: false,
      });
      const sanitizedHtml = window.DOMPurify.sanitize(parsedHtml);
      element.innerHTML = sanitizedHtml;

      const renderMath = () => {
        if (window.renderMathInElement) {
          try {
            window.renderMathInElement(element, {
              delimiters: [
                { left: '$$', right: '$$', display: true },
                { left: '\\[', right: '\\]', display: true },
                { left: '$', right: '$', display: false },
                { left: '\\(', right: '\\)', display: false },
              ],
              throwOnError: false
            });
          } catch (error) {
            console.error('KaTeX rendering error:', error);
          }
        }
      };

      if (window.renderMathInElement) {
        renderMath();
      } else {
        const script = document.querySelector('script[src*="auto-render.min.js"]');
        if (script) {
          const handleScriptLoad = () => {
            renderMath();
            script.removeEventListener('load', handleScriptLoad);
          };
          if (script.getAttribute('data-loaded')) {
            renderMath();
          } else {
            script.addEventListener('load', handleScriptLoad);
          }
        }
      }
    } else if (containerRef.current) {
        // Clear the container if content is null or empty
        containerRef.current.innerHTML = '';
    }
  }, [content]);
  
  return (
<div
  ref={containerRef}
  className="prose prose-invert max-w-none p-6 prose-pre:bg-gray-900/50 prose-pre:border prose-pre:border-gray-700 prose-img:rounded-md prose-img:shadow-md overflow-y-auto h-[80vh] rounded-lg"
></div>
  );
};

export default MarkdownRenderer;
