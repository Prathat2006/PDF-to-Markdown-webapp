
import React from 'react';

const NotebookIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg
    {...props}
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M2 6h4" />
    <path d="M2 12h4" />
    <path d="M2 18h4" />
    <path d="M4 2v20" />
    <path d="M6 4h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6" />
  </svg>
);

export default NotebookIcon;
